"""Licensing and tier management."""

import base64
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional


class Tier(Enum):
    """User tier levels."""
    FREE = "free"
    TEAM = "team"
    BUSINESS = "business"


@dataclass
class Limits:
    """Tier limits configuration."""
    max_decisions: int  # -1 for unlimited
    max_projects: int   # -1 for unlimited
    llm_extraction: bool
    corrections: bool
    api_access: bool  # REST API access (Copilot, Universal API)
    web_ui: bool  # Web dashboard access


# Tier limits configuration
TIER_LIMITS = {
    Tier.FREE: Limits(
        max_decisions=100,
        max_projects=1,
        llm_extraction=False,  # Pattern-only for free tier
        corrections=True,  # Allow corrections to build habit
        api_access=False,  # MCP only, no REST APIs
        web_ui=True  # Basic dashboard access
    ),
    Tier.TEAM: Limits(
        max_decisions=-1,  # Unlimited
        max_projects=5,
        llm_extraction=True,
        corrections=True,
        api_access=True,  # Full API access
        web_ui=True
    ),
    Tier.BUSINESS: Limits(
        max_decisions=-1,
        max_projects=-1,
        llm_extraction=True,
        corrections=True,
        api_access=True,
        web_ui=True
    )
}


@dataclass
class LicenseInfo:
    """License information."""
    tier: Tier
    email: str
    expires_at: datetime


@dataclass
class LimitViolation:
    """Represents a tier limit violation."""
    type: str  # "decisions", "projects"
    current: int
    limit: int
    message: str


def validate_license_key(key: str) -> Optional[LicenseInfo]:
    """
    Validate a license key.

    Args:
        key: Base64-encoded license key

    Returns:
        LicenseInfo if valid, None if invalid

    Note:
        For MVP, this is a basic implementation.
        Production would use proper cryptographic signing.
    """
    try:
        # Decode key
        decoded = base64.b64decode(key)
        payload = json.loads(decoded)

        # Check required fields
        if not all(k in payload for k in ["tier", "email", "expires_at", "signature"]):
            return None

        # Verify signature (basic check for MVP)
        expected_sig = compute_signature(
            payload["tier"],
            payload["email"],
            payload["expires_at"]
        )
        if payload["signature"] != expected_sig:
            return None

        # Check expiry
        expires = datetime.fromisoformat(payload["expires_at"])
        if expires < datetime.now():
            return None

        return LicenseInfo(
            tier=Tier(payload["tier"]),
            email=payload["email"],
            expires_at=expires
        )

    except (json.JSONDecodeError, KeyError, ValueError, Exception):
        return None


def compute_signature(tier: str, email: str, expires_at: str) -> str:
    """
    Compute signature for license validation.

    Note:
        For MVP, using simple hash. Production should use
        proper HMAC or asymmetric signing.
    """
    # Get secret from environment (not stored in code)
    secret = os.environ.get("LATTICE_LICENSE_SECRET", "dev-secret-change-in-prod")

    data = f"{tier}:{email}:{expires_at}:{secret}"
    return hashlib.sha256(data.encode()).hexdigest()


def get_current_tier() -> Tier:
    """
    Get the current user's tier.

    Checks:
    1. Environment variable LATTICE_LICENSE_KEY
    2. Config file license_key
    3. Defaults to FREE

    Returns:
        Tier enum value
    """
    # Check environment variable first
    key = os.environ.get("LATTICE_LICENSE_KEY")
    if key:
        info = validate_license_key(key)
        if info:
            return info.tier

    # Check config file
    try:
        from pathlib import Path

        from lattice_context.core.config import LatticeConfig

        config_path = Path(".lattice/config.yml")
        if config_path.exists():
            config = LatticeConfig.load(Path("."))
            if config.license_key:
                info = validate_license_key(config.license_key)
                if info:
                    return info.tier
    except Exception:
        # If config loading fails, fall through to default
        pass

    # Default to free tier
    return Tier.FREE


def check_decision_limit(tier: Tier, current_count: int) -> Optional[LimitViolation]:
    """
    Check if decision count exceeds tier limit.

    Args:
        tier: User's tier
        current_count: Current number of decisions

    Returns:
        LimitViolation if limit exceeded, None if within limit
    """
    limits = TIER_LIMITS[tier]

    # -1 means unlimited
    if limits.max_decisions < 0:
        return None

    if current_count >= limits.max_decisions:
        return LimitViolation(
            type="decisions",
            current=current_count,
            limit=limits.max_decisions,
            message=f"Free tier limited to {limits.max_decisions} decisions. "
                   f"You have {current_count}. Upgrade to Team for unlimited."
        )

    return None


def check_project_limit(tier: Tier, current_count: int) -> Optional[LimitViolation]:
    """
    Check if project count exceeds tier limit.

    Args:
        tier: User's tier
        current_count: Current number of projects

    Returns:
        LimitViolation if limit exceeded, None if within limit
    """
    limits = TIER_LIMITS[tier]

    if limits.max_projects < 0:
        return None

    if current_count >= limits.max_projects:
        return LimitViolation(
            type="projects",
            current=current_count,
            limit=limits.max_projects,
            message=f"Free tier limited to {limits.max_projects} project. "
                   f"Upgrade to Team for 5 projects or Business for unlimited."
        )

    return None


def can_use_llm_extraction(tier: Tier) -> bool:
    """Check if tier allows LLM-based extraction."""
    return TIER_LIMITS[tier].llm_extraction


def can_use_corrections(tier: Tier) -> bool:
    """Check if tier allows corrections."""
    return TIER_LIMITS[tier].corrections


def can_use_api_access(tier: Tier) -> bool:
    """Check if tier allows REST API access (Copilot, Universal API)."""
    return TIER_LIMITS[tier].api_access


def can_use_web_ui(tier: Tier) -> bool:
    """Check if tier allows web dashboard."""
    return TIER_LIMITS[tier].web_ui


def get_limits_for_tier(tier: Tier) -> Limits:
    """Get limits configuration for a tier."""
    return TIER_LIMITS[tier]


def format_tier_info(tier: Tier) -> str:
    """Format tier information for display."""
    limits = TIER_LIMITS[tier]

    lines = [
        f"Current tier: {tier.value.upper()}",
        "",
        "Limits:",
    ]

    if limits.max_decisions < 0:
        lines.append("  • Decisions: Unlimited")
    else:
        lines.append(f"  • Decisions: {limits.max_decisions}")

    if limits.max_projects < 0:
        lines.append("  • Projects: Unlimited")
    else:
        lines.append(f"  • Projects: {limits.max_projects}")

    lines.append(f"  • LLM extraction: {'Yes' if limits.llm_extraction else 'No'}")
    lines.append(f"  • Corrections: {'Yes' if limits.corrections else 'No'}")
    lines.append(f"  • API access: {'Yes' if limits.api_access else 'No (MCP only)'}")
    lines.append(f"  • Web UI: {'Yes' if limits.web_ui else 'No'}")

    if tier == Tier.FREE:
        lines.extend([
            "",
            "Upgrade for:",
            "  • Unlimited decisions",
            "  • Multiple projects",
            "  • LLM-enhanced extraction",
            "  • REST API access (Copilot, Cursor, Windsurf)",
            "",
            "Run 'lattice upgrade' for more info"
        ])

    return "\n".join(lines)


def get_usage_stats(tier: Tier, decision_count: int, project_count: int = 1) -> dict:
    """
    Get usage statistics for current tier.

    Args:
        tier: Current tier
        decision_count: Number of decisions indexed
        project_count: Number of projects indexed

    Returns:
        Dictionary with usage statistics
    """
    limits = TIER_LIMITS[tier]

    return {
        "tier": tier.value,
        "decisions": {
            "current": decision_count,
            "limit": limits.max_decisions,
            "unlimited": limits.max_decisions < 0,
            "percent_used": (
                0 if limits.max_decisions < 0
                else min(100, int((decision_count / limits.max_decisions) * 100))
            ),
        },
        "projects": {
            "current": project_count,
            "limit": limits.max_projects,
            "unlimited": limits.max_projects < 0,
        },
        "features": {
            "llm_extraction": limits.llm_extraction,
            "api_access": limits.api_access,
            "corrections": limits.corrections,
            "web_ui": limits.web_ui,
        },
    }


def should_show_upgrade_prompt(tier: Tier, decision_count: int) -> bool:
    """Check if upgrade prompt should be shown (approaching limits)."""
    if tier != Tier.FREE:
        return False

    limits = TIER_LIMITS[tier]
    if limits.max_decisions < 0:
        return False

    # Show upgrade prompt at 80% of limit
    threshold = int(limits.max_decisions * 0.8)
    return decision_count >= threshold


def generate_license_key(
    email: str,
    tier: Tier,
    organization: str = "",
    valid_days: int = 365,
) -> str:
    """Generate a license key (for testing/admin use).

    Args:
        email: User email
        tier: Tier level
        organization: Organization name (optional)
        valid_days: Number of days until expiration

    Returns:
        Base64-encoded license key

    Note:
        In production, this would be done server-side.
        This is for testing and admin tools only.
    """
    now = datetime.now()
    expires_at = now + timedelta(days=valid_days)

    # Build data dict
    data = {
        "email": email,
        "tier": tier.value,
        "organization": organization,
        "issued_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
    }

    # Compute signature
    signature = compute_signature(tier.value, email, data["expires_at"])

    # Build payload
    payload = {
        "signature": signature,
        "tier": tier.value,
        "email": email,
        "expires_at": data["expires_at"],
    }

    # Encode as base64
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()
    return encoded
