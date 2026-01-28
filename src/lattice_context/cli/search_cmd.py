"""Search command to find indexed content."""

from pathlib import Path

from rich.console import Console
from rich.table import Table

from lattice_context.core.errors import ProjectNotInitializedError
from lattice_context.storage.database import Database

console = Console()


def search_decisions(
    query: str,
    path: Path = Path("."),
    limit: int = 20,
) -> None:
    """Search indexed decisions using full-text search."""
    try:
        lattice_dir = path / ".lattice"

        if not lattice_dir.exists():
            raise ProjectNotInitializedError(path)

        db = Database(lattice_dir / "index.db")
        decisions = db.search_decisions(query, limit=limit)

        if not decisions:
            console.print(f"[yellow]No decisions found matching '{query}'[/yellow]")
            console.print("[dim]Try different keywords or check indexed content with 'lattice list decisions'[/dim]")
            return

        # Create table
        table = Table(title=f"Search Results for '{query}' ({len(decisions)} found)", show_lines=True)
        table.add_column("Entity", style="cyan", no_wrap=True)
        table.add_column("Type", style="magenta")
        table.add_column("Why", style="white")
        table.add_column("Score", style="green")

        for decision in decisions:
            table.add_row(
                decision.entity,
                decision.change_type.value,
                decision.why[:80] + "..." if len(decision.why) > 80 else decision.why,
                f"{decision.confidence:.2f}",
            )

        console.print(table)

        if len(decisions) == limit:
            console.print(f"\n[dim]Showing top {limit} results. Use --limit to see more.[/dim]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if hasattr(e, "hint"):
            console.print(f"\n[yellow]Hint: {e.hint}[/yellow]")
