"""CLI command for showing status."""

from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.table import Table

from lattice_context.core.errors import ProjectNotInitializedError
from lattice_context.storage.database import Database

console = Console()


def show_status(path: Path) -> None:
    """Show Lattice status."""
    try:
        lattice_dir = path / ".lattice"

        if not lattice_dir.exists():
            raise ProjectNotInitializedError(path)

        db = Database(lattice_dir / "index.db")

        # Check if indexed
        if not db.is_indexed():
            console.print("[yellow]Not indexed yet. Run 'lattice index' to start.[/yellow]")
            return

        # Get stats
        last_indexed = db.last_indexed_at()
        entities = db.count_entities()
        decisions = db.count_decisions()
        conventions = db.count_conventions()
        corrections = db.count_corrections()

        # Create status table
        table = Table(title="Lattice Status", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Entities", str(entities))
        table.add_row("Decisions", str(decisions))
        table.add_row("Conventions", str(conventions))
        table.add_row("Corrections", str(corrections))

        if last_indexed:
            time_ago = datetime.now() - last_indexed
            if time_ago.days > 0:
                time_str = f"{time_ago.days} day(s) ago"
            elif time_ago.seconds > 3600:
                time_str = f"{time_ago.seconds // 3600} hour(s) ago"
            else:
                time_str = f"{time_ago.seconds // 60} minute(s) ago"
            table.add_row("Last indexed", time_str)

        console.print(table)

        # Status indicator
        if decisions > 0 and conventions > 0:
            console.print("\n[green]✓[/green] Ready to serve context")
        else:
            console.print("\n[yellow]⚠[/yellow] Low data - consider running 'lattice index' again")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
