"""CLI command for serving MCP server."""

import asyncio
from pathlib import Path

from rich.console import Console

from lattice_context.core.errors import ProjectNotInitializedError

console = Console()


def serve_mcp(path: Path, transport: str = "stdio", port: int = 3001) -> None:
    """Start MCP server."""
    try:
        lattice_dir = path / ".lattice"

        if not lattice_dir.exists():
            raise ProjectNotInitializedError(path)

        if transport != "stdio":
            console.print("[yellow]Only stdio transport is currently supported[/yellow]")
            return

        console.print(f"[cyan]Starting Lattice MCP server for {path.name}...[/cyan]")
        console.print("[dim]Press Ctrl+C to stop[/dim]")

        # Try to use full MCP server if available, otherwise use simple server
        try:
            from lattice_context.mcp.server import serve
            asyncio.run(serve(path))
        except ImportError:
            from lattice_context.mcp.simple_server import serve_simple
            asyncio.run(serve_simple(path))

    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
