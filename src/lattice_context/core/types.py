"""Core type definitions for Lattice Context Layer."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class EntityType(str, Enum):
    """Types of entities we track."""
    MODEL = "model"
    COLUMN = "column"
    METRIC = "metric"
    DIMENSION = "dimension"
    TABLE = "table"
    VIEW = "view"
    SCHEMA = "schema"
    DATABASE = "database"
    DAG = "dag"
    TASK = "task"
    SCHEDULE = "schedule"
    DASHBOARD = "dashboard"


class ChangeType(str, Enum):
    """Types of changes to entities."""
    CREATED = "created"
    MODIFIED = "modified"
    REMOVED = "removed"
    RENAMED = "renamed"
    LOGIC_CHANGED = "logic_changed"
    DEPENDENCY_ADDED = "dependency_added"
    DEPENDENCY_REMOVED = "dependency_removed"
    TEST_ADDED = "test_added"


class DecisionSource(str, Enum):
    """Source of a decision."""
    GIT_COMMIT = "git_commit"
    PR_DESCRIPTION = "pr_description"
    PR_COMMENT = "pr_comment"
    CODE_COMMENT = "code_comment"
    YAML_DESCRIPTION = "yaml_description"
    USER_CORRECTION = "user_correction"


class DataTool(str, Enum):
    """Data stack tools we support."""
    DBT = "dbt"
    SQLMESH = "sqlmesh"
    SNOWFLAKE = "snowflake"
    DATABRICKS = "databricks"
    BIGQUERY = "bigquery"
    AIRFLOW = "airflow"
    DAGSTER = "dagster"
    LOOKER = "looker"


class Decision(BaseModel):
    """A captured decision about why something was built a certain way."""
    id: str
    entity: str
    entity_type: EntityType
    change_type: ChangeType
    why: str
    context: str = ""
    source: DecisionSource
    source_ref: str
    author: str
    timestamp: datetime
    confidence: float = Field(ge=0.0, le=1.0)
    tags: list[str] = Field(default_factory=list)
    tool: DataTool


class ConventionType(str, Enum):
    """Types of conventions."""
    PREFIX = "prefix"
    SUFFIX = "suffix"
    CASE = "case"
    SEPARATOR = "separator"
    DIRECTORY_STRUCTURE = "directory_structure"
    TEST_PATTERN = "test_pattern"


class Convention(BaseModel):
    """A detected naming or structural pattern."""
    id: str
    type: ConventionType
    pattern: str
    applies_to: list[EntityType]
    examples: list[str]
    frequency: int
    confidence: float = Field(ge=0.0, le=1.0)
    detected_at: datetime
    tool: DataTool


class CorrectionScope(str, Enum):
    """Scope of a correction."""
    GLOBAL = "global"
    ENTITY = "entity"
    PATTERN = "pattern"


class CorrectionPriority(str, Enum):
    """Priority of a correction."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Correction(BaseModel):
    """User-provided knowledge that overrides or supplements extracted context."""
    id: str
    entity: str
    entity_type: Optional[EntityType] = None
    correction: str
    context: str = ""
    added_by: str
    added_at: datetime
    scope: CorrectionScope = CorrectionScope.ENTITY
    priority: CorrectionPriority = CorrectionPriority.MEDIUM


class TierContent(BaseModel):
    """Content for a specific tier."""
    content: str
    tokens: int
    sources: list[str]


class ContextRequest(BaseModel):
    """Request for context."""
    task: Optional[str] = None
    files: Optional[list[str]] = None
    entities: Optional[list[str]] = None
    max_tokens: int = 8000
    tools: Optional[list[DataTool]] = None
    include_decisions: bool = True
    include_conventions: bool = True
    include_corrections: bool = True


class ContextResponse(BaseModel):
    """Response containing context."""
    tiers: dict[str, TierContent]
    decisions: list[Decision]
    conventions: list[Convention]
    corrections: list[Correction]
    total_tokens: int
    sources: list[str]


class IndexResult(BaseModel):
    """Result of an indexing operation."""
    entities: int
    conventions: int
    decisions: int
    elapsed_seconds: float


# Team Workspace Types (v0.2.0)


class DecisionStatus(str, Enum):
    """Status of a decision."""
    ACTIVE = "active"
    VERIFIED = "verified"
    OUTDATED = "outdated"


class Comment(BaseModel):
    """A comment on a decision."""
    id: str
    decision_id: str
    author: str
    author_email: str
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    parent_id: Optional[str] = None


class Vote(BaseModel):
    """A vote on a decision."""
    decision_id: str
    user_email: str
    vote: int  # 1 for upvote, -1 for downvote
    created_at: datetime


class DecisionMetadata(BaseModel):
    """Metadata for a decision."""
    decision_id: str
    status: DecisionStatus = DecisionStatus.ACTIVE
    last_verified_at: Optional[datetime] = None
    last_verified_by: Optional[str] = None
    vote_score: int = 0
