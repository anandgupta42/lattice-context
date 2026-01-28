"""
CLI command for universal context API server.
"""

from pathlib import Path
from rich.console import Console

from lattice_context.integrations.context_server import start_server

console = Console()


def start_api_server(
    path: Path = Path("."),
    port: int = 8082,
    host: str = "0.0.0.0",
) -> None:
    """Start universal context API server.

    Args:
        path: Project root directory
        port: Port to run on (default: 8082)
        host: Host to bind to (default: 0.0.0.0)
    """
    console.print(f"\n[bold cyan]Starting Lattice Universal Context API[/bold cyan]")
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
    console.print(f"\n[bold green]API Server running at http://{host}:{port}[/bold green]")
    console.print("\n[bold]Supported AI Tools:[/bold]")
    console.print("  • Cursor")
    console.print("  • Windsurf")
    console.print("  • VS Code (any extension)")
    console.print("  • GitHub Copilot")
    console.print("  • Generic (any tool with HTTP)")
    console.print("\n[bold]Key Endpoints:[/bold]")
    console.print("  POST /v1/context - Universal context endpoint")
    console.print("  POST /v1/context/cursor - Cursor-specific")
    console.print("  POST /v1/context/windsurf - Windsurf-specific")
    console.print("  POST /v1/context/vscode - VS Code-specific")
    console.print("  GET  /health - Health check")
    console.print("\n[dim]Press Ctrl+C to stop[/dim]\n")

    try:
        start_server(project_root=path, port=port, host=host)
    except KeyboardInterrupt:
        console.print("\n[yellow]API server stopped[/yellow]")
