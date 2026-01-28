"""Basic tests to verify core functionality."""

import shutil
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

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
from lattice_context.storage.database import Database


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    db = Database(temp_dir / "test.db")
    db.initialize()
    yield db
    db.close()
    shutil.rmtree(temp_dir)


def test_database_initialization(temp_db):
    """Test that database initializes correctly."""
    assert not temp_db.is_indexed()
    assert temp_db.count_entities() == 0
    assert temp_db.count_decisions() == 0
    assert temp_db.count_conventions() == 0
    assert temp_db.count_corrections() == 0


def test_add_decision(temp_db):
    """Test adding a decision."""
    decision = Decision(
        id="dec_test123",
        entity="dim_customer",
        entity_type=EntityType.MODEL,
        change_type=ChangeType.CREATED,
        why="Created to centralize customer data",
        context="Part of the dimensional model refactor",
        source=DecisionSource.GIT_COMMIT,
        source_ref="abc123",
        author="test@example.com",
        timestamp=datetime.now(),
        confidence=0.9,
        tags=["refactor"],
        tool=DataTool.DBT,
    )

    temp_db.add_decision(decision)
    assert temp_db.count_decisions() == 1

    # Retrieve the decision
    decisions = temp_db.get_decisions_for_entity("dim_customer")
    assert len(decisions) == 1
    assert decisions[0].entity == "dim_customer"
    assert decisions[0].why == "Created to centralize customer data"


def test_add_convention(temp_db):
    """Test adding a convention."""
    convention = Convention(
        id="conv_test456",
        type=ConventionType.PREFIX,
        pattern="dim_",
        applies_to=[EntityType.MODEL],
        examples=["dim_customer", "dim_product"],
        frequency=5,
        confidence=0.95,
        detected_at=datetime.now(),
        tool=DataTool.DBT,
    )

    temp_db.add_convention(convention)
    assert temp_db.count_conventions() == 1

    # Retrieve conventions
    conventions = temp_db.get_conventions()
    assert len(conventions) == 1
    assert conventions[0].pattern == "dim_"


def test_add_correction(temp_db):
    """Test adding a correction."""
    correction = Correction(
        id="corr_test789",
        entity="revenue",
        entity_type=EntityType.COLUMN,
        correction="Always exclude refunds and taxes",
        context="Per finance requirements",
        added_by="user",
        added_at=datetime.now(),
        scope=CorrectionScope.ENTITY,
        priority=CorrectionPriority.HIGH,
    )

    temp_db.add_correction(correction)
    assert temp_db.count_corrections() == 1

    # Retrieve corrections
    corrections = temp_db.get_corrections("revenue")
    assert len(corrections) == 1
    assert corrections[0].correction == "Always exclude refunds and taxes"


def test_search_decisions(temp_db):
    """Test full-text search of decisions."""
    # Add multiple decisions
    decisions = [
        Decision(
            id="dec_1",
            entity="revenue",
            entity_type=EntityType.COLUMN,
            change_type=ChangeType.CREATED,
            why="Added for financial reporting",
            context="",
            source=DecisionSource.GIT_COMMIT,
            source_ref="abc1",
            author="test@example.com",
            timestamp=datetime.now(),
            confidence=0.8,
            tags=["finance"],
            tool=DataTool.DBT,
        ),
        Decision(
            id="dec_2",
            entity="discount",
            entity_type=EntityType.COLUMN,
            change_type=ChangeType.CREATED,
            why="Track promotional discounts",
            context="",
            source=DecisionSource.GIT_COMMIT,
            source_ref="abc2",
            author="test@example.com",
            timestamp=datetime.now(),
            confidence=0.8,
            tags=["promotion"],
            tool=DataTool.DBT,
        ),
    ]

    for decision in decisions:
        temp_db.add_decision(decision)

    # Search for "financial"
    results = temp_db.search_decisions("financial")
    assert len(results) >= 1
    assert any(d.entity == "revenue" for d in results)
