"""
GitHub Copilot integration for Lattice Context Layer.

Provides institutional knowledge as context to GitHub Copilot
to improve code suggestions with team conventions and decisions.
"""

import json
from pathlib import Path
from typing import Any

from lattice_context.storage.database import Database


class CopilotContextProvider:
    """Provides Lattice context to GitHub Copilot."""

    def __init__(self, project_root: Path = Path(".")):
        """Initialize context provider.

        Args:
            project_root: Root directory of the project (contains .lattice/)
        """
        self.project_root = project_root
        self.lattice_dir = project_root / ".lattice"
        self.db_path = self.lattice_dir / "index.db"

        if not self.db_path.exists():
            raise FileNotFoundError(
                f"Lattice index not found at {self.db_path}. "
                "Run 'lattice init && lattice index' first."
            )

        self.db = Database(self.db_path)

    def get_context_for_query(self, query: str, max_results: int = 5) -> str:
        """Get relevant context for a Copilot query.

        Args:
            query: The query from Copilot (e.g., file path, code snippet, or question)
            max_results: Maximum number of results to return

        Returns:
            Formatted context string for Copilot
        """
        # Search for relevant decisions
        decisions = self.db.search_decisions(query, limit=max_results)

        if not decisions:
            return ""

        # Format context for Copilot
        context_parts = []
        context_parts.append("# Lattice Context - Institutional Knowledge\n")

        for i, decision in enumerate(decisions, 1):
            context_parts.append(f"## Decision {i}: {decision.entity}")
            context_parts.append(f"**Why**: {decision.why}")

            if decision.context:
                context_parts.append(f"**Context**: {decision.context}")

            context_parts.append(f"**Change**: {decision.change_type.value}")
            context_parts.append(f"**Source**: {decision.source.value}")
            context_parts.append(f"**Author**: {decision.author}")
            context_parts.append("")

        # Add conventions if relevant
        conventions = self.db.get_conventions()
        if conventions:
            context_parts.append("## Team Conventions")
            for conv in conventions[:3]:  # Top 3 conventions
                examples = ", ".join(conv.examples[:3])
                context_parts.append(
                    f"- **{conv.type.value}**: `{conv.pattern}` (examples: {examples})"
                )
            context_parts.append("")

        return "\n".join(context_parts)

    def get_context_for_file(self, file_path: str, max_results: int = 5) -> str:
        """Get context relevant to a specific file.

        Args:
            file_path: Path to the file being edited
            max_results: Maximum number of results to return

        Returns:
            Formatted context string
        """
        # Extract entity name from file path (e.g., models/staging/stg_customers.sql -> stg_customers)
        file_name = Path(file_path).stem

        # Get context for this entity
        return self.get_context_for_query(file_name, max_results=max_results)

    def get_context_for_entity(self, entity_name: str) -> dict[str, Any]:
        """Get all context for a specific entity.

        Args:
            entity_name: Name of the entity (e.g., "stg_customers")

        Returns:
            Dictionary with all context information
        """
        decisions = [
            d
            for d in self.db.list_decisions(limit=1000)
            if entity_name.lower() in d.entity.lower()
        ]

        corrections = [
            c
            for c in self.db.get_corrections()
            if entity_name.lower() in c.entity.lower()
        ]

        return {
            "entity": entity_name,
            "decisions": [
                {
                    "why": d.why,
                    "context": d.context,
                    "change_type": d.change_type.value,
                    "source": d.source.value,
                    "author": d.author,
                    "timestamp": d.timestamp.isoformat(),
                }
                for d in decisions
            ],
            "corrections": [
                {
                    "correction": c.correction,
                    "context": c.context,
                    "added_by": c.added_by,
                    "timestamp": c.added_at.isoformat(),
                }
                for c in corrections
            ],
            "conventions": [
                {
                    "type": c.type.value,
                    "pattern": c.pattern,
                    "examples": c.examples,
                }
                for c in self.db.get_conventions()
            ],
        }

    def format_for_copilot_chat(self, query: str) -> str:
        """Format context for Copilot Chat.

        Args:
            query: The user's question to Copilot Chat

        Returns:
            Formatted context optimized for chat interface
        """
        context = self.get_context_for_query(query, max_results=3)

        if not context:
            return "No relevant institutional knowledge found for this query."

        # Add helpful prefix for chat
        prefix = (
            "Based on your team's institutional knowledge captured by Lattice:\n\n"
        )
        return prefix + context

    def export_all_context(self) -> dict[str, Any]:
        """Export all context as a structured dictionary.

        Returns:
            Complete context data
        """
        return {
            "decisions": [
                {
                    "entity": d.entity,
                    "why": d.why,
                    "context": d.context,
                    "change_type": d.change_type.value,
                    "source": d.source.value,
                    "author": d.author,
                    "timestamp": d.timestamp.isoformat(),
                }
                for d in self.db.list_decisions(limit=10000)
            ],
            "conventions": [
                {
                    "type": c.type.value,
                    "pattern": c.pattern,
                    "examples": c.examples,
                    "confidence": c.confidence,
                }
                for c in self.db.get_conventions()
            ],
            "corrections": [
                {
                    "entity": c.entity,
                    "correction": c.correction,
                    "context": c.context,
                    "added_by": c.added_by,
                    "timestamp": c.added_at.isoformat(),
                }
                for c in self.db.get_corrections()
            ],
        }


def main():
    """CLI for testing Copilot integration."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m lattice_context.integrations.copilot <query>")
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    provider = CopilotContextProvider()
    context = provider.get_context_for_query(query)

    if context:
        print(context)
    else:
        print(f"No context found for: {query}")


if __name__ == "__main__":
    main()
