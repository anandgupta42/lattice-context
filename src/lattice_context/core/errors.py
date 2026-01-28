"""Error types with user-friendly messages."""

from pathlib import Path


class LatticeError(Exception):
    """Base error with user-friendly message."""

    def __init__(self, message: str, hint: str | None = None):
        self.message = message
        self.hint = hint
        super().__init__(message)

    def __str__(self) -> str:
        if self.hint:
            return f"{self.message}\n\nHint: {self.hint}"
        return self.message


class ManifestNotFoundError(LatticeError):
    """Raised when dbt manifest.json cannot be found."""

    def __init__(self, searched_paths: list[Path]):
        super().__init__(
            message="Could not find dbt manifest.json",
            hint=f"Run 'dbt compile' first, or specify path with --manifest.\n"
                 f"Searched: {', '.join(str(p) for p in searched_paths)}"
        )


class GitNotFoundError(LatticeError):
    """Raised when not in a git repository."""

    def __init__(self) -> None:
        super().__init__(
            message="Not a git repository",
            hint="Lattice needs git history to extract decisions. "
                 "Run 'git init' or use --no-git to skip."
        )


class ProjectNotInitializedError(LatticeError):
    """Raised when Lattice is not initialized."""

    def __init__(self, path: Path):
        super().__init__(
            message=f"Lattice not initialized in {path}",
            hint="Run 'lattice init' first to set up Lattice."
        )


class ConfigNotFoundError(LatticeError):
    """Raised when config file not found."""

    def __init__(self, path: Path):
        super().__init__(
            message=f"Config file not found: {path}",
            hint="Run 'lattice init' to create configuration."
        )
