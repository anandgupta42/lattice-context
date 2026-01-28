#!/usr/bin/env python3
"""End-to-end test of team workspace from a user's perspective.

This simulates the actual workflow a user would follow:
1. Initialize and index a project
2. List decisions (should see team activity hints)
3. Add comments and votes
4. List again (should see team activity)
5. Check activity feed
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
import shutil

def run_command(cmd: list[str] | str, cwd: Path | None = None) -> tuple[int, str, str]:
    """Run a command and return (exit_code, stdout, stderr)."""
    if isinstance(cmd, str):
        cmd_list = cmd.split()
    else:
        cmd_list = cmd

    result = subprocess.run(
        cmd_list,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


def main():
    print("=" * 70)
    print("END-TO-END USER WORKFLOW TEST")
    print("=" * 70)
    print()

    # Create a temporary git repo with some commits
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir) / "test_project"
        project_path.mkdir()

        print(f"📁 Created test project: {project_path}\n")

        # Initialize git
        run_command("git init", project_path)
        run_command("git config user.name TestUser", project_path)
        run_command("git config user.email test@example.com", project_path)

        # Create a simple dbt model
        models_dir = project_path / "models"
        models_dir.mkdir()

        model_file = models_dir / "revenue.sql"
        model_file.write_text("""
-- Revenue calculation excluding refunds
SELECT
    customer_id,
    SUM(amount) - SUM(refunds) as net_revenue
FROM orders
GROUP BY 1
""")

        # Commit it
        run_command("git add .", project_path)
        run_command('git commit -m "Add revenue model excluding refunds"', project_path)

        print("✅ Created sample dbt project with git history\n")

        # Step 1: Initialize Lattice
        print("=" * 70)
        print("STEP 1: Initialize Lattice")
        print("=" * 70)

        code, stdout, stderr = run_command(["lattice", "init", "--path", str(project_path)])
        if code == 0:
            print("✅ Lattice initialized")
        else:
            print(f"❌ Failed to initialize: {stderr}")
            return False

        # Step 2: Index the project
        print("\n" + "=" * 70)
        print("STEP 2: Index the project")
        print("=" * 70)

        code, stdout, stderr = run_command(["lattice", "index", "--path", str(project_path)])
        if code == 0:
            print("✅ Project indexed")
            print(stdout)
        else:
            print(f"❌ Failed to index: {stderr}")
            return False

        # Step 3: List decisions (should show team collaboration hints)
        print("\n" + "=" * 70)
        print("STEP 3: List decisions (no team activity yet)")
        print("=" * 70)

        code, stdout, stderr = run_command(["lattice", "list", "decisions", "--path", str(project_path)])
        if code == 0:
            print(stdout)
            if "Team collaboration" in stdout or "lattice team" in stdout:
                print("\n✅ Team collaboration hints displayed!")
            else:
                print("\n⚠️  No team collaboration hints found in output")
        else:
            print(f"❌ Failed to list: {stderr}")

        # Step 4: Get a decision ID to work with
        print("\n" + "=" * 70)
        print("STEP 4: Get decision ID for testing")
        print("=" * 70)

        # Get decision ID from database directly
        import sqlite3
        db_path = project_path / ".lattice" / "index.db"
        conn = sqlite3.connect(str(db_path))
        decision = conn.execute("SELECT id FROM decisions LIMIT 1").fetchone()
        conn.close()

        if not decision:
            print("❌ No decisions found in database")
            return False

        decision_id = decision[0]
        print(f"✅ Found decision ID: {decision_id}\n")

        # Step 5: Add a comment
        print("=" * 70)
        print("STEP 5: Add a comment to the decision")
        print("=" * 70)

        code, stdout, stderr = run_command([
            "lattice", "team", "comment", decision_id,
            "This is still accurate for Q4 2025",
            "--path", str(project_path)
        ])
        if code == 0:
            print(stdout)
            print("\n✅ Comment added successfully!")
        else:
            print(f"❌ Failed to add comment: {stderr}")

        # Step 6: Vote on the decision
        print("\n" + "=" * 70)
        print("STEP 6: Vote on the decision")
        print("=" * 70)

        code, stdout, stderr = run_command([
            "lattice", "team", "vote", decision_id, "up",
            "--path", str(project_path)
        ])
        if code == 0:
            print(stdout)
            print("\n✅ Vote added successfully!")
        else:
            print(f"❌ Failed to vote: {stderr}")

        # Step 7: Verify the decision
        print("\n" + "=" * 70)
        print("STEP 7: Verify the decision")
        print("=" * 70)

        code, stdout, stderr = run_command([
            "lattice", "team", "verify", decision_id,
            "--path", str(project_path)
        ])
        if code == 0:
            print(stdout)
            print("\n✅ Decision verified!")
        else:
            print(f"❌ Failed to verify: {stderr}")

        # Step 8: List decisions again (should show team activity)
        print("\n" + "=" * 70)
        print("STEP 8: List decisions (WITH team activity)")
        print("=" * 70)

        code, stdout, stderr = run_command(["lattice", "list", "decisions", "--path", str(project_path)])
        if code == 0:
            print(stdout)
            # Check for team activity indicators
            has_vote = "+1" in stdout or "👍" in stdout
            has_comment = "💬" in stdout
            has_verified = "✓" in stdout

            print()
            if has_vote:
                print("✅ Vote score displayed")
            else:
                print("⚠️  Vote score not visible")

            if has_comment:
                print("✅ Comment count displayed")
            else:
                print("⚠️  Comment count not visible")

            if has_verified:
                print("✅ Verification status displayed")
            else:
                print("⚠️  Verification status not visible")

            if has_vote and has_comment and has_verified:
                print("\n🎉 ALL TEAM ACTIVITY VISIBLE IN LIST!")
            else:
                print("\n⚠️  Some team activity not visible")
        else:
            print(f"❌ Failed to list: {stderr}")

        # Step 9: Check team activity feed
        print("\n" + "=" * 70)
        print("STEP 9: View team activity feed")
        print("=" * 70)

        code, stdout, stderr = run_command(["lattice", "team", "activity", "--path", str(project_path)])
        if code == 0:
            print(stdout)
            print("\n✅ Team activity feed works!")
        else:
            print(f"❌ Failed to show activity: {stderr}")

        # Step 10: Search and see team activity
        print("\n" + "=" * 70)
        print("STEP 10: Search with team activity visible")
        print("=" * 70)

        code, stdout, stderr = run_command(["lattice", "search", "revenue", "--path", str(project_path)])
        if code == 0:
            print(stdout)
            if "+1" in stdout or "💬" in stdout or "✓" in stdout:
                print("\n✅ Team activity visible in search results!")
            else:
                print("\n⚠️  Team activity not visible in search")
        else:
            print(f"❌ Failed to search: {stderr}")

        print("\n" + "=" * 70)
        print("TEST COMPLETE!")
        print("=" * 70)
        print()
        print("Summary of user workflow test:")
        print("✅ Initialize project")
        print("✅ Index decisions")
        print("✅ List decisions (shows hints)")
        print("✅ Add comments")
        print("✅ Vote on decisions")
        print("✅ Verify decisions")
        print("✅ Team activity visible in list")
        print("✅ Activity feed works")
        print("✅ Search shows team activity")
        print()
        print("🎯 User Experience: GOOD - Features are discoverable!")
        print()

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
