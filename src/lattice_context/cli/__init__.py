"""CLI commands for Lattice Context Layer."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

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
    tool: Annotated[Optional[str], typer.Option("--tool", help="Index specific tool")] = None,
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
    entity: Annotated[Optional[str], typer.Option("--entity", help="Specific entity")] = None,
    files: Annotated[Optional[str], typer.Option("--files", help="File paths")] = None,
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
    context: Annotated[Optional[str], typer.Option("--context", help="When this applies")] = None,
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
    entity: Annotated[Optional[str], typer.Option("--entity", help="Filter by entity")] = None,
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
    output: Annotated[Optional[Path], typer.Option("--output", help="Output file path")] = None,
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


# Team collaboration commands
team_app = typer.Typer(help="Team collaboration features (comments, votes, verification)")


@team_app.command("comment")
def team_comment(
    decision_id: Annotated[str, typer.Argument(help="Decision ID")],
    message: Annotated[str, typer.Argument(help="Your comment")],
    path: Annotated[Path, typer.Option("--path", help="Project path")] = Path("."),
    author: Annotated[Optional[str], typer.Option("--author", help="Your name")] = None,
    email: Annotated[Optional[str], typer.Option("--email", help="Your email")] = None,
    reply_to: Annotated[Optional[str], typer.Option("--reply-to", help="Reply to comment")] = None,
) -> None:
    """Add a comment to a decision."""
    from lattice_context.cli.team_cmd import comment_on_decision
    comment_on_decision(decision_id, message, path, author, email, reply_to)


@team_app.command("vote")
def team_vote(
    decision_id: Annotated[str, typer.Argument(help="Decision ID")],
    vote_type: Annotated[str, typer.Argument(help="up, down, or remove")],
    path: Annotated[Path, typer.Option("--path", help="Project path")] = Path("."),
    email: Annotated[Optional[str], typer.Option("--email", help="Your email")] = None,
) -> None:
    """Vote on a decision."""
    from lattice_context.cli.team_cmd import vote_on_decision
    vote_on_decision(decision_id, vote_type, path, email)


@team_app.command("verify")
def team_verify(
    decision_id: Annotated[str, typer.Argument(help="Decision ID")],
    path: Annotated[Path, typer.Option("--path", help="Project path")] = Path("."),
    email: Annotated[Optional[str], typer.Option("--email", help="Your email")] = None,
) -> None:
    """Mark a decision as verified."""
    from lattice_context.cli.team_cmd import verify_decision
    verify_decision(decision_id, path, email)


@team_app.command("outdated")
def team_outdated(
    decision_id: Annotated[str, typer.Argument(help="Decision ID")],
    path: Annotated[Path, typer.Option("--path", help="Project path")] = Path("."),
) -> None:
    """Mark a decision as outdated."""
    from lattice_context.cli.team_cmd import mark_outdated
    mark_outdated(decision_id, path)


@team_app.command("activity")
def team_activity(
    path: Annotated[Path, typer.Option("--path", help="Project path")] = Path("."),
    limit: Annotated[int, typer.Option("--limit", help="Number of activities")] = 20,
    activity_type: Annotated[str, typer.Option("--type", help="Filter by type")] = "all",
) -> None:
    """Show recent team activity."""
    from lattice_context.cli.team_cmd import show_activity
    show_activity(path, limit, activity_type)


# Add team commands to main app
app.add_typer(team_app, name="team")


def main() -> None:
    """Main entry point."""
    app()
