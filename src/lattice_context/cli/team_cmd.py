"""CLI commands for team collaboration features."""

from __future__ import annotations

from typing import Optional

import subprocess
import sys
from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from typing_extensions import Annotated

from lattice_context.config import get_config
from lattice_context.storage.database import Database

console = Console()


def get_git_user_info() -> tuple[str, str]:
    """Get user name and email from git config."""
    try:
        name_result = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True,
            text=True,
            check=True
        )
        email_result = subprocess.run(
            ["git", "config", "user.email"],
            capture_output=True,
            text=True,
            check=True
        )
        return name_result.stdout.strip(), email_result.stdout.strip()
    except subprocess.CalledProcessError:
        console.print("[red]Error: Could not get git user info.[/red]")
        console.print("[dim]Make sure git is configured:[/dim]")
        console.print("  git config user.name \"Your Name\"")
        console.print("  git config user.email \"you@example.com\"")
        sys.exit(1)


def comment_on_decision(
    decision_id: Annotated[str, typer.Argument(help="Decision ID to comment on")],
    message: Annotated[str, typer.Argument(help="Your comment")],
    path: Annotated[Path, typer.Option("--path", help="Project path")] = Path("."),
    author: Annotated[Optional[str], typer.Option("--author", help="Your name")] = None,
    email: Annotated[Optional[str], typer.Option("--email", help="Your email")] = None,
    reply_to: Annotated[Optional[str], typer.Option("--reply-to", help="Comment ID to reply to")] = None,
) -> None:
    """Add a comment to a decision.

    Examples:
        lattice team comment dec_abc123 "This is still accurate"
        lattice team comment dec_abc123 "Great point!" --reply-to cmt_xyz789
    """
    config = get_config()
    db = Database(config.db_path)

    # Get author info from git if not provided
    if not author or not email:
        git_name, git_email = get_git_user_info()
        author = author or git_name
        email = email or git_email

    # Verify decision exists
    conn = db.connect()
    decision = conn.execute("SELECT * FROM decisions WHERE id = ?", (decision_id,)).fetchone()
    if not decision:
        console.print(f"[red]Error: Decision '{decision_id}' not found.[/red]")
        console.print("\n[dim]Tip: Use 'lattice search <query>' to find decisions[/dim]")
        sys.exit(1)

    # Verify reply-to comment exists if specified
    if reply_to:
        parent_comment = conn.execute(
            "SELECT * FROM decision_comments WHERE id = ?",
            (reply_to,)
        ).fetchone()
        if not parent_comment:
            console.print(f"[red]Error: Comment '{reply_to}' not found.[/red]")
            sys.exit(1)

    # Add comment
    comment_id = db.add_comment(
        decision_id=decision_id,
        author=author,
        author_email=email,
        content=message,
        parent_id=reply_to
    )

    # Show success with context
    console.print(f"\n[green]✓[/green] Comment added: [cyan]{comment_id}[/cyan]")
    console.print(f"[dim]On decision:[/dim] {decision['why']}")

    if reply_to:
        console.print(f"[dim]Replying to:[/dim] {reply_to}")

    # Show all comments on this decision
    comments = db.get_comments(decision_id)
    if len(comments) > 1:
        console.print(f"\n[dim]💬 This decision now has {len(comments)} comments[/dim]")


def vote_on_decision(
    decision_id: Annotated[str, typer.Argument(help="Decision ID to vote on")],
    vote_type: Annotated[str, typer.Argument(help="up, down, or remove")],
    path: Annotated[Path, typer.Option("--path", help="Project path")] = Path("."),
    email: Annotated[Optional[str], typer.Option("--email", help="Your email")] = None,
) -> None:
    """Vote on a decision (upvote, downvote, or remove vote).

    Upvote means the decision is still accurate and useful.
    Downvote means the decision may be outdated or needs review.

    Examples:
        lattice team vote dec_abc123 up      # Mark as accurate
        lattice team vote dec_abc123 down    # Mark as needs review
        lattice team vote dec_abc123 remove  # Remove your vote
    """
    if vote_type not in ["up", "down", "remove"]:
        console.print(f"[red]Error: Invalid vote type '{vote_type}'[/red]")
        console.print("[yellow]Valid options: up, down, remove[/yellow]")
        sys.exit(1)

    config = get_config()
    db = Database(config.db_path)

    # Get email from git if not provided
    if not email:
        _, git_email = get_git_user_info()
        email = git_email

    # Verify decision exists
    conn = db.connect()
    decision = conn.execute("SELECT * FROM decisions WHERE id = ?", (decision_id,)).fetchone()
    if not decision:
        console.print(f"[red]Error: Decision '{decision_id}' not found.[/red]")
        sys.exit(1)

    # Convert vote type to value
    vote_value = {"up": 1, "down": -1, "remove": 0}[vote_type]

    # Record vote
    db.vote_decision(decision_id, email, vote_value)

    # Get new score
    score = db.get_vote_score(decision_id)

    # Show success
    if vote_type == "remove":
        console.print(f"\n[yellow]○[/yellow] Vote removed")
    elif vote_type == "up":
        console.print(f"\n[green]↑[/green] Upvoted (marked as accurate)")
    else:
        console.print(f"\n[red]↓[/red] Downvoted (marked as needs review)")

    console.print(f"[dim]Decision:[/dim] {decision['why']}")
    console.print(f"[dim]Team score:[/dim] [bold]{score:+d}[/bold]")

    # Show interpretation
    if score >= 3:
        console.print("[green]✓ Highly trusted by team[/green]")
    elif score <= -3:
        console.print("[red]⚠ Team thinks this needs review[/red]")


def verify_decision(
    decision_id: Annotated[str, typer.Argument(help="Decision ID to verify")],
    path: Annotated[Path, typer.Option("--path", help="Project path")] = Path("."),
    email: Annotated[Optional[str], typer.Option("--email", help="Your email")] = None,
) -> None:
    """Mark a decision as verified (still accurate).

    Use this to confirm a decision is still valid after reviewing it.

    Example:
        lattice team verify dec_abc123
    """
    config = get_config()
    db = Database(config.db_path)

    # Get email from git if not provided
    if not email:
        _, git_email = get_git_user_info()
        email = git_email

    # Verify decision exists
    conn = db.connect()
    decision = conn.execute("SELECT * FROM decisions WHERE id = ?", (decision_id,)).fetchone()
    if not decision:
        console.print(f"[red]Error: Decision '{decision_id}' not found.[/red]")
        sys.exit(1)

    # Mark as verified
    db.verify_decision(decision_id, email)

    # Show success
    console.print(f"\n[green]✓[/green] Decision verified by {email}")
    console.print(f"[dim]Decision:[/dim] {decision['why']}")
    console.print(f"[dim]Status:[/dim] [green]Verified[/green]")


def mark_outdated(
    decision_id: Annotated[str, typer.Argument(help="Decision ID to mark as outdated")],
    path: Annotated[Path, typer.Option("--path", help="Project path")] = Path("."),
) -> None:
    """Mark a decision as outdated (no longer valid).

    Use this when a decision has been superseded or is no longer accurate.

    Example:
        lattice team outdated dec_abc123
    """
    config = get_config()
    db = Database(config.db_path)

    # Verify decision exists
    conn = db.connect()
    decision = conn.execute("SELECT * FROM decisions WHERE id = ?", (decision_id,)).fetchone()
    if not decision:
        console.print(f"[red]Error: Decision '{decision_id}' not found.[/red]")
        sys.exit(1)

    # Mark as outdated
    db.mark_outdated(decision_id)

    # Show success
    console.print(f"\n[yellow]⚠[/yellow] Decision marked as outdated")
    console.print(f"[dim]Decision:[/dim] {decision['why']}")
    console.print(f"[dim]Status:[/dim] [yellow]Outdated[/yellow]")
    console.print("\n[dim]Tip: Outdated decisions are excluded from context by default[/dim]")


def show_activity(
    path: Annotated[Path, typer.Option("--path", help="Project path")] = Path("."),
    limit: Annotated[int, typer.Option("--limit", help="Number of activities")] = 20,
    activity_type: Annotated[str, typer.Option("--type", help="all, comments, votes, or verifications")] = "all",
) -> None:
    """Show recent team activity (comments, votes, verifications).

    This helps you stay aware of what your team is discussing and verifying.

    Examples:
        lattice team activity                    # Show all recent activity
        lattice team activity --limit 50         # Show more activity
        lattice team activity --type comments    # Only show comments
    """
    config = get_config()
    db = Database(config.db_path)
    conn = db.connect()

    activities = []

    # Get comments
    if activity_type in ["all", "comments"]:
        comments = conn.execute("""
            SELECT
                c.id,
                c.decision_id,
                c.author,
                c.author_email,
                c.content,
                c.created_at,
                d.why as decision_why,
                d.entity as decision_entity
            FROM decision_comments c
            JOIN decisions d ON c.decision_id = d.id
            ORDER BY c.created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()

        for comment in comments:
            activities.append({
                "type": "comment",
                "time": datetime.fromisoformat(comment["created_at"]),
                "author": comment["author"],
                "email": comment["author_email"],
                "decision_id": comment["decision_id"],
                "decision_why": comment["decision_why"],
                "decision_entity": comment["decision_entity"],
                "content": comment["content"],
            })

    # Get votes
    if activity_type in ["all", "votes"]:
        votes = conn.execute("""
            SELECT
                v.decision_id,
                v.user_email,
                v.vote,
                v.created_at,
                d.why as decision_why,
                d.entity as decision_entity
            FROM decision_votes v
            JOIN decisions d ON v.decision_id = d.id
            ORDER BY v.created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()

        for vote in votes:
            activities.append({
                "type": "vote",
                "time": datetime.fromisoformat(vote["created_at"]),
                "email": vote["user_email"],
                "decision_id": vote["decision_id"],
                "decision_why": vote["decision_why"],
                "decision_entity": vote["decision_entity"],
                "vote": vote["vote"],
            })

    # Get verifications
    if activity_type in ["all", "verifications"]:
        verifications = conn.execute("""
            SELECT
                m.decision_id,
                m.last_verified_by,
                m.last_verified_at,
                d.why as decision_why,
                d.entity as decision_entity
            FROM decision_metadata m
            JOIN decisions d ON m.decision_id = d.id
            WHERE m.status = 'verified' AND m.last_verified_at IS NOT NULL
            ORDER BY m.last_verified_at DESC
            LIMIT ?
        """, (limit,)).fetchall()

        for verification in verifications:
            activities.append({
                "type": "verification",
                "time": datetime.fromisoformat(verification["last_verified_at"]),
                "email": verification["last_verified_by"],
                "decision_id": verification["decision_id"],
                "decision_why": verification["decision_why"],
                "decision_entity": verification["decision_entity"],
            })

    # Sort by time
    activities.sort(key=lambda x: x["time"], reverse=True)
    activities = activities[:limit]

    if not activities:
        console.print("\n[dim]No team activity yet[/dim]")
        console.print("\n[bold]Get started with team features:[/bold]")
        console.print("  lattice team comment <decision_id> \"your thoughts\"")
        console.print("  lattice team vote <decision_id> up")
        console.print("  lattice team verify <decision_id>")
        return

    # Display activity feed
    console.print(f"\n[bold]Recent Team Activity[/bold] ({len(activities)} items)\n")

    for activity in activities:
        # Format time
        time_str = activity["time"].strftime("%Y-%m-%d %H:%M")

        # Icon and message based on type
        if activity["type"] == "comment":
            icon = "💬"
            author = activity.get("author", activity["email"])
            message = f"[cyan]{author}[/cyan] commented on [yellow]{activity['decision_entity']}[/yellow]"
            details = f'"{activity["content"][:80]}{"..." if len(activity["content"]) > 80 else ""}"'
        elif activity["type"] == "vote":
            icon = "👍" if activity["vote"] > 0 else "👎"
            message = f"[cyan]{activity['email']}[/cyan] {'upvoted' if activity['vote'] > 0 else 'downvoted'} [yellow]{activity['decision_entity']}[/yellow]"
            details = activity["decision_why"]
        else:  # verification
            icon = "✓"
            message = f"[cyan]{activity['email']}[/cyan] verified [yellow]{activity['decision_entity']}[/yellow]"
            details = activity["decision_why"]

        console.print(f"{icon} [dim]{time_str}[/dim] {message}")
        console.print(f"   [dim]{details}[/dim]")
        console.print()
