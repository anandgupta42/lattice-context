"""Tests for CLI commands."""

import json
import os
import shutil
import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from lattice_context.cli import app

runner = CliRunner()


@pytest.fixture
def temp_dbt_project():
    """Create a temporary dbt project for testing."""
    temp_dir = Path(tempfile.mkdtemp())

    # Create dbt_project.yml
    (temp_dir / "dbt_project.yml").write_text("""
name: 'test_project'
version: '1.0.0'
config-version: 2
profile: 'test'
model-paths: ["models"]
target-path: "target"
""")

    # Create models directory
    (temp_dir / "models").mkdir()

    # Create a simple model
    (temp_dir / "models" / "customers.sql").write_text("""
select
    customer_id as customer_key,
    customer_name,
    revenue_amount
from raw.customers
""")

    # Create target/manifest.json
    (temp_dir / "target").mkdir()
    manifest = {
        "metadata": {"generated_at": "2024-01-27T00:00:00.000000Z"},
        "nodes": {
            "model.test_project.customers": {
                "resource_type": "model",
                "name": "customers",
                "schema": "analytics",
                "database": "prod",
                "original_file_path": "models/customers.sql",
                "description": "Customer dimension table",
                "columns": {
                    "customer_key": {
                        "name": "customer_key",
                        "description": "Unique customer ID",
                        "data_type": "integer"
                    },
                    "revenue_amount": {
                        "name": "revenue_amount",
                        "description": "Lifetime revenue",
                        "data_type": "decimal"
                    }
                }
            }
        }
    }
    (temp_dir / "target" / "manifest.json").write_text(json.dumps(manifest))

    yield temp_dir

    # Cleanup
    shutil.rmtree(temp_dir)


def test_cli_help():
    """Test that CLI shows help."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Lattice Context Layer" in result.output
    assert "init" in result.output
    assert "index" in result.output


def test_init_command(temp_dbt_project):
    """Test lattice init command."""
    # Change to temp directory
    original_dir = os.getcwd()
    os.chdir(temp_dbt_project)

    try:
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        assert "Detected project type: dbt" in result.output
        assert "Ready to go" in result.output

        # Check that .lattice directory was created
        assert (temp_dbt_project / ".lattice").exists()
        assert (temp_dbt_project / ".lattice" / "config.yml").exists()
        assert (temp_dbt_project / ".lattice" / "index.db").exists()
    finally:
        os.chdir(original_dir)


def test_init_already_initialized(temp_dbt_project):
    """Test that init warns if already initialized."""
    original_dir = os.getcwd()
    os.chdir(temp_dbt_project)

    try:
        # Init once
        runner.invoke(app, ["init"])

        # Try to init again
        result = runner.invoke(app, ["init"])
        assert "already initialized" in result.output.lower()
    finally:
        os.chdir(original_dir)


def test_index_command(temp_dbt_project):
    """Test lattice index command."""
    original_dir = os.getcwd()
    os.chdir(temp_dbt_project)

    try:
        # First init
        runner.invoke(app, ["init"])

        # Then index
        result = runner.invoke(app, ["index"])
        assert result.exit_code == 0
        assert "Indexing complete" in result.output
        assert "Entities:" in result.output
        assert "Decisions:" in result.output
    finally:
        os.chdir(original_dir)


def test_status_command_not_initialized(temp_dbt_project):
    """Test status command when not initialized."""
    original_dir = os.getcwd()
    os.chdir(temp_dbt_project)

    try:
        result = runner.invoke(app, ["status"])
        assert result.exit_code != 0 or "not initialized" in result.output.lower()
    finally:
        os.chdir(original_dir)


def test_status_command(temp_dbt_project):
    """Test lattice status command."""
    original_dir = os.getcwd()
    os.chdir(temp_dbt_project)

    try:
        # Init and index first
        runner.invoke(app, ["init"])
        runner.invoke(app, ["index"])

        # Check status
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "Lattice Status" in result.output or "Entities" in result.output
    finally:
        os.chdir(original_dir)


def test_context_command(temp_dbt_project):
    """Test lattice context command."""
    original_dir = os.getcwd()
    os.chdir(temp_dbt_project)

    try:
        # Setup
        runner.invoke(app, ["init"])
        runner.invoke(app, ["index"])

        # Query context
        result = runner.invoke(app, ["context", "customers"])
        assert result.exit_code == 0
        # Should return some context
        assert len(result.output) > 50
    finally:
        os.chdir(original_dir)


def test_correct_command(temp_dbt_project):
    """Test lattice correct command."""
    original_dir = os.getcwd()
    os.chdir(temp_dbt_project)

    try:
        # Setup
        runner.invoke(app, ["init"])

        # Add correction
        result = runner.invoke(app, ["correct", "revenue_amount", "Always exclude refunds"])
        assert result.exit_code == 0
        assert "Correction added" in result.output
    finally:
        os.chdir(original_dir)


def test_init_no_dbt_project():
    """Test init fails gracefully when not in dbt project."""
    with tempfile.TemporaryDirectory() as temp_dir:
        result = runner.invoke(app, ["init"], cwd=temp_dir)
        assert result.exit_code != 0 or "Could not auto-detect" in result.output
