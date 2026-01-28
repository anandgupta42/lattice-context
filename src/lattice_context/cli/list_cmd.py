"""List command to show indexed content."""

from __future__ import annotations

from typing import Optional

from pathlib import Path

from rich.console import Console
from rich.table import Table

from lattice_context.core.errors import ProjectNotInitializedError
from lattice_context.storage.database import Database

console = Console()


def list_decisions(
    path: Path = Path("."),
    limit: int = 20,
    entity: Optional[str] = None,
) -> None:
    """List indexed decisions with team activity."""
    try:
        lattice_dir = path / ".lattice"

        if not lattice_dir.exists():
            raise ProjectNotInitializedError(path)

        db = Database(lattice_dir / "index.db")
        conn = db.connect()
        decisions = db.list_decisions(limit=limit if not entity else 1000)

        # Filter by entity if specified
        if entity:
            decisions = [d for d in decisions if entity.lower() in d.entity.lower()]

        if not decisions:
            console.print("[yellow]No decisions found.[/yellow]")
            if entity:
                console.print(f"[dim]No decisions matching '{entity}'[/dim]")
            return

        # Get team activity for all decisions
        decision_ids = [d.id for d in decisions[:limit]]
        team_activity = {}

        for dec_id in decision_ids:
            # Get metadata
            metadata = db.get_decision_metadata(dec_id)
            # Get comment count
            comments = conn.execute(
                "SELECT COUNT(*) as count FROM decision_comments WHERE decision_id = ?",
                (dec_id,)
            ).fetchone()

            team_activity[dec_id] = {
                "score": metadata["vote_score"] if metadata else 0,
                "status": metadata["status"] if metadata else "active",
                "comments": comments["count"] if comments else 0,
            }

        # Create table with team activity columns
        table = Table(title=f"Indexed Decisions ({len(decisions)} found)", show_lines=True)
        table.add_column("Entity", style="cyan", no_wrap=True)
        table.add_column("Why", style="white", max_width=50)
        table.add_column("Team", style="yellow", justify="center")  # New: team activity
        table.add_column("ID", style="dim", no_wrap=True)

        for decision in decisions[:limit]:
            activity = team_activity[decision.id]

            # Format team activity indicator
            team_indicators = []
            if activity["score"] != 0:
                score_color = "green" if activity["score"] > 0 else "red"
                team_indicators.append(f"[{score_color}]{activity['score']:+d}[/{score_color}]")
            if activity["comments"] > 0:
                team_indicators.append(f"💬{activity['comments']}")
            if activity["status"] == "verified":
                team_indicators.append("[green]✓[/green]")
            elif activity["status"] == "outdated":
                team_indicators.append("[yellow]⚠[/yellow]")

            team_str = " ".join(team_indicators) if team_indicators else "[dim]–[/dim]"

            table.add_row(
                decision.entity,
                decision.why[:50] + "..." if len(decision.why) > 50 else decision.why,
                team_str,
                decision.id,
            )

        console.print(table)

        # Show helpful hints about team features
        has_team_activity = any(
            a["score"] != 0 or a["comments"] > 0 or a["status"] != "active"
            for a in team_activity.values()
        )

        if has_team_activity:
            console.print("\n[dim]Legend: +N=votes, 💬=comments, ✓=verified, ⚠=outdated[/dim]")
            console.print("[dim]Use 'lattice team activity' to see recent team discussions[/dim]")
        else:
            console.print("\n[dim]💡 Team collaboration:[/dim]")
            console.print("  lattice team vote <id> up     - Mark decision as accurate")
            console.print("  lattice team comment <id> \"...\" - Discuss decisions")
            console.print("  lattice team verify <id>      - Verify it's still valid")

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
