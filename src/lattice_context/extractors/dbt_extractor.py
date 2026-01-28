"""Extract context from dbt projects."""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from lattice_context.core.types import (
    ChangeType,
    Convention,
    ConventionType,
    DataTool,
    Decision,
    DecisionSource,
    EntityType,
)


class DbtExtractor:
    """Extract entities, decisions, and conventions from dbt projects."""

    def __init__(self, manifest_path: Path):
        self.manifest_path = manifest_path
        self.manifest: dict[str, Any] = {}

    def load_manifest(self) -> None:
        """Load dbt manifest.json."""
        with open(self.manifest_path) as f:
            self.manifest = json.load(f)

    def extract_entities(self) -> list[dict[str, Any]]:
        """Extract entities from manifest."""
        entities = []

        # Extract models
        for node_id, node in self.manifest.get("nodes", {}).items():
            if node.get("resource_type") == "model":
                entity_id = hashlib.sha256(node_id.encode()).hexdigest()[:12]
                entities.append({
                    "id": f"ent_{entity_id}",
                    "name": node.get("name"),
                    "type": EntityType.MODEL.value,
                    "tool": DataTool.DBT.value,
                    "path": node.get("original_file_path"),
                    "metadata": json.dumps({
                        "schema": node.get("schema"),
                        "database": node.get("database"),
                        "description": node.get("description", ""),
                    }),
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                })

                # Extract columns for this model
                for col_name, col_data in node.get("columns", {}).items():
                    col_id = hashlib.sha256(f"{node_id}:{col_name}".encode()).hexdigest()[:12]
                    entities.append({
                        "id": f"ent_{col_id}",
                        "name": col_name,
                        "type": EntityType.COLUMN.value,
                        "tool": DataTool.DBT.value,
                        "path": node.get("original_file_path"),
                        "metadata": json.dumps({
                            "model": node.get("name"),
                            "description": col_data.get("description", ""),
                            "data_type": col_data.get("data_type", ""),
                        }),
                        "created_at": datetime.now(),
                        "updated_at": datetime.now(),
                    })

        return entities

    def detect_conventions(self) -> list[Convention]:
        """Detect naming conventions from entities."""
        conventions = []
        model_names: list[str] = []
        column_names: list[str] = []

        # Collect names
        for node_id, node in self.manifest.get("nodes", {}).items():
            if node.get("resource_type") == "model":
                model_names.append(node.get("name"))
                for col_name in node.get("columns", {}).keys():
                    column_names.append(col_name)

        # Detect prefixes for models
        model_conventions = self._detect_prefix_patterns(model_names, EntityType.MODEL)
        conventions.extend(model_conventions)

        # Detect suffixes for columns
        column_conventions = self._detect_suffix_patterns(column_names, EntityType.COLUMN)
        conventions.extend(column_conventions)

        return conventions

    def _detect_prefix_patterns(self, names: list[str], entity_type: EntityType) -> list[Convention]:
        """Detect prefix patterns."""
        conventions = []
        prefix_counts: dict[str, list[str]] = {}

        # Common dbt prefixes
        common_prefixes = ["dim_", "fct_", "stg_", "int_", "rpt_"]

        for name in names:
            for prefix in common_prefixes:
                if name.startswith(prefix):
                    if prefix not in prefix_counts:
                        prefix_counts[prefix] = []
                    prefix_counts[prefix].append(name)

        # Create conventions for patterns with 3+ occurrences
        for prefix, examples in prefix_counts.items():
            if len(examples) >= 3:
                conv_id = hashlib.sha256(f"{prefix}:{entity_type.value}".encode()).hexdigest()[:12]
                conventions.append(
                    Convention(
                        id=f"conv_{conv_id}",
                        type=ConventionType.PREFIX,
                        pattern=prefix,
                        applies_to=[entity_type],
                        examples=examples[:5],  # Max 5 examples
                        frequency=len(examples),
                        confidence=min(0.95, 0.7 + (len(examples) * 0.05)),
                        detected_at=datetime.now(),
                        tool=DataTool.DBT,
                    )
                )

        return conventions

    def _detect_suffix_patterns(self, names: list[str], entity_type: EntityType) -> list[Convention]:
        """Detect suffix patterns."""
        conventions = []
        suffix_counts: dict[str, list[str]] = {}

        # Common column suffixes
        common_suffixes = ["_id", "_key", "_at", "_date", "_amount", "_count", "_flag"]

        for name in names:
            for suffix in common_suffixes:
                if name.endswith(suffix):
                    if suffix not in suffix_counts:
                        suffix_counts[suffix] = []
                    suffix_counts[suffix].append(name)

        # Create conventions for patterns with 3+ occurrences
        for suffix, examples in suffix_counts.items():
            if len(examples) >= 3:
                conv_id = hashlib.sha256(f"{suffix}:{entity_type.value}".encode()).hexdigest()[:12]
                conventions.append(
                    Convention(
                        id=f"conv_{conv_id}",
                        type=ConventionType.SUFFIX,
                        pattern=suffix,
                        applies_to=[entity_type],
                        examples=examples[:5],
                        frequency=len(examples),
                        confidence=min(0.95, 0.7 + (len(examples) * 0.05)),
                        detected_at=datetime.now(),
                        tool=DataTool.DBT,
                    )
                )

        return conventions

    def extract_yaml_descriptions(self) -> list[Decision]:
        """Extract descriptions from YAML as decisions."""
        decisions = []

        for node_id, node in self.manifest.get("nodes", {}).items():
            if node.get("resource_type") != "model":
                continue

            description = node.get("description", "").strip()
            if description and len(description) > 20:
                # This is substantial documentation - treat as a decision
                dec_id = hashlib.sha256(f"yaml:{node_id}".encode()).hexdigest()[:12]
                decisions.append(
                    Decision(
                        id=f"dec_{dec_id}",
                        entity=node.get("name"),
                        entity_type=EntityType.MODEL,
                        change_type=ChangeType.CREATED,
                        why=description,
                        context="From dbt model documentation",
                        source=DecisionSource.YAML_DESCRIPTION,
                        source_ref=node.get("original_file_path", ""),
                        author="unknown",
                        timestamp=datetime.now(),
                        confidence=0.8,
                        tags=["documentation"],
                        tool=DataTool.DBT,
                    )
                )

        return decisions
