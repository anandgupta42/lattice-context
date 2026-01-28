"""CLI commands for Lattice Context Layer."""

from pathlib import Path

import typer
from typing_extensions import Annotated

app = typer.Typer(
    name="lattice",
    help="Lattice Context Layer - Give AI assistants institutional knowledge",
    no_args_is_help=True,
)


@app.command()
def init(
    path: Annotated[Path, typer.Argument(help="Project path")] = Path("."),
    force: Annotated[bool, typer.Option("--force", help="Overwrite existing config")] = False,
) -> None:
    """Initialize Lattice in a project."""
    from lattice_context.cli.init_cmd import init_project
    init_project(path, force)


@app.command()
def index(
    path: Annotated[Path, typer.Argument(help="Project path")] = Path("."),
    incremental: Annotated[bool, typer.Option("--incremental", help="Incremental index")] = False,
    tool: Annotated[str | None, typer.Option("--tool", help="Index specific tool")] = None,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Verbose output")] = False,
) -> None:
    """Index a project to extract decisions and conventions."""
    from lattice_context.cli.index_cmd import index_project
    index_project(path, incremental, tool, verbose)


@app.command()
def serve(
    path: Annotated[Path, typer.Argument(help="Project path")] = Path("."),
    transport: Annotated[str, typer.Option("--transport", help="stdio or http")] = "stdio",
    port: Annotated[int, typer.Option("--port", help="HTTP port")] = 3001,
) -> None:
    """Start MCP server."""
    from lattice_context.cli.serve_cmd import serve_mcp
    serve_mcp(path, transport, port)


@app.command()
def context(
    query: Annotated[str, typer.Argument(help="What are you trying to do?")],
    path: Annotated[Path, typer.Option("--path", help="Project path")] = Path("."),
    entity: Annotated[str | None, typer.Option("--entity", help="Specific entity")] = None,
    files: Annotated[str | None, typer.Option("--files", help="File paths")] = None,
    format: Annotated[str, typer.Option("--format", help="json or markdown")] = "markdown",
) -> None:
    """Get context for a task."""
    from lattice_context.cli.context_cmd import get_context
    get_context(query, path, entity, files, format)


@app.command()
def correct(
    entity: Annotated[str, typer.Argument(help="Entity name")],
    correction: Annotated[str, typer.Argument(help="Correction text")],
    path: Annotated[Path, typer.Option("--path", help="Project path")] = Path("."),
    context: Annotated[str | None, typer.Option("--context", help="When this applies")] = None,
    scope: Annotated[str, typer.Option("--scope", help="global, entity, pattern")] = "entity",
) -> None:
    """Add a correction."""
    from lattice_context.cli.correct_cmd import add_correction
    add_correction(entity, correction, path, context, scope)


@app.command()
def status(
    path: Annotated[Path, typer.Argument(help="Project path")] = Path("."),
) -> None:
    """Show Lattice status."""
    from lattice_context.cli.status_cmd import show_status
    show_status(path)


@app.command()
def upgrade() -> None:
    """Show upgrade information."""
    from lattice_context.cli.upgrade_cmd import show_upgrade_info
    show_upgrade_info()


@app.command()
def tier() -> None:
    """Show current tier and limits."""
    from lattice_context.cli.tier_cmd import show_tier_info
    show_tier_info()


@app.command(name="list")
def list_cmd(
    what: Annotated[str, typer.Argument(help="What to list: decisions, conventions, corrections")] = "decisions",
    path: Annotated[Path, typer.Option("--path", help="Project path")] = Path("."),
    limit: Annotated[int, typer.Option("--limit", help="Max items to show")] = 20,
    entity: Annotated[str | None, typer.Option("--entity", help="Filter by entity")] = None,
) -> None:
    """List indexed content."""
    from lattice_context.cli.list_cmd import list_decisions, list_conventions, list_corrections

    if what == "decisions":
        list_decisions(path, limit, entity)
    elif what == "conventions":
        list_conventions(path)
    elif what == "corrections":
        list_corrections(path)
    else:
        console = __import__("rich").console.Console()
        console.print(f"[red]Unknown type: {what}[/red]")
        console.print("[yellow]Valid options: decisions, conventions, corrections[/yellow]")


@app.command()
def search(
    query: Annotated[str, typer.Argument(help="Search query")],
    path: Annotated[Path, typer.Option("--path", help="Project path")] = Path("."),
    limit: Annotated[int, typer.Option("--limit", help="Max results")] = 20,
) -> None:
    """Search indexed decisions using full-text search."""
    from lattice_context.cli.search_cmd import search_decisions
    search_decisions(query, path, limit)


@app.command()
def export(
    path: Annotated[Path, typer.Option("--path", help="Project path")] = Path("."),
    output: Annotated[Path | None, typer.Option("--output", help="Output file path")] = None,
    format: Annotated[str, typer.Option("--format", help="Export format")] = "json",
) -> None:
    """Export all indexed data to JSON."""
    from lattice_context.cli.export_cmd import export_data
    export_data(path, output, format)


@app.command()
def ui(
    path: Annotated[Path, typer.Option("--path", help="Project path")] = Path("."),
    port: Annotated[int, typer.Option("--port", help="Port number")] = 8080,
    no_browser: Annotated[bool, typer.Option("--no-browser", help="Don't open browser")] = False,
) -> None:
    """Start web UI."""
    from lattice_context.cli.ui_cmd import start_ui
    start_ui(path, port, no_browser)


@app.command()
def copilot(
    path: Annotated[Path, typer.Option("--path", help="Project path")] = Path("."),
    port: Annotated[int, typer.Option("--port", help="Port number")] = 8081,
    host: Annotated[str, typer.Option("--host", help="Host to bind to")] = "0.0.0.0",
) -> None:
    """Start Copilot context server for GitHub Copilot integration."""
    from lattice_context.cli.copilot_cmd import start_copilot_server
    start_copilot_server(path, port, host)


@app.command()
def api(
    path: Annotated[Path, typer.Option("--path", help="Project path")] = Path("."),
    port: Annotated[int, typer.Option("--port", help="Port number")] = 8082,
    host: Annotated[str, typer.Option("--host", help="Host to bind to")] = "0.0.0.0",
) -> None:
    """Start universal context API for all AI tools (Cursor, Windsurf, VS Code, etc)."""
    from lattice_context.cli.api_cmd import start_api_server
    start_api_server(path, port, host)


def main() -> None:
    """Main entry point."""
    app()
