"""Context retrieval engine with tiered approach and token budgeting."""

import re
from typing import Any

from lattice_context.core.types import Convention, Correction, DataTool, Decision
from lattice_context.storage.database import Database


class ContextRetriever:
    """Retrieve relevant context with tiered approach and token budgeting."""

    def __init__(self, db: Database):
        self.db = db

    async def get_context(
        self,
        task: str,
        max_tokens: int = 8000,
    ) -> dict[str, Any]:
        """Get context for a task using tiered retrieval."""

        # Extract entities mentioned in the task
        entities = self._extract_entities(task)

        # Tier 1: Immediate - Directly mentioned entities
        immediate_decisions = []
        for entity in entities:
            decisions = self.db.get_decisions_for_entity(entity, limit=5)
            immediate_decisions.extend(decisions)

        # If no immediate results, try fuzzy search
        if not immediate_decisions and entities:
            for entity in entities[:3]:  # Try first 3 entities
                # Search decisions by partial match
                search_results = self.db.search_decisions(entity, limit=3)
                immediate_decisions.extend(search_results)

        # Get corrections (highest priority)
        corrections = []
        for entity in entities:
            entity_corrections = self.db.get_corrections(entity)
            corrections.extend(entity_corrections)

        # Get global corrections
        global_corrections = self.db.get_corrections()
        corrections.extend([c for c in global_corrections if c.scope.value == "global"])

        # Deduplicate corrections
        seen_ids = set()
        unique_corrections = []
        for corr in corrections:
            if corr.id not in seen_ids:
                unique_corrections.append(corr)
                seen_ids.add(corr.id)

        # Tier 2: Related - Search for related decisions
        related_decisions = []
        if entities:
            # Use first entity as search query
            search_query = entities[0]
            related = self.db.search_decisions(search_query, limit=10)
            # Exclude immediate decisions
            immediate_ids = {d.id for d in immediate_decisions}
            related_decisions = [d for d in related if d.id not in immediate_ids]

        # Tier 3: Global - Get conventions
        conventions = self.db.get_conventions(tool=DataTool.DBT)

        # Rank and prioritize within token budget
        response = {
            "immediate_decisions": self._rank_decisions(immediate_decisions[:5]),
            "related_decisions": self._rank_decisions(related_decisions[:5]),
            "corrections": self._rank_corrections(unique_corrections[:5]),
            "conventions": self._rank_conventions(conventions[:5]),
        }

        return response

    def _extract_entities(self, task: str) -> list[str]:
        """Extract entity names from task description."""
        entities = []

        # Look for quoted entities
        quoted = re.findall(r'["`\'](\w+)["`\']', task)
        entities.extend(quoted)

        # Look for common dbt patterns (exact matches)
        patterns = [
            r"\b(dim_\w+)\b",
            r"\b(fct_\w+)\b",
            r"\b(stg_\w+)\b",
            r"\b(int_\w+)\b",
            r"\b(rpt_\w+)\b",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, task, re.IGNORECASE)
            entities.extend(matches)

        # Extract from common query patterns
        # "add X to Y" or "add X column to Y"
        add_patterns = [
            r"add\s+(?:a\s+)?(\w+)\s+(?:column\s+)?to\s+(\w+)",
            r"create\s+(?:a\s+)?(\w+)\s+(?:column\s+)?in\s+(\w+)",
        ]
        for pattern in add_patterns:
            matches = re.findall(pattern, task, re.IGNORECASE)
            for match in matches:
                # Add both the column and model name
                entities.extend(match)

        # Look for words that might be model/column names
        # Typically lowercase with underscores
        words = re.findall(r"\b([a-z_]+)\b", task.lower())
        for word in words:
            if "_" in word and len(word) > 3:  # Likely a model/column name
                entities.append(word)
            elif len(word) > 4:  # Could be a partial name
                # Add with suffix patterns for fuzzy matching
                potential_entities = [
                    f"{word}_id",
                    f"{word}_key",
                    f"{word}_at",
                    f"{word}_amount",
                    f"{word}_date",
                ]
                entities.extend(potential_entities)

        # Deduplicate while preserving order
        seen = set()
        unique_entities = []
        for entity in entities:
            if entity not in seen:
                unique_entities.append(entity)
                seen.add(entity)

        return unique_entities

    def _rank_decisions(self, decisions: list[Decision]) -> list[Decision]:
        """Rank decisions by relevance."""
        # Sort by confidence and recency
        return sorted(
            decisions,
            key=lambda d: (d.confidence, d.timestamp),
            reverse=True
        )

    def _rank_corrections(self, corrections: list[Correction]) -> list[Correction]:
        """Rank corrections by priority."""
        priority_order = {"high": 3, "medium": 2, "low": 1}
        return sorted(
            corrections,
            key=lambda c: (priority_order.get(c.priority.value, 0), c.added_at),
            reverse=True
        )

    def _rank_conventions(self, conventions: list[Convention]) -> list[Convention]:
        """Rank conventions by confidence and frequency."""
        return sorted(
            conventions,
            key=lambda c: (c.confidence, c.frequency),
            reverse=True
        )
