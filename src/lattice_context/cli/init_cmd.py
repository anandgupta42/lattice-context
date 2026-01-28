"""CLI command for initializing Lattice."""

from __future__ import annotations

from typing import Optional

from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from lattice_context.core.config import DbtToolConfig, LatticeConfig, ProjectConfig
from lattice_context.core.errors import LatticeError
from lattice_context.storage.database import Database

console = Console()


def detect_project_type(path: Path) -> Optional[str]:
    """Auto-detect project type. User should never need to configure this."""
    # dbt detection (most common)
    if (path / "dbt_project.yml").exists():
        return "dbt"

    # SQLMesh detection
    if (path / "sqlmesh" / "config.py").exists():
        return "sqlmesh"

    # Airflow detection
    if (path / "dags").is_dir() or (path / "airflow.cfg").exists():
        return "airflow"

    return None


def find_manifest(path: Path) -> Optional[Path]:
    """Find dbt manifest without user config."""
    candidates = [
        path / "target" / "manifest.json",
        path / "manifest.json",
        path / "dbt_packages" / "manifest.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def init_project(path: Path, force: bool = False) -> None:
    """Initialize Lattice in a project."""
    try:
        lattice_dir = path / ".lattice"

        # Check if already initialized
        if lattice_dir.exists() and not force:
            console.print(
                f"[yellow]Lattice already initialized in {path}[/yellow]",
            )
            console.print("Use --force to reinitialize")
            return

        # Detect project type
        project_type = detect_project_type(path)
        if not project_type:
            console.print(
                f"[red]Could not auto-detect project type in {path}[/red]",
            )
            console.print("\nLooking for one of:")
            console.print("  • dbt_project.yml (dbt)")
            console.print("  • dags/ (Airflow)")
            console.print("  • sqlmesh/config.py (SQLMesh)")
            return

        console.print(f"[green]✓[/green] Detected project type: [bold]{project_type}[/bold]")

        # For dbt, find manifest
        manifest_path = None
        if project_type == "dbt":
            manifest_path = find_manifest(path)
            if manifest_path:
                console.print(f"[green]✓[/green] Found manifest: {manifest_path.relative_to(path)}")
            else:
                console.print(
                    "[yellow]⚠[/yellow] manifest.json not found. Run 'dbt compile' to generate it."
                )

        # Create .lattice directory
        lattice_dir.mkdir(parents=True, exist_ok=True)
        console.print(f"[green]✓[/green] Created {lattice_dir.relative_to(path)}")

        # Create config
        config = LatticeConfig(
            version=1,
            project=ProjectConfig(
                name=path.name,
                type=project_type,
            ),
            tools={
                "dbt": DbtToolConfig(
                    enabled=True,
                    manifest_path=str(manifest_path.relative_to(path)) if manifest_path else "target/manifest.json",
                    project_path=".",
                ).model_dump()
            }
        )
        config.save(path)
        console.print("[green]✓[/green] Created config.yml")

        # Initialize database
        db = Database(lattice_dir / "index.db")
        db.initialize()
        console.print("[green]✓[/green] Initialized database")

        # Create corrections file
        corrections_file = lattice_dir / "corrections.jsonl"
        corrections_file.touch()
        console.print("[green]✓[/green] Created corrections.jsonl")

        # Success message
        console.print()
        console.print(
            Panel(
                "[bold green]Lattice initialized successfully![/bold green]\n\n"
                "Next steps:\n"
                "  1. [cyan]lattice index[/cyan] - Index your project\n"
                "  2. [cyan]lattice serve[/cyan] - Start MCP server\n"
                "  3. Configure Claude Desktop to use Lattice",
                title="🎉 Ready to go",
                border_style="green",
            )
        )

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if isinstance(e, LatticeError) and e.hint:
            console.print(f"\n[yellow]Hint: {e.hint}[/yellow]")
