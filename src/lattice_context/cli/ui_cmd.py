"""UI command to start web interface."""

import webbrowser
from pathlib import Path

from rich.console import Console

from lattice_context.core.errors import ProjectNotInitializedError

console = Console()


def start_ui(
    path: Path = Path("."),
    port: int = 8080,
    no_browser: bool = False,
) -> None:
    """Start web UI for Lattice."""
    try:
        lattice_dir = path / ".lattice"

        if not lattice_dir.exists():
            raise ProjectNotInitializedError(path)

        # Import here to avoid loading FastAPI unless needed
        import uvicorn
        from lattice_context.web.api import create_app

        console.print("[cyan]Starting Lattice Web UI...[/cyan]")
        console.print(f"[dim]Project: {path.absolute()}[/dim]")
        console.print(f"[dim]Port: {port}[/dim]")

        # Create FastAPI app
        db_path = lattice_dir / "index.db"
        app = create_app(db_path)

        # Open browser
        if not no_browser:
            url = f"http://localhost:{port}"
            console.print(f"\n[green]✓ Opening browser at {url}[/green]")
            webbrowser.open(url)

        console.print("\n[yellow]Press Ctrl+C to stop the server[/yellow]\n")

        # Start server
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

    except ModuleNotFoundError as e:
        if "uvicorn" in str(e) or "fastapi" in str(e):
            console.print("[red]Error: Web dependencies not installed[/red]")
            console.print("\n[yellow]Install with: pip install 'lattice-context[web]'[/yellow]")
        else:
            raise
    except KeyboardInterrupt:
        console.print("\n[cyan]Stopping server...[/cyan]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if hasattr(e, "hint"):
            console.print(f"\n[yellow]Hint: {e.hint}[/yellow]")
