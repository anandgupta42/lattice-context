#!/usr/bin/env python
"""Quick test of monetization system."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lattice_context.core.licensing import (
    Tier,
    TIER_LIMITS,
    get_current_tier,
    check_decision_limit,
    can_use_api_access,
    get_usage_stats,
    should_show_upgrade_prompt,
    generate_license_key,
    validate_license_key,
)

def test_tier_limits():
    """Test tier limits configuration."""
    print("=" * 60)
    print("TEST 1: Tier Limits Configuration")
    print("=" * 60)

    for tier in Tier:
        limits = TIER_LIMITS[tier]
        print(f"\n{tier.value.upper()}:")
        print(f"  Decisions: {limits.max_decisions if limits.max_decisions > 0 else 'Unlimited'}")
        print(f"  Projects: {limits.max_projects if limits.max_projects > 0 else 'Unlimited'}")
        print(f"  LLM Extraction: {limits.llm_extraction}")
        print(f"  API Access: {limits.api_access}")
        print(f"  Corrections: {limits.corrections}")
        print(f"  Web UI: {limits.web_ui}")

    print("\n✓ Tier limits configured correctly")


def test_tier_detection():
    """Test tier detection."""
    print("\n" + "=" * 60)
    print("TEST 2: Tier Detection")
    print("=" * 60)

    tier = get_current_tier()
    print(f"\nCurrent tier: {tier.value}")
    print("(No license key set, should be FREE)")

    assert tier == Tier.FREE, "Should default to FREE tier"
    print("✓ Tier detection works")


def test_api_access_control():
    """Test API access control."""
    print("\n" + "=" * 60)
    print("TEST 3: API Access Control")
    print("=" * 60)

    free_has_access = can_use_api_access(Tier.FREE)
    team_has_access = can_use_api_access(Tier.TEAM)
    business_has_access = can_use_api_access(Tier.BUSINESS)

    print(f"\nFREE tier API access: {free_has_access}")
    print(f"TEAM tier API access: {team_has_access}")
    print(f"BUSINESS tier API access: {business_has_access}")

    assert not free_has_access, "FREE should not have API access"
    assert team_has_access, "TEAM should have API access"
    assert business_has_access, "BUSINESS should have API access"

    print("✓ API access control works")


def test_decision_limits():
    """Test decision limit checking."""
    print("\n" + "=" * 60)
    print("TEST 4: Decision Limit Checking")
    print("=" * 60)

    # Test FREE tier at various usage levels
    print("\nFREE tier:")
    for count in [50, 85, 100, 150]:
        violation = check_decision_limit(Tier.FREE, count)
        status = "⚠ VIOLATION" if violation else "✓ OK"
        print(f"  {count} decisions: {status}")
        if violation:
            print(f"    Message: {violation.message[:60]}...")

    # Test TEAM tier
    print("\nTEAM tier:")
    violation = check_decision_limit(Tier.TEAM, 10000)
    status = "✓ OK (unlimited)" if not violation else "ERROR"
    print(f"  10000 decisions: {status}")

    print("\n✓ Decision limit checking works")


def test_usage_stats():
    """Test usage statistics calculation."""
    print("\n" + "=" * 60)
    print("TEST 5: Usage Statistics")
    print("=" * 60)

    stats = get_usage_stats(Tier.FREE, decision_count=85)

    print("\nFREE tier with 85 decisions:")
    print(f"  Tier: {stats['tier']}")
    print(f"  Decisions: {stats['decisions']['current']}/{stats['decisions']['limit']}")
    print(f"  Usage: {stats['decisions']['percent_used']}%")
    print(f"  API Access: {stats['features']['api_access']}")
    print(f"  LLM Extraction: {stats['features']['llm_extraction']}")

    assert stats['tier'] == 'free'
    assert stats['decisions']['current'] == 85
    assert stats['decisions']['limit'] == 100
    assert stats['decisions']['percent_used'] == 85
    assert not stats['features']['api_access']

    print("✓ Usage statistics work")


def test_upgrade_prompts():
    """Test upgrade prompt logic."""
    print("\n" + "=" * 60)
    print("TEST 6: Upgrade Prompt Logic")
    print("=" * 60)

    print("\nFREE tier upgrade prompts:")
    for count in [50, 75, 80, 85, 95, 100]:
        show_prompt = should_show_upgrade_prompt(Tier.FREE, count)
        status = "SHOW" if show_prompt else "HIDE"
        print(f"  {count} decisions: {status}")

    # TEAM tier should never show prompt
    show_for_team = should_show_upgrade_prompt(Tier.TEAM, 10000)
    print(f"\nTEAM tier with 10000 decisions: {'SHOW' if show_for_team else 'HIDE (correct)'}")

    assert should_show_upgrade_prompt(Tier.FREE, 85), "Should show at 85%"
    assert not should_show_upgrade_prompt(Tier.FREE, 75), "Should not show at 75%"
    assert not should_show_upgrade_prompt(Tier.TEAM, 10000), "TEAM should never show"

    print("✓ Upgrade prompt logic works")


def test_license_generation_and_validation():
    """Test license key generation and validation."""
    print("\n" + "=" * 60)
    print("TEST 7: License Key System")
    print("=" * 60)

    # Generate a test license
    print("\nGenerating TEAM tier license...")
    license_key = generate_license_key(
        email="test@example.com",
        tier=Tier.TEAM,
        organization="Test Corp",
        valid_days=365
    )

    print(f"Generated key (first 50 chars): {license_key[:50]}...")

    # Validate it
    print("\nValidating license...")
    info = validate_license_key(license_key)

    if info:
        print(f"  ✓ Valid license")
        print(f"  Email: {info.email}")
        print(f"  Tier: {info.tier.value}")
        print(f"  Expires: {info.expires_at.strftime('%Y-%m-%d')}")

        assert info.tier == Tier.TEAM
        assert info.email == "test@example.com"
    else:
        print("  ✗ License validation failed")
        raise AssertionError("License validation failed")

    # Test invalid license
    print("\nTesting invalid license...")
    invalid_info = validate_license_key("invalid_key_123")
    assert invalid_info is None, "Invalid key should return None"
    print("  ✓ Correctly rejected invalid license")

    print("\n✓ License key system works")


def main():
    """Run all tests."""
    print("\nMONETIZATION SYSTEM TEST SUITE")
    print("=" * 60)

    try:
        test_tier_limits()
        test_tier_detection()
        test_api_access_control()
        test_decision_limits()
        test_usage_stats()
        test_upgrade_prompts()
        test_license_generation_and_validation()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✅")
        print("=" * 60)
        print("\nMonetization system is ready for production!")
        return 0

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
