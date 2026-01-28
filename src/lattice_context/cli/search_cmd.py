"""Search command to find indexed content."""

from __future__ import annotations

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
        conn = db.connect()
        decisions = db.search_decisions(query, limit=limit)

        if not decisions:
            console.print(f"[yellow]No decisions found matching '{query}'[/yellow]")
            console.print("[dim]Try different keywords or check indexed content with 'lattice list decisions'[/dim]")
            return

        # Get team activity for all decisions
        decision_ids = [d.id for d in decisions]
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

        # Create table with team activity
        table = Table(title=f"Search Results for '{query}' ({len(decisions)} found)", show_lines=True)
        table.add_column("Entity", style="cyan", no_wrap=True)
        table.add_column("Why", style="white", max_width=50)
        table.add_column("Team", style="yellow", justify="center")
        table.add_column("ID", style="dim", no_wrap=True)

        for decision in decisions:
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

        # Show helpful hints
        has_team_activity = any(
            a["score"] != 0 or a["comments"] > 0 or a["status"] != "active"
            for a in team_activity.values()
        )

        if has_team_activity:
            console.print("\n[dim]Legend: +N=votes, 💬=comments, ✓=verified, ⚠=outdated[/dim]")
            console.print("[dim]Use ID to interact: lattice team comment <id> \"your thoughts\"[/dim]")
        else:
            console.print("\n[dim]💡 Start a discussion: lattice team comment <id> \"your thoughts\"[/dim]")

        if len(decisions) == limit:
            console.print(f"\n[dim]Showing top {limit} results. Use --limit to see more.[/dim]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if hasattr(e, "hint"):
            console.print(f"\n[yellow]Hint: {e.hint}[/yellow]")
