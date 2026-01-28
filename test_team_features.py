#!/usr/bin/env python3
"""Test script to validate team workspace features from user perspective."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lattice_context.storage.database import Database
from lattice_context.core.types import Decision, EntityType, ChangeType, DecisionSource, DataTool
from datetime import datetime


def test_team_workflow():
    """Simulate real team collaboration workflow."""
    print("🧪 Testing Team Workspace Features\n")

    # Initialize database
    db_path = Path("/tmp/test_lattice_team.db")
    db_path.unlink(missing_ok=True)  # Clean start

    db = Database(db_path)
    db.initialize()  # Create tables
    print("✅ Database initialized\n")

    # Create a sample decision
    decision = Decision(
        id="dec_test123",
        entity="revenue",
        entity_type=EntityType.MODEL,
        change_type=ChangeType.LOGIC_CHANGED,
        why="Revenue now excludes refunds per accounting policy",
        context="Updated Q4 2025 after accounting team feedback",
        source=DecisionSource.GIT_COMMIT,
        source_ref="abc123",
        author="sarah",
        timestamp=datetime.now(),
        confidence=0.9,
        tags=["revenue", "accounting"],
        tool=DataTool.DBT
    )

    db.add_decision(decision)
    print(f"✅ Created decision: {decision.why}\n")

    # Test 1: Add comments (team discussion)
    print("📝 Test 1: Team Discussion via Comments")
    print("-" * 50)

    try:
        # James asks a question
        comment1_id = db.add_comment(
            decision_id="dec_test123",
            author="James Chen",
            author_email="james@company.com",
            content="Does this apply to all regions or just North America?"
        )
        print(f"✅ James added question: {comment1_id}")

        # Sarah responds
        comment2_id = db.add_comment(
            decision_id="dec_test123",
            author="Sarah Kim",
            author_email="sarah@company.com",
            content="All regions! We standardized this globally.",
            parent_id=comment1_id  # Threading
        )
        print(f"✅ Sarah replied: {comment2_id}")

        # Get all comments
        comments = db.get_comments("dec_test123")
        print(f"\n💬 Total comments: {len(comments)}")
        for c in comments:
            indent = "  " if c["parent_id"] else ""
            print(f"{indent}└─ {c['author']}: \"{c['content']}\"")

        print("\n✅ Comment threading works!\n")

    except Exception as e:
        print(f"❌ PROBLEM: Comments failed - {e}\n")
        return False

    # Test 2: Voting (team consensus)
    print("👍 Test 2: Team Voting for Consensus")
    print("-" * 50)

    try:
        # Three team members upvote
        db.vote_decision("dec_test123", "james@company.com", 1)
        db.vote_decision("dec_test123", "sarah@company.com", 1)
        db.vote_decision("dec_test123", "maya@company.com", 1)
        print("✅ 3 team members upvoted")

        # One person changes their mind
        db.vote_decision("dec_test123", "maya@company.com", -1)
        print("✅ Maya changed vote to downvote")

        # Check score
        score = db.get_vote_score("dec_test123")
        print(f"\n🎯 Final score: {score} (2 up, 1 down)")

        # Get individual vote
        maya_vote = db.get_user_vote("dec_test123", "maya@company.com")
        print(f"📊 Maya's vote: {maya_vote}")

        if score != 1:  # 2 upvotes - 1 downvote
            print(f"❌ PROBLEM: Expected score 1, got {score}")
            return False

        print("\n✅ Voting system works!\n")

    except Exception as e:
        print(f"❌ PROBLEM: Voting failed - {e}\n")
        return False

    # Test 3: Verification (quality control)
    print("✓ Test 3: Decision Verification")
    print("-" * 50)

    try:
        # Senior team member verifies
        db.verify_decision("dec_test123", "sarah@company.com")
        print("✅ Sarah verified the decision")

        # Check metadata
        metadata = db.get_decision_metadata("dec_test123")
        print(f"\n📋 Status: {metadata['status']}")
        print(f"📋 Verified by: {metadata['last_verified_by']}")
        print(f"📋 Vote score: {metadata['vote_score']}")

        if metadata['status'] != 'verified':
            print(f"❌ PROBLEM: Expected 'verified', got '{metadata['status']}'")
            return False

        print("\n✅ Verification works!\n")

    except Exception as e:
        print(f"❌ PROBLEM: Verification failed - {e}\n")
        return False

    # Test 4: Mark as outdated (lifecycle)
    print("🕐 Test 4: Decision Lifecycle Management")
    print("-" * 50)

    try:
        # Later, decision becomes outdated
        db.mark_outdated("dec_test123")
        print("✅ Marked decision as outdated")

        metadata = db.get_decision_metadata("dec_test123")
        print(f"📋 New status: {metadata['status']}")

        if metadata['status'] != 'outdated':
            print(f"❌ PROBLEM: Expected 'outdated', got '{metadata['status']}'")
            return False

        print("\n✅ Lifecycle management works!\n")

    except Exception as e:
        print(f"❌ PROBLEM: Lifecycle failed - {e}\n")
        return False

    print("=" * 50)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 50)
    return True


def identify_experience_gaps():
    """Think critically about UX gaps."""
    print("\n\n🤔 Critical Analysis: Experience Gaps\n")
    print("=" * 50)

    gaps = [
        {
            "area": "Discovery",
            "problem": "How do users know they can comment on decisions?",
            "impact": "HIGH",
            "fix": "Add hints in CLI output, web UI tooltips, onboarding"
        },
        {
            "area": "Notifications",
            "problem": "Team members don't know when decisions are commented/voted",
            "impact": "HIGH",
            "fix": "Email/Slack notifications (Sprint 3)"
        },
        {
            "area": "Comment Threading",
            "problem": "No easy way to see full conversation tree",
            "impact": "MEDIUM",
            "fix": "Better UI visualization, nested display"
        },
        {
            "area": "Vote Meaning",
            "problem": "What does upvote vs downvote actually mean?",
            "impact": "MEDIUM",
            "fix": "Clear labels: 'Still accurate' vs 'Needs update'"
        },
        {
            "area": "Verification Authority",
            "problem": "Who has permission to verify? Anyone?",
            "impact": "HIGH",
            "fix": "Role-based permissions, senior approval flow"
        },
        {
            "area": "Bulk Operations",
            "problem": "Can't mark multiple old decisions as outdated",
            "impact": "LOW",
            "fix": "Bulk update CLI command"
        },
        {
            "area": "Search Integration",
            "problem": "Can't search by vote score or verification status",
            "impact": "MEDIUM",
            "fix": "Update search to filter by metadata"
        },
        {
            "area": "Activity Feed",
            "problem": "No way to see recent team activity",
            "impact": "HIGH",
            "fix": "Activity timeline in web UI + CLI"
        }
    ]

    for i, gap in enumerate(gaps, 1):
        print(f"\n{i}. {gap['area']} ({gap['impact']} IMPACT)")
        print(f"   Problem: {gap['problem']}")
        print(f"   Fix: {gap['fix']}")

    print("\n" + "=" * 50)
    print("📊 Summary:")
    high_impact = sum(1 for g in gaps if g['impact'] == 'HIGH')
    print(f"   - {high_impact} HIGH impact gaps to fix")
    print(f"   - Focus on: Discovery, Notifications, Permissions")
    print("=" * 50)


if __name__ == "__main__":
    success = test_team_workflow()

    if success:
        identify_experience_gaps()
        print("\n💡 Next: Fix HIGH impact gaps before shipping")
    else:
        print("\n❌ Fix core functionality first!")
        sys.exit(1)
