"""SQLite database management for Lattice."""

import sqlite3
from datetime import datetime
from pathlib import Path

from lattice_context.core.types import (
    ChangeType,
    Convention,
    ConventionType,
    Correction,
    CorrectionPriority,
    CorrectionScope,
    DataTool,
    Decision,
    DecisionSource,
    EntityType,
)

# Register datetime adapters for Python 3.12+ compatibility
sqlite3.register_adapter(datetime, lambda dt: dt.isoformat())
sqlite3.register_converter("timestamp", lambda b: datetime.fromisoformat(b.decode()))


class Database:
    """SQLite database for storing Lattice data."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn: sqlite3.Connection | None = None

    def connect(self) -> sqlite3.Connection:
        """Get database connection."""
        if self.conn is None:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row
            # Enable WAL mode for better concurrency
            self.conn.execute("PRAGMA journal_mode=WAL")
        return self.conn

    def initialize(self) -> None:
        """Initialize database schema."""
        conn = self.connect()

        # Entities table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                tool TEXT NOT NULL,
                path TEXT,
                metadata TEXT,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL
            )
        """)

        # Decisions table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                id TEXT PRIMARY KEY,
                entity TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                change_type TEXT NOT NULL,
                why TEXT NOT NULL,
                context TEXT,
                source TEXT NOT NULL,
                source_ref TEXT NOT NULL,
                author TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                confidence REAL NOT NULL,
                tags TEXT,
                tool TEXT NOT NULL
            )
        """)

        # Conventions table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conventions (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                pattern TEXT NOT NULL,
                applies_to TEXT NOT NULL,
                examples TEXT NOT NULL,
                frequency INTEGER NOT NULL,
                confidence REAL NOT NULL,
                detected_at TIMESTAMP NOT NULL,
                tool TEXT NOT NULL
            )
        """)

        # Corrections table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS corrections (
                id TEXT PRIMARY KEY,
                entity TEXT NOT NULL,
                entity_type TEXT,
                correction TEXT NOT NULL,
                context TEXT,
                added_by TEXT NOT NULL,
                added_at TIMESTAMP NOT NULL,
                scope TEXT NOT NULL,
                priority TEXT NOT NULL
            )
        """)

        # Create FTS5 virtual tables for full-text search
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS decisions_fts USING fts5(
                entity, why, context, tags, content='decisions', content_rowid='rowid'
            )
        """)

        # Create indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_decisions_entity ON decisions(entity)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_decisions_tool ON decisions(tool)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_decisions_timestamp ON decisions(timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_conventions_tool ON conventions(tool)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_corrections_entity ON corrections(entity)")

        # Metadata table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP NOT NULL
            )
        """)

        conn.commit()

    def is_indexed(self) -> bool:
        """Check if project has been indexed."""
        conn = self.connect()
        cursor = conn.execute("SELECT value FROM metadata WHERE key = 'last_indexed_at'")
        row = cursor.fetchone()
        return row is not None

    def last_indexed_at(self) -> datetime | None:
        """Get last indexed timestamp."""
        conn = self.connect()
        cursor = conn.execute("SELECT value FROM metadata WHERE key = 'last_indexed_at'")
        row = cursor.fetchone()
        if row:
            return datetime.fromisoformat(row[0])
        return None

    def set_last_indexed_at(self, timestamp: datetime) -> None:
        """Set last indexed timestamp."""
        conn = self.connect()
        conn.execute(
            "INSERT OR REPLACE INTO metadata (key, value, updated_at) VALUES (?, ?, ?)",
            ("last_indexed_at", timestamp.isoformat(), datetime.now())
        )
        conn.commit()

    def count_entities(self) -> int:
        """Count entities."""
        conn = self.connect()
        cursor = conn.execute("SELECT COUNT(*) FROM entities")
        return cursor.fetchone()[0]

    def count_decisions(self) -> int:
        """Count decisions."""
        conn = self.connect()
        cursor = conn.execute("SELECT COUNT(*) FROM decisions")
        return cursor.fetchone()[0]

    def count_conventions(self) -> int:
        """Count conventions."""
        conn = self.connect()
        cursor = conn.execute("SELECT COUNT(*) FROM conventions")
        return cursor.fetchone()[0]

    def count_corrections(self) -> int:
        """Count corrections."""
        conn = self.connect()
        cursor = conn.execute("SELECT COUNT(*) FROM corrections")
        return cursor.fetchone()[0]

    def add_decision(self, decision: Decision) -> None:
        """Add a decision."""
        conn = self.connect()

        # Insert into main table
        conn.execute(
            """
            INSERT OR REPLACE INTO decisions
            (id, entity, entity_type, change_type, why, context, source, source_ref,
             author, timestamp, confidence, tags, tool)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                decision.id,
                decision.entity,
                decision.entity_type.value,
                decision.change_type.value,
                decision.why,
                decision.context,
                decision.source.value,
                decision.source_ref,
                decision.author,
                decision.timestamp,
                decision.confidence,
                ",".join(decision.tags),
                decision.tool.value,
            )
        )

        # Update FTS5 index
        conn.execute(
            """
            INSERT OR REPLACE INTO decisions_fts (rowid, entity, why, context, tags)
            SELECT rowid, entity, why, context, tags FROM decisions WHERE id = ?
            """,
            (decision.id,)
        )

        conn.commit()

    def get_decisions_for_entity(self, entity: str, limit: int = 10) -> list[Decision]:
        """Get decisions for an entity."""
        conn = self.connect()
        cursor = conn.execute(
            """
            SELECT * FROM decisions
            WHERE entity = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (entity, limit)
        )

        decisions = []
        for row in cursor.fetchall():
            decisions.append(
                Decision(
                    id=row["id"],
                    entity=row["entity"],
                    entity_type=EntityType(row["entity_type"]),
                    change_type=ChangeType(row["change_type"]),
                    why=row["why"],
                    context=row["context"] or "",
                    source=DecisionSource(row["source"]),
                    source_ref=row["source_ref"],
                    author=row["author"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    confidence=row["confidence"],
                    tags=row["tags"].split(",") if row["tags"] else [],
                    tool=DataTool(row["tool"]),
                )
            )
        return decisions

    def list_decisions(self, limit: int = 100) -> list[Decision]:
        """List all decisions."""
        conn = self.connect()
        cursor = conn.execute(
            """
            SELECT * FROM decisions
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,)
        )

        decisions = []
        for row in cursor.fetchall():
            decisions.append(
                Decision(
                    id=row["id"],
                    entity=row["entity"],
                    entity_type=EntityType(row["entity_type"]),
                    change_type=ChangeType(row["change_type"]),
                    why=row["why"],
                    context=row["context"] or "",
                    source=DecisionSource(row["source"]),
                    source_ref=row["source_ref"],
                    author=row["author"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    confidence=row["confidence"],
                    tags=row["tags"].split(",") if row["tags"] else [],
                    tool=DataTool(row["tool"]),
                )
            )
        return decisions

    def search_decisions(self, query: str, limit: int = 20) -> list[Decision]:
        """Search decisions using FTS5."""
        # Sanitize query for FTS5 - remove special characters that cause syntax errors
        # FTS5 special chars: " * ( ) : -
        sanitized_query = query.replace('"', '').replace('*', '').replace('(', '').replace(')', '').replace(':', '').replace('?', '')

        # If query is empty after sanitization, return empty list
        if not sanitized_query.strip():
            return []

        conn = self.connect()
        cursor = conn.execute(
            """
            SELECT d.* FROM decisions d
            JOIN decisions_fts ON decisions_fts.rowid = d.rowid
            WHERE decisions_fts MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (sanitized_query, limit)
        )

        decisions = []
        for row in cursor.fetchall():
            decisions.append(
                Decision(
                    id=row["id"],
                    entity=row["entity"],
                    entity_type=EntityType(row["entity_type"]),
                    change_type=ChangeType(row["change_type"]),
                    why=row["why"],
                    context=row["context"] or "",
                    source=DecisionSource(row["source"]),
                    source_ref=row["source_ref"],
                    author=row["author"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    confidence=row["confidence"],
                    tags=row["tags"].split(",") if row["tags"] else [],
                    tool=DataTool(row["tool"]),
                )
            )
        return decisions

    def add_convention(self, convention: Convention) -> None:
        """Add a convention."""
        conn = self.connect()
        conn.execute(
            """
            INSERT OR REPLACE INTO conventions
            (id, type, pattern, applies_to, examples, frequency, confidence, detected_at, tool)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                convention.id,
                convention.type.value,
                convention.pattern,
                ",".join(e.value for e in convention.applies_to),
                ",".join(convention.examples),
                convention.frequency,
                convention.confidence,
                convention.detected_at,
                convention.tool.value,
            )
        )
        conn.commit()

    def get_conventions(self, tool: DataTool | None = None) -> list[Convention]:
        """Get conventions."""
        conn = self.connect()

        if tool:
            cursor = conn.execute(
                "SELECT * FROM conventions WHERE tool = ? ORDER BY confidence DESC",
                (tool.value,)
            )
        else:
            cursor = conn.execute("SELECT * FROM conventions ORDER BY confidence DESC")

        conventions = []
        for row in cursor.fetchall():
            conventions.append(
                Convention(
                    id=row["id"],
                    type=ConventionType(row["type"]),
                    pattern=row["pattern"],
                    applies_to=[EntityType(e) for e in row["applies_to"].split(",")],
                    examples=row["examples"].split(","),
                    frequency=row["frequency"],
                    confidence=row["confidence"],
                    detected_at=datetime.fromisoformat(row["detected_at"]),
                    tool=DataTool(row["tool"]),
                )
            )
        return conventions

    def add_correction(self, correction: Correction) -> None:
        """Add a correction."""
        conn = self.connect()
        conn.execute(
            """
            INSERT OR REPLACE INTO corrections
            (id, entity, entity_type, correction, context, added_by, added_at, scope, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                correction.id,
                correction.entity,
                correction.entity_type.value if correction.entity_type else None,
                correction.correction,
                correction.context,
                correction.added_by,
                correction.added_at,
                correction.scope.value,
                correction.priority.value,
            )
        )
        conn.commit()

    def get_corrections(self, entity: str | None = None) -> list[Correction]:
        """Get corrections."""
        conn = self.connect()

        if entity:
            cursor = conn.execute(
                """
                SELECT * FROM corrections
                WHERE entity = ? OR scope = 'global'
                ORDER BY priority DESC, added_at DESC
                """,
                (entity,)
            )
        else:
            cursor = conn.execute("SELECT * FROM corrections ORDER BY priority DESC, added_at DESC")

        corrections = []
        for row in cursor.fetchall():
            corrections.append(
                Correction(
                    id=row["id"],
                    entity=row["entity"],
                    entity_type=EntityType(row["entity_type"]) if row["entity_type"] else None,
                    correction=row["correction"],
                    context=row["context"] or "",
                    added_by=row["added_by"],
                    added_at=datetime.fromisoformat(row["added_at"]),
                    scope=CorrectionScope(row["scope"]),
                    priority=CorrectionPriority(row["priority"]),
                )
            )
        return corrections

    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
