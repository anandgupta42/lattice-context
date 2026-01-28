"""
CLI command for GitHub Copilot integration.
"""

from pathlib import Path
from rich.console import Console

from lattice_context.integrations.copilot_server import start_server

console = Console()


def start_copilot_server(
    path: Path = Path("."),
    port: int = 8081,
    host: str = "0.0.0.0",
) -> None:
    """Start Copilot context server.

    Args:
        path: Project root directory
        port: Port to run on (default: 8081)
        host: Host to bind to (default: 0.0.0.0)
    """
    console.print(f"\n[bold cyan]Starting Lattice Copilot Context Server[/bold cyan]")
    console.print(f"[dim]Project: {path.absolute()}[/dim]")
    console.print(f"[dim]Server: http://{host}:{port}[/dim]\n")

    console.print("[yellow]→[/yellow] Initializing context provider...")

    lattice_dir = path / ".lattice"
    if not lattice_dir.exists():
        console.print(
            "[red]✗[/red] Lattice not initialized. Run [cyan]lattice init[/cyan] first."
        )
        return

    db_path = lattice_dir / "index.db"
    if not db_path.exists():
        console.print(
            "[red]✗[/red] Lattice not indexed. Run [cyan]lattice index[/cyan] first."
        )
        return

    console.print("[green]✓[/green] Context provider ready")
    console.print(f"\n[bold green]Server running at http://{host}:{port}[/bold green]")
    console.print("\n[bold]Available endpoints:[/bold]")
    console.print("  POST /context - Get context for a query")
    console.print("  POST /context/file - Get context for a file")
    console.print("  POST /context/entity - Get context for an entity")
    console.print("  POST /context/chat - Get context for Copilot Chat")
    console.print("  GET  /context/all - Export all context")
    console.print("  GET  /health - Health check")
    console.print("\n[dim]Press Ctrl+C to stop[/dim]\n")

    try:
        start_server(project_root=path, port=port, host=host)
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped[/yellow]")
