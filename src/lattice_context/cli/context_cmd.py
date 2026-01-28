"""CLI command for getting context."""

from __future__ import annotations

from typing import Optional

import asyncio
import json
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown

from lattice_context.core.errors import ProjectNotInitializedError
from lattice_context.mcp.retrieval import ContextRetriever
from lattice_context.storage.database import Database

console = Console()


def get_context(
    query: str,
    path: Path,
    entity: Optional[str] = None,
    files: Optional[str] = None,
    format: str = "markdown"
) -> None:
    """Get context for a task."""
    try:
        lattice_dir = path / ".lattice"

        if not lattice_dir.exists():
            raise ProjectNotInitializedError(path)

        db = Database(lattice_dir / "index.db")
        retriever = ContextRetriever(db)

        # Get context
        response = asyncio.run(retriever.get_context(query))

        # Format output
        if format == "json":
            output = _format_json(response)
            console.print(output)
        else:
            output = _format_markdown(response, query)
            console.print(Markdown(output))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def _format_markdown(response: dict, query: str) -> str:
    """Format response as markdown."""
    sections = [f"# Context for: {query}\n"]

    # Corrections
    corrections = response.get("corrections", [])
    if corrections:
        sections.append("## ⚠️ Important Notes\n")
        for corr in corrections:
            sections.append(f"- **{corr.entity}**: {corr.correction}")
        sections.append("")

    # Immediate decisions
    immediate = response.get("immediate_decisions", [])
    if immediate:
        sections.append("## Relevant Decisions\n")
        for dec in immediate:
            sections.append(f"### {dec.entity} ({dec.change_type.value})\n")
            sections.append(f"{dec.why}\n")
        sections.append("")

    # Conventions
    conventions = response.get("conventions", [])
    if conventions:
        sections.append("## Conventions\n")
        for conv in conventions:
            sections.append(f"- **{conv.pattern}**: {', '.join(conv.examples[:3])}")
        sections.append("")

    # Related
    related = response.get("related_decisions", [])
    if related:
        sections.append("## Related Context\n")
        for dec in related:
            sections.append(f"- **{dec.entity}**: {dec.why}")
        sections.append("")

    if len(sections) == 1:
        sections.append("No context found.")

    return "\n".join(sections)


def _format_json(response: dict) -> str:
    """Format response as JSON."""
    # Convert Pydantic models to dicts
    output = {
        "immediate_decisions": [d.model_dump() for d in response.get("immediate_decisions", [])],
        "related_decisions": [d.model_dump() for d in response.get("related_decisions", [])],
        "corrections": [c.model_dump() for c in response.get("corrections", [])],
        "conventions": [c.model_dump() for c in response.get("conventions", [])],
    }
    return json.dumps(output, indent=2, default=str)
