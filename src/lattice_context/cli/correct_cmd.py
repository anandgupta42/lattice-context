"""CLI command for adding corrections."""

import hashlib
from datetime import datetime
from pathlib import Path

from rich.console import Console

from lattice_context.core.errors import ProjectNotInitializedError
from lattice_context.core.types import Correction, CorrectionPriority, CorrectionScope
from lattice_context.storage.database import Database

console = Console()


def add_correction(
    entity: str,
    correction: str,
    path: Path,
    context: str | None = None,
    scope: str = "entity"
) -> None:
    """Add a correction."""
    try:
        lattice_dir = path / ".lattice"

        if not lattice_dir.exists():
            raise ProjectNotInitializedError(path)

        db = Database(lattice_dir / "index.db")

        # Create correction
        correction_id = hashlib.sha256(f"{entity}:{correction}".encode()).hexdigest()[:12]
        corr = Correction(
            id=f"corr_{correction_id}",
            entity=entity,
            entity_type=None,
            correction=correction,
            context=context or "",
            added_by="user",
            added_at=datetime.now(),
            scope=CorrectionScope(scope),
            priority=CorrectionPriority.MEDIUM,
        )

        db.add_correction(corr)

        console.print(f"[green]✓[/green] Correction added for '{entity}'")
        console.print(f"\n  {correction}")

        if context:
            console.print(f"\n  Context: {context}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
