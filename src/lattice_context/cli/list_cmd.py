"""List command to show indexed content."""

from pathlib import Path

from rich.console import Console
from rich.table import Table

from lattice_context.core.errors import ProjectNotInitializedError
from lattice_context.storage.database import Database

console = Console()


def list_decisions(
    path: Path = Path("."),
    limit: int = 20,
    entity: str | None = None,
) -> None:
    """List indexed decisions."""
    try:
        lattice_dir = path / ".lattice"

        if not lattice_dir.exists():
            raise ProjectNotInitializedError(path)

        db = Database(lattice_dir / "index.db")
        decisions = db.list_decisions(limit=limit if not entity else 1000)

        # Filter by entity if specified
        if entity:
            decisions = [d for d in decisions if entity.lower() in d.entity.lower()]

        if not decisions:
            console.print("[yellow]No decisions found.[/yellow]")
            if entity:
                console.print(f"[dim]No decisions matching '{entity}'[/dim]")
            return

        # Create table
        table = Table(title=f"Indexed Decisions ({len(decisions)} found)", show_lines=True)
        table.add_column("Entity", style="cyan", no_wrap=True)
        table.add_column("Type", style="magenta")
        table.add_column("Why", style="white")
        table.add_column("Source", style="dim")

        for decision in decisions[:limit]:
            table.add_row(
                decision.entity,
                decision.change_type.value,
                decision.why[:80] + "..." if len(decision.why) > 80 else decision.why,
                f"{decision.source.value}/{decision.tool.value}",
            )

        console.print(table)

        if len(decisions) > limit:
            console.print(f"\n[dim]Showing {limit} of {len(decisions)} decisions. Use --limit to see more.[/dim]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if hasattr(e, "hint"):
            console.print(f"\n[yellow]Hint: {e.hint}[/yellow]")


def list_conventions(path: Path = Path(".")) -> None:
    """List detected conventions."""
    try:
        lattice_dir = path / ".lattice"

        if not lattice_dir.exists():
            raise ProjectNotInitializedError(path)

        db = Database(lattice_dir / "index.db")
        conventions = db.get_conventions()

        if not conventions:
            console.print("[yellow]No conventions detected.[/yellow]")
            console.print("[dim]Conventions are detected when 3+ entities follow the same pattern.[/dim]")
            return

        # Create table
        table = Table(title=f"Detected Conventions ({len(conventions)} found)", show_lines=True)
        table.add_column("Type", style="magenta")
        table.add_column("Pattern", style="cyan")
        table.add_column("Examples", style="green")

        for convention in conventions:
            examples_str = ", ".join(convention.examples[:5])
            if len(convention.examples) > 5:
                examples_str += f" (+{len(convention.examples) - 5} more)"

            table.add_row(
                convention.type.value,
                convention.pattern,
                examples_str,
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if hasattr(e, "hint"):
            console.print(f"\n[yellow]Hint: {e.hint}[/yellow]")


def list_corrections(path: Path = Path(".")) -> None:
    """List user corrections."""
    try:
        lattice_dir = path / ".lattice"

        if not lattice_dir.exists():
            raise ProjectNotInitializedError(path)

        db = Database(lattice_dir / "index.db")
        corrections = db.get_corrections()

        if not corrections:
            console.print("[yellow]No corrections added yet.[/yellow]")
            console.print("[dim]Use 'lattice correct <entity> <correction>' to add corrections.[/dim]")
            return

        # Create table
        table = Table(title=f"User Corrections ({len(corrections)} found)", show_lines=True)
        table.add_column("Entity", style="cyan", no_wrap=True)
        table.add_column("Correction", style="white")
        table.add_column("Priority", style="magenta")

        for correction in corrections:
            table.add_row(
                correction.entity,
                correction.correction[:100] + "..." if len(correction.correction) > 100 else correction.correction,
                correction.priority.value,
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if hasattr(e, "hint"):
            console.print(f"\n[yellow]Hint: {e.hint}[/yellow]")
