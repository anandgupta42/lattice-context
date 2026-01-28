"""Upgrade command."""

import webbrowser

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def show_upgrade_info() -> None:
    """Show upgrade information and pricing."""

    console.print()
    console.print(Panel.fit(
        "[bold cyan]Lattice Context Layer - Upgrade[/bold cyan]",
        border_style="cyan"
    ))

    # Create pricing table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Tier", style="cyan", width=12)
    table.add_column("Price", style="green", width=15)
    table.add_column("Decisions", width=12)
    table.add_column("Projects", width=10)
    table.add_column("LLM Extract", width=12)
    table.add_column("API Access", width=12)

    table.add_row(
        "FREE",
        "$0/month",
        "100",
        "1",
        "No",
        "MCP only"
    )
    table.add_row(
        "TEAM",
        "$50/month",
        "Unlimited",
        "5",
        "Yes",
        "Full"
    )
    table.add_row(
        "BUSINESS",
        "$200/month",
        "Unlimited",
        "Unlimited",
        "Yes",
        "Full"
    )

    console.print()
    console.print(table)
    console.print()

    console.print("[bold]Team Tier Includes:[/bold]")
    console.print("  • Unlimited decisions")
    console.print("  • Up to 5 projects")
    console.print("  • LLM-enhanced extraction")
    console.print("  • Full API access (Copilot, Cursor, Windsurf)")
    console.print("  • Priority support")
    console.print()

    console.print("[bold]Business Tier Includes:[/bold]")
    console.print("  • Everything in Team")
    console.print("  • Unlimited projects")
    console.print("  • Dedicated support")
    console.print("  • Custom integrations")
    console.print()

    console.print("[dim]Note: Lattice is currently in beta. Paid tiers coming soon![/dim]")
    console.print()

    # Ask if user wants to open upgrade page
    console.print("For more information or to join the waitlist:")
    console.print("  [cyan]https://altimate.ai/lattice/upgrade[/cyan]")
    console.print()

    try:
        open_browser = console.input("Open in browser? [y/N]: ")
        if open_browser.lower() in ["y", "yes"]:
            webbrowser.open("https://altimate.ai/lattice/upgrade")
            console.print("[green]✓[/green] Opened in browser")
    except (EOFError, KeyboardInterrupt):
        console.print()
