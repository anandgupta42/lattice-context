"""Export command to export indexed content."""

import json
from pathlib import Path

from rich.console import Console

from lattice_context.core.errors import ProjectNotInitializedError
from lattice_context.storage.database import Database

console = Console()


def export_data(
    path: Path = Path("."),
    output: Path | None = None,
    format: str = "json",
) -> None:
    """Export all indexed data to JSON."""
    try:
        lattice_dir = path / ".lattice"

        if not lattice_dir.exists():
            raise ProjectNotInitializedError(path)

        db = Database(lattice_dir / "index.db")

        # Gather all data
        decisions = db.list_decisions(limit=10000)
        conventions = db.get_conventions()
        corrections = db.get_corrections()

        # Convert to dicts
        data = {
            "decisions": [
                {
                    "id": d.id,
                    "entity": d.entity,
                    "entity_type": d.entity_type.value,
                    "change_type": d.change_type.value,
                    "why": d.why,
                    "context": d.context,
                    "source": d.source.value,
                    "source_ref": d.source_ref,
                    "author": d.author,
                    "timestamp": d.timestamp.isoformat(),
                    "confidence": d.confidence,
                    "tags": d.tags,
                    "tool": d.tool.value,
                }
                for d in decisions
            ],
            "conventions": [
                {
                    "id": c.id,
                    "type": c.type.value,
                    "pattern": c.pattern,
                    "description": c.description,
                    "applies_to": [e.value for e in c.applies_to],
                    "examples": c.examples,
                    "frequency": c.frequency,
                    "confidence": c.confidence,
                    "detected_at": c.detected_at.isoformat(),
                    "tool": c.tool.value,
                }
                for c in conventions
            ],
            "corrections": [
                {
                    "id": c.id,
                    "entity": c.entity,
                    "entity_type": c.entity_type.value if c.entity_type else None,
                    "correction": c.correction,
                    "context": c.context,
                    "added_by": c.added_by,
                    "added_at": c.added_at.isoformat(),
                    "scope": c.scope.value,
                    "priority": c.priority.value,
                }
                for c in corrections
            ],
            "metadata": {
                "entities": db.count_entities(),
                "decisions": db.count_decisions(),
                "conventions": db.count_conventions(),
                "corrections": db.count_corrections(),
                "last_indexed_at": db.last_indexed_at().isoformat() if db.last_indexed_at() else None,
            }
        }

        # Determine output path
        if output is None:
            output = path / "lattice-export.json"

        # Write JSON
        with open(output, "w") as f:
            json.dump(data, f, indent=2)

        console.print(f"[green]✓ Exported {len(decisions)} decisions, {len(conventions)} conventions, {len(corrections)} corrections[/green]")
        console.print(f"[cyan]Output: {output}[/cyan]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if hasattr(e, "hint"):
            console.print(f"\n[yellow]Hint: {e.hint}[/yellow]")
