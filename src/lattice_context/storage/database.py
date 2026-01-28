"""SQLite database management for Lattice."""

from __future__ import annotations

from typing import Optional

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
        self.conn: Optional[sqlite3.Connection] = None

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

        # Team Workspace tables (v0.2.0)
        # Comments on decisions
        conn.execute("""
            CREATE TABLE IF NOT EXISTS decision_comments (
                id TEXT PRIMARY KEY,
                decision_id TEXT NOT NULL,
                author TEXT NOT NULL,
                author_email TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP,
                parent_id TEXT,
                FOREIGN KEY (decision_id) REFERENCES decisions(id) ON DELETE CASCADE,
                FOREIGN KEY (parent_id) REFERENCES decision_comments(id) ON DELETE CASCADE
            )
        """)

        # Votes on decisions
        conn.execute("""
            CREATE TABLE IF NOT EXISTS decision_votes (
                decision_id TEXT NOT NULL,
                user_email TEXT NOT NULL,
                vote INTEGER NOT NULL,
                created_at TIMESTAMP NOT NULL,
                PRIMARY KEY (decision_id, user_email),
                FOREIGN KEY (decision_id) REFERENCES decisions(id) ON DELETE CASCADE
            )
        """)

        # Decision metadata (status, verification)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS decision_metadata (
                decision_id TEXT PRIMARY KEY,
                status TEXT NOT NULL DEFAULT 'active',
                last_verified_at TIMESTAMP,
                last_verified_by TEXT,
                vote_score INTEGER DEFAULT 0,
                FOREIGN KEY (decision_id) REFERENCES decisions(id) ON DELETE CASCADE
            )
        """)

        # Create indexes for team features
        conn.execute("CREATE INDEX IF NOT EXISTS idx_comments_decision ON decision_comments(decision_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_comments_author ON decision_comments(author_email)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_votes_decision ON decision_votes(decision_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_metadata_status ON decision_metadata(status)")

        conn.commit()

    def is_indexed(self) -> bool:
        """Check if project has been indexed."""
        conn = self.connect()
        cursor = conn.execute("SELECT value FROM metadata WHERE key = 'last_indexed_at'")
        row = cursor.fetchone()
        return row is not None

    def last_indexed_at(self) -> Optional[datetime]:
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

    def get_conventions(self, tool: Optional[DataTool] = None) -> list[Convention]:
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

    def get_corrections(self, entity: Optional[str] = None) -> list[Correction]:
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

    # Team Workspace methods (v0.2.0)

    def add_comment(
        self,
        decision_id: str,
        author: str,
        author_email: str,
        content: str,
        parent_id: Optional[str] = None
    ) -> str:
        """Add a comment to a decision."""
        import uuid

        comment_id = f"cmt_{uuid.uuid4().hex[:12]}"
        conn = self.connect()

        conn.execute(
            """
            INSERT INTO decision_comments
            (id, decision_id, author, author_email, content, created_at, parent_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (comment_id, decision_id, author, author_email, content, datetime.now(), parent_id)
        )
        conn.commit()
        return comment_id

    def get_comments(self, decision_id: str) -> list[dict]:
        """Get all comments for a decision."""
        conn = self.connect()
        cursor = conn.execute(
            """
            SELECT * FROM decision_comments
            WHERE decision_id = ?
            ORDER BY created_at ASC
            """,
            (decision_id,)
        )

        comments = []
        for row in cursor.fetchall():
            comments.append({
                "id": row["id"],
                "decision_id": row["decision_id"],
                "author": row["author"],
                "author_email": row["author_email"],
                "content": row["content"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "parent_id": row["parent_id"]
            })
        return comments

    def vote_decision(self, decision_id: str, user_email: str, vote: int) -> None:
        """Vote on a decision. Vote: 1 for upvote, -1 for downvote, 0 to remove."""
        conn = self.connect()

        if vote == 0:
            # Remove vote
            conn.execute(
                "DELETE FROM decision_votes WHERE decision_id = ? AND user_email = ?",
                (decision_id, user_email)
            )
        else:
            # Add or update vote
            conn.execute(
                """
                INSERT INTO decision_votes (decision_id, user_email, vote, created_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(decision_id, user_email)
                DO UPDATE SET vote = excluded.vote
                """,
                (decision_id, user_email, vote, datetime.now())
            )

        # Update vote score in metadata
        cursor = conn.execute(
            "SELECT SUM(vote) as score FROM decision_votes WHERE decision_id = ?",
            (decision_id,)
        )
        score = cursor.fetchone()["score"] or 0

        conn.execute(
            """
            INSERT INTO decision_metadata (decision_id, vote_score)
            VALUES (?, ?)
            ON CONFLICT(decision_id)
            DO UPDATE SET vote_score = excluded.vote_score
            """,
            (decision_id, score)
        )

        conn.commit()

    def get_vote_score(self, decision_id: str) -> int:
        """Get vote score for a decision."""
        conn = self.connect()
        cursor = conn.execute(
            "SELECT vote_score FROM decision_metadata WHERE decision_id = ?",
            (decision_id,)
        )
        row = cursor.fetchone()
        return row["vote_score"] if row else 0

    def get_user_vote(self, decision_id: str, user_email: str) -> int:
        """Get user's vote on a decision. Returns 1, -1, or 0."""
        conn = self.connect()
        cursor = conn.execute(
            "SELECT vote FROM decision_votes WHERE decision_id = ? AND user_email = ?",
            (decision_id, user_email)
        )
        row = cursor.fetchone()
        return row["vote"] if row else 0

    def verify_decision(self, decision_id: str, user_email: str) -> None:
        """Mark a decision as verified by a user."""
        conn = self.connect()
        conn.execute(
            """
            INSERT INTO decision_metadata (decision_id, status, last_verified_at, last_verified_by)
            VALUES (?, 'verified', ?, ?)
            ON CONFLICT(decision_id)
            DO UPDATE SET
                status = 'verified',
                last_verified_at = excluded.last_verified_at,
                last_verified_by = excluded.last_verified_by
            """,
            (decision_id, datetime.now(), user_email)
        )
        conn.commit()

    def mark_outdated(self, decision_id: str) -> None:
        """Mark a decision as outdated."""
        conn = self.connect()
        conn.execute(
            """
            INSERT INTO decision_metadata (decision_id, status)
            VALUES (?, 'outdated')
            ON CONFLICT(decision_id)
            DO UPDATE SET status = 'outdated'
            """,
            (decision_id,)
        )
        conn.commit()

    def get_decision_metadata(self, decision_id: str) -> Optional[dict]:
        """Get metadata for a decision."""
        conn = self.connect()
        cursor = conn.execute(
            "SELECT * FROM decision_metadata WHERE decision_id = ?",
            (decision_id,)
        )
        row = cursor.fetchone()
        if row:
            return {
                "decision_id": row["decision_id"],
                "status": row["status"],
                "last_verified_at": row["last_verified_at"],
                "last_verified_by": row["last_verified_by"],
                "vote_score": row["vote_score"]
            }
        return None

    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
