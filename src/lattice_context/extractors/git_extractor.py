"""Extract decisions from git history."""

from __future__ import annotations

from typing import Optional

import hashlib
import re
from datetime import datetime
from pathlib import Path

from git import Commit, Repo

from lattice_context.core.errors import GitNotFoundError
from lattice_context.core.types import (
    ChangeType,
    DataTool,
    Decision,
    DecisionSource,
    EntityType,
)


class GitExtractor:
    """Extract decisions from git commit history."""

    # Patterns to detect in commit messages
    PATTERNS = [
        (r"add(?:ed|ing)?\s+(?:column|field)\s+[`']?(\w+)[`']?", ChangeType.CREATED, EntityType.COLUMN),
        (r"(?:remove|drop)(?:ed|ing)?\s+(?:column|field)\s+[`']?(\w+)[`']?", ChangeType.REMOVED, EntityType.COLUMN),
        (r"add(?:ed|ing)?\s+(?:model|table)\s+[`']?(\w+)[`']?", ChangeType.CREATED, EntityType.MODEL),
        (r"(?:create|add)(?:ed|ing)?\s+[`']?(\w+)[`']?\s+(?:model|table)", ChangeType.CREATED, EntityType.MODEL),
        (r"(?:update|modify|change)(?:ed|ing)?\s+(?:join|logic)\s+(?:in|for)\s+[`']?(\w+)[`']?", ChangeType.LOGIC_CHANGED, EntityType.MODEL),
        (r"(?:rename|refactor)(?:ed|ing)?\s+[`']?(\w+)[`']?\s+to\s+[`']?(\w+)[`']?", ChangeType.RENAMED, EntityType.MODEL),
        (r"(?:fix|correct)(?:ed|ing)?\s+[`']?(\w+)[`']?", ChangeType.MODIFIED, EntityType.MODEL),
    ]

    def __init__(self, repo_path: Path, limit: int = 500):
        try:
            self.repo = Repo(repo_path, search_parent_directories=True)
        except Exception:
            raise GitNotFoundError()
        self.limit = limit

    def extract_decisions(self, branch: str = "main") -> list[Decision]:
        """Extract decisions from git history."""
        decisions = []

        try:
            # Get commits from the specified branch
            commits = list(self.repo.iter_commits(branch, max_count=self.limit))
        except Exception:
            # If branch doesn't exist, try HEAD
            try:
                commits = list(self.repo.iter_commits("HEAD", max_count=self.limit))
            except Exception:
                # No commits yet
                return []

        for commit in commits:
            # Skip merge commits
            if len(commit.parents) > 1:
                continue

            commit_decisions = self._analyze_commit(commit)
            decisions.extend(commit_decisions)

        return decisions

    def _analyze_commit(self, commit: Commit) -> list[Decision]:
        """Analyze a single commit for decisions."""
        decisions = []
        message = commit.message.strip()

        # Skip if message is too generic
        if len(message) < 10 or message.lower() in ["wip", "update", "fix", "refactor"]:
            return []

        # Try pattern-based extraction
        for pattern, change_type, entity_type in self.PATTERNS:
            matches = re.finditer(pattern, message, re.IGNORECASE)
            for match in matches:
                entity_name = match.group(1) if match.groups() else "unknown"

                # Extract the "why" from the commit message
                # Use the full message if it's substantial, otherwise use the summary
                lines = message.split("\n")
                summary = lines[0]
                body = "\n".join(lines[2:]) if len(lines) > 2 else ""

                why = body if body and len(body) > 20 else summary

                dec_id = hashlib.sha256(f"{commit.hexsha}:{entity_name}".encode()).hexdigest()[:12]

                decision = Decision(
                    id=f"dec_{dec_id}",
                    entity=entity_name,
                    entity_type=entity_type,
                    change_type=change_type,
                    why=why,
                    context=f"Commit: {commit.hexsha[:7]}",
                    source=DecisionSource.GIT_COMMIT,
                    source_ref=commit.hexsha,
                    author=commit.author.email if commit.author else "unknown",
                    timestamp=datetime.fromtimestamp(commit.committed_date),
                    confidence=0.7,  # Pattern-based has medium confidence
                    tags=self._extract_tags(message),
                    tool=DataTool.DBT,  # Assume dbt for now, could be smarter
                )
                decisions.append(decision)

        # If no patterns matched but message is substantial, create a generic decision
        if not decisions and len(message) > 50:
            # Try to extract entity from changed files
            entity = self._guess_entity_from_diff(commit)
            if entity:
                dec_id = hashlib.sha256(f"{commit.hexsha}:{entity}".encode()).hexdigest()[:12]
                decision = Decision(
                    id=f"dec_{dec_id}",
                    entity=entity,
                    entity_type=EntityType.MODEL,
                    change_type=ChangeType.MODIFIED,
                    why=message,
                    context=f"Commit: {commit.hexsha[:7]}",
                    source=DecisionSource.GIT_COMMIT,
                    source_ref=commit.hexsha,
                    author=commit.author.email if commit.author else "unknown",
                    timestamp=datetime.fromtimestamp(commit.committed_date),
                    confidence=0.5,  # Lower confidence for generic extraction
                    tags=self._extract_tags(message),
                    tool=DataTool.DBT,
                )
                decisions.append(decision)

        return decisions

    def _guess_entity_from_diff(self, commit: Commit) -> Optional[str]:
        """Guess entity name from changed files."""
        try:
            if not commit.parents:
                return None

            diffs = commit.parents[0].diff(commit)
            for diff in diffs:
                if diff.a_path and ".sql" in diff.a_path:
                    # Extract filename without extension
                    path = Path(diff.a_path)
                    return path.stem
        except Exception:
            pass
        return None

    def _extract_tags(self, message: str) -> list[str]:
        """Extract tags from commit message."""
        tags = []

        # Common tags
        tag_patterns = [
            (r"JIRA-\d+", "jira"),
            (r"#\d+", "github-issue"),
            (r"\bbreaking\b", "breaking-change"),
            (r"\bfeat(?:ure)?\b", "feature"),
            (r"\bfix\b", "bugfix"),
            (r"\brefactor\b", "refactor"),
            (r"\btest\b", "test"),
            (r"\bdocs?\b", "documentation"),
        ]

        for pattern, tag in tag_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                tags.append(tag)

        return tags
