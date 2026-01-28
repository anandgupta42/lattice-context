"""CLI command for indexing projects."""

import time
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn

from lattice_context.core.config import LatticeConfig
from lattice_context.core.errors import ManifestNotFoundError, ProjectNotInitializedError
from lattice_context.core.licensing import check_decision_limit, get_current_tier
from lattice_context.core.logging import configure_logging, get_logger
from lattice_context.extractors.dbt_extractor import DbtExtractor
from lattice_context.extractors.git_extractor import GitExtractor
from lattice_context.storage.database import Database

console = Console()
logger = get_logger(__name__)


def index_project(path: Path, incremental: bool = False, tool: str | None = None, verbose: bool = False) -> None:
    """Index a project to extract decisions and conventions."""
    # Configure logging
    configure_logging(verbose)

    try:
        lattice_dir = path / ".lattice"

        if not lattice_dir.exists():
            raise ProjectNotInitializedError(path)

        logger.info("indexing_started", project_path=str(path), incremental=incremental)

        # Load config
        config = LatticeConfig.load(path)
        db = Database(lattice_dir / "index.db")

        start_time = time.time()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
        ) as progress:

            # Phase 1: Parse manifest
            task1 = progress.add_task("[cyan]Parsing dbt manifest...", total=1)

            dbt_config = config.tools.get("dbt", {})
            manifest_path = path / dbt_config.get("manifest_path", "target/manifest.json")

            if not manifest_path.exists():
                raise ManifestNotFoundError([manifest_path])

            extractor = DbtExtractor(manifest_path)
            extractor.load_manifest()
            logger.info("manifest_parsed", path=str(manifest_path))
            progress.update(task1, completed=1)

            # Phase 2: Extract entities
            task2 = progress.add_task("[cyan]Extracting entities...", total=1)
            entities = extractor.extract_entities()
            logger.info("entities_extracted", count=len(entities))

            if verbose:
                console.print(f"  Found {len(entities)} entities")

            progress.update(task2, completed=1)

            # Phase 3: Detect conventions
            task3 = progress.add_task("[cyan]Detecting conventions...", total=1)
            conventions = extractor.detect_conventions()
            logger.info("conventions_detected", count=len(conventions))

            if verbose:
                console.print(f"  Detected {len(conventions)} conventions")

            for convention in conventions:
                db.add_convention(convention)

            progress.update(task3, completed=1)

            # Phase 4: Extract from YAML descriptions
            task4 = progress.add_task("[cyan]Extracting YAML descriptions...", total=1)
            yaml_decisions = extractor.extract_yaml_descriptions()
            logger.info("yaml_decisions_extracted", count=len(yaml_decisions))

            if verbose:
                console.print(f"  Extracted {len(yaml_decisions)} descriptions")

            for decision in yaml_decisions:
                db.add_decision(decision)

            progress.update(task4, completed=1)

            # Phase 5: Git history (if enabled)
            git_decisions = []
            if config.extraction.git.enabled:
                task5 = progress.add_task("[cyan]Analyzing git history...", total=1)

                try:
                    git_extractor = GitExtractor(
                        path,
                        limit=config.extraction.git.depth
                    )
                    git_decisions = git_extractor.extract_decisions(
                        branch=config.extraction.git.branch
                    )
                    logger.info("git_decisions_extracted", count=len(git_decisions))

                    if verbose:
                        console.print(f"  Extracted {len(git_decisions)} decisions from git")

                    for decision in git_decisions:
                        db.add_decision(decision)

                except Exception as e:
                    logger.warning("git_extraction_failed", error=str(e))
                    if verbose:
                        console.print(f"  [yellow]Git extraction skipped: {e}[/yellow]")

                progress.update(task5, completed=1)

            # Phase 6: Store results
            task6 = progress.add_task("[cyan]Storing results...", total=1)
            db.set_last_indexed_at(datetime.now())
            progress.update(task6, completed=1)

        elapsed = time.time() - start_time

        # Summary
        total_decisions = len(yaml_decisions) + len(git_decisions)

        logger.info(
            "indexing_complete",
            elapsed_seconds=round(elapsed, 2),
            entities=len(entities),
            conventions=len(conventions),
            decisions=total_decisions
        )

        console.print()
        console.print(f"[green]✓[/green] Indexing complete in {elapsed:.1f}s")
        console.print()
        console.print(f"  Entities:    {len(entities)}")
        console.print(f"  Conventions: {len(conventions)}")
        console.print(f"  Decisions:   {total_decisions}")
        console.print()

        # Check tier limits
        tier = get_current_tier()
        violation = check_decision_limit(tier, total_decisions)
        if violation:
            console.print(f"[yellow]⚠ {violation.message}[/yellow]")
            console.print("[dim]Run 'lattice upgrade' for more info[/dim]")
            console.print()

        if total_decisions == 0:
            console.print("[yellow]⚠ No decisions extracted. Consider:[/yellow]")
            console.print("  • Adding descriptions to your dbt models")
            console.print("  • Using more descriptive commit messages")
            console.print("  • Adding corrections with 'lattice correct'")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if hasattr(e, "hint"):
            console.print(f"\n[yellow]Hint: {e.hint}[/yellow]")
