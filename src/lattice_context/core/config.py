"""Configuration management for Lattice."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field


class ProjectConfig(BaseModel):
    """Project configuration."""
    name: str
    type: str = "dbt"


class DbtToolConfig(BaseModel):
    """dbt tool configuration."""
    enabled: bool = True
    manifest_path: str = "target/manifest.json"
    project_path: str = "."


class GitExtractionConfig(BaseModel):
    """Git extraction configuration."""
    enabled: bool = True
    depth: int = 500
    branch: str = "main"
    include_merge_commits: bool = False


class LLMExtractionConfig(BaseModel):
    """LLM extraction configuration."""
    enabled: bool = False
    provider: str = "anthropic"
    model: str = "claude-3-haiku-20240307"


class ExtractionConfig(BaseModel):
    """Extraction configuration."""
    git: GitExtractionConfig = Field(default_factory=GitExtractionConfig)
    llm: LLMExtractionConfig = Field(default_factory=LLMExtractionConfig)


class TokenBudgets(BaseModel):
    """Token budgets for retrieval."""
    tier1_immediate: int = 2500
    tier2_related: int = 2500
    tier3_global: int = 2000


class RetrievalConfig(BaseModel):
    """Retrieval configuration."""
    token_budgets: TokenBudgets = Field(default_factory=TokenBudgets)
    include_code_snippets: bool = True


class ConventionConfig(BaseModel):
    """Convention detection configuration."""
    enabled: bool = True
    min_confidence: float = 0.7
    min_frequency: int = 3


class LatticeConfig(BaseModel):
    """Main Lattice configuration."""
    version: int = 1
    project: ProjectConfig
    tools: dict[str, Any] = Field(default_factory=lambda: {"dbt": DbtToolConfig().model_dump()})
    extraction: ExtractionConfig = Field(default_factory=ExtractionConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    conventions: ConventionConfig = Field(default_factory=ConventionConfig)
    license_key: Optional[str] = None  # Optional license key for paid tiers

    @classmethod
    def load(cls, path: Path) -> "LatticeConfig":
        """Load configuration from a file."""
        config_path = path / ".lattice" / "config.yml"
        if not config_path.exists():
            raise FileNotFoundError(f"Config not found: {config_path}")

        with open(config_path) as f:
            data = yaml.safe_load(f)

        return cls(**data)

    def save(self, path: Path) -> None:
        """Save configuration to a file."""
        config_path = path / ".lattice" / "config.yml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w") as f:
            yaml.safe_dump(self.model_dump(exclude_none=True), f, default_flow_style=False)
