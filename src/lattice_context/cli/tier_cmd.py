"""Tier command."""

from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from lattice_context.core.licensing import (
    get_current_tier,
    get_limits_for_tier,
)
from lattice_context.storage.database import Database

console = Console()


def show_tier_info() -> None:
    """Show current tier and usage."""

    tier = get_current_tier()
    limits = get_limits_for_tier(tier)

    console.print()
    console.print(Panel.fit(
        f"[bold cyan]Current Tier: {tier.value.upper()}[/bold cyan]",
        border_style="cyan"
    ))
    console.print()

    # Try to get usage stats
    try:
        lattice_dir = Path(".lattice")
        if lattice_dir.exists():
            db_path = lattice_dir / "index.db"
            if db_path.exists():
                db = Database(db_path)
                decision_count = len(db.list_decisions())

                console.print("[bold]Usage:[/bold]")
                console.print()

                # Show decision usage
                if limits.max_decisions > 0:
                    usage_pct = (decision_count / limits.max_decisions) * 100
                    console.print(f"  Decisions: {decision_count} / {limits.max_decisions}")

                    # Progress bar
                    if usage_pct >= 90:
                        style = "red"
                    elif usage_pct >= 75:
                        style = "yellow"
                    else:
                        style = "green"

                    # Simple text-based progress indicator
                    bar_width = 30
                    filled = int((usage_pct / 100) * bar_width)
                    bar = "█" * filled + "░" * (bar_width - filled)
                    console.print(f"  [{style}]{bar}[/{style}] {usage_pct:.0f}%")

                    if usage_pct >= 90:
                        console.print()
                        console.print("  [yellow]⚠ Approaching limit! Consider upgrading.[/yellow]")
                else:
                    console.print(f"  Decisions: {decision_count} (unlimited)")

                console.print()
    except Exception:
        pass

    # Show tier limits
    console.print("[bold]Tier Limits:[/bold]")
    console.print()

    if limits.max_decisions > 0:
        console.print(f"  • Decisions: {limits.max_decisions}")
    else:
        console.print("  • Decisions: Unlimited")

    if limits.max_projects > 0:
        console.print(f"  • Projects: {limits.max_projects}")
    else:
        console.print("  • Projects: Unlimited")

    console.print(f"  • LLM extraction: {'Yes' if limits.llm_extraction else 'No (pattern-based only)'}")
    console.print(f"  • Corrections: {'Yes' if limits.corrections else 'No'}")
    console.print(f"  • API access: {'Yes' if limits.api_access else 'No (MCP only)'}")
    console.print(f"  • Web UI: {'Yes' if limits.web_ui else 'No'}")
    console.print()

    # Show upgrade prompt for free tier
    if tier.name == "FREE":
        console.print("[dim]Want unlimited decisions and LLM extraction?[/dim]")
        console.print("[dim]Run [cyan]lattice upgrade[/cyan] for more info[/dim]")
        console.print()
