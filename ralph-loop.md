# Lattice Context Layer - Ralph Loop Implementation Prompt

> **Mission**: Build a production-ready context layer for data teams that delivers value in under 5 minutes.
>
> **Stack**: Python (FastAPI) + React + SQLite
>
> **Philosophy**: Ship like a 100-person team. Every feature must answer: "Would a user pay for this?"

---

## EXIT CRITERIA (Loop Stops When ALL Are True)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         EXIT CRITERIA CHECKLIST                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  □ 1. USER CAN GET VALUE IN <5 MINUTES                                  │
│     - `pip install lattice-context && lattice init && lattice serve`    │
│     - Claude Desktop shows context on first query                        │
│     - No configuration required for basic dbt project                    │
│                                                                          │
│  □ 2. CORE FLOW WORKS END-TO-END                                        │
│     - Indexing: dbt manifest → decisions extracted                       │
│     - Retrieval: AI asks → relevant context returned                     │
│     - Corrections: User adds → AI learns                                 │
│                                                                          │
│  □ 3. PRODUCTION QUALITY                                                │
│     - All tests pass (>90% coverage on core paths)                      │
│     - No TypeErrors, no unhandled exceptions                            │
│     - Graceful degradation (works without LLM API key)                  │
│     - <500ms response time for MCP queries                              │
│                                                                          │
│  □ 4. SHIPPABLE ARTIFACTS                                               │
│     - PyPI package published and installable                            │
│     - Docker image builds and runs                                      │
│     - README with 60-second quickstart                                  │
│     - Landing page with clear value prop                                │
│                                                                          │
│  □ 5. MONETIZATION READY                                                │
│     - Free tier limits enforced (100 decisions)                         │
│     - License key validation for paid tiers                             │
│     - Usage tracking for billing                                        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## CORE PRINCIPLES (Read Before Every Phase)

### 1. Time-to-Value is Everything

**Bad**: User runs 5 commands, edits config, waits 10 minutes, still doesn't see value.
**Good**: User runs 1 command, sees "Found 47 models, extracted 123 decisions" in 30 seconds.

**Test yourself**: Can a new user:
- Install in 30 seconds?
- See first result in 60 seconds?
- Understand the value in 5 minutes?

### 2. Build for the User, Not the Spec

**The spec is a guide, not a mandate.**

Before building any feature, ask:
- Does Maya (Analytics Engineer) need this TODAY?
- Would James (Data Team Lead) pay $50/month for this?
- Does this solve a real problem or is it "nice to have"?

**Kill features that don't pass this test.**

### 3. Production Quality from Day 1

**Every commit should be shippable.**

- No "TODO: fix later" in production paths
- No hardcoded secrets or paths
- Error messages should help users fix issues
- Logs should tell a story

### 4. Critical Self-Review

After each phase, ask:
- Would I pay for this?
- Would I recommend this to a friend?
- What's embarrassing about this?
- What would a competitor mock?

---

## USER PERSONAS (Reference Constantly)

### Maya - Analytics Engineer (Primary)

**Context**: 3 years experience, uses dbt daily, trying AI assistants for the first time.

**Pain**: "Every time I ask Claude to help write a model, I have to explain our naming conventions, why we join on customer_key not customer_id, and what 'revenue' actually means. It's exhausting."

**Success for Maya**:
1. Installs Lattice in her dbt project
2. Connects to Claude Desktop
3. Asks Claude to "add a discount column to orders"
4. Claude automatically knows to use `discount_amount` (her team's convention) and warns about the refund exclusion rule

**What Maya will NOT tolerate**:
- Complex setup (>5 minutes)
- Requiring her to document things manually
- Breaking her existing workflow
- Slow responses (>2 seconds)

### James - Data Team Lead (Secondary)

**Context**: 8 years experience, manages 6 analytics engineers, worried about knowledge loss.

**Pain**: "Sarah left last month after 5 years. Half our institutional knowledge walked out the door. The new hire keeps asking questions nobody can answer."

**Success for James**:
1. Sees Lattice capturing decisions from git history
2. New hire asks "why is dim_customer built this way?"
3. Claude gives the actual historical context
4. James doesn't have to answer the same question for the 10th time

**What James will pay for**:
- Reduced onboarding time (measurable)
- Knowledge preservation (peace of mind)
- Team-wide consistency

---

## PHASE 1: THE 5-MINUTE MIRACLE

**Goal**: User installs, runs, sees value in 5 minutes. Nothing else matters.

**Exit Criteria for Phase 1**:
```
□ pip install lattice-context works
□ lattice init auto-detects dbt project (no config required)
□ lattice index completes in <30 seconds for 100-model project
□ lattice serve starts MCP server
□ Claude Desktop can call get_context and get a response
□ Response includes at least 1 useful piece of information
```

### Step 1.1: Project Scaffold

```
lattice-context/
├── pyproject.toml           # Package config (use Poetry or Hatch)
├── README.md                 # 60-second quickstart
├── LICENSE                   # MIT
├── .github/
│   └── workflows/
│       ├── test.yml          # CI on every PR
│       └── publish.yml       # Publish to PyPI on release
├── src/
│   └── lattice_context/
│       ├── __init__.py
│       ├── __main__.py       # Entry point
│       ├── cli/              # CLI commands
│       ├── core/             # Business logic
│       ├── extractors/       # Tool-specific extractors
│       ├── storage/          # SQLite layer
│       ├── mcp/              # MCP server
│       └── api/              # FastAPI (optional, for UI)
├── ui/                       # React dashboard (Phase 3)
├── tests/
└── docker/
```

**Critical decisions**:
- Use `typer` for CLI (better than argparse, familiar to Python devs)
- Use `sqlite3` (stdlib) not SQLAlchemy (faster startup, less deps)
- Use `httpx` for async HTTP
- Bundle `mcp` SDK properly

### Step 1.2: Zero-Config Detection

**The init command should "just work":**

```python
# src/lattice_context/cli/init.py

def detect_project_type(path: Path) -> ProjectType | None:
    """Auto-detect project type. User should never need to configure this."""

    # dbt detection (most common)
    if (path / "dbt_project.yml").exists():
        return ProjectType.DBT

    # SQLMesh detection
    if (path / "sqlmesh" / "config.py").exists():
        return ProjectType.SQLMESH

    # Airflow detection
    if (path / "dags").is_dir() or (path / "airflow.cfg").exists():
        return ProjectType.AIRFLOW

    return None

def find_manifest(path: Path) -> Path | None:
    """Find dbt manifest without user config."""
    candidates = [
        path / "target" / "manifest.json",
        path / "manifest.json",
        path / "dbt_packages" / "manifest.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None
```

**Test**: Run `lattice init` in 10 different dbt projects. It should work in 9/10 without any flags.

### Step 1.3: Fast Indexing

**Indexing must be FAST. Users won't wait.**

```python
# src/lattice_context/core/indexer.py

async def index_dbt_project(manifest_path: Path, db: Database) -> IndexResult:
    """Index a dbt project. Target: <30 seconds for 100 models."""

    start = time.time()

    # Step 1: Parse manifest (fast, <1 second)
    manifest = parse_manifest(manifest_path)

    # Step 2: Extract entities (fast, <2 seconds)
    entities = extract_entities(manifest)

    # Step 3: Detect conventions (fast, <1 second)
    conventions = detect_conventions(entities)

    # Step 4: Git history (slower, but bounded)
    # IMPORTANT: Limit to recent history on first run
    decisions = await extract_decisions_from_git(
        limit=500,  # Only last 500 commits
        timeout=20  # Max 20 seconds
    )

    # Step 5: Store (fast, <1 second)
    await db.store_index(entities, conventions, decisions)

    elapsed = time.time() - start

    return IndexResult(
        entities=len(entities),
        conventions=len(conventions),
        decisions=len(decisions),
        elapsed_seconds=elapsed
    )
```

**Critical**: First index should be FAST with limited depth. Full history can be indexed later as a background job.

### Step 1.4: MCP Server (Minimal Viable)

**Only implement 3 tools initially. More is NOT better.**

```python
# src/lattice_context/mcp/server.py

TOOLS = [
    # Tool 1: The main one - get context for a task
    Tool(
        name="get_context",
        description="Get relevant context for a data engineering task",
        inputSchema={
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "What you're trying to do (e.g., 'add revenue column to orders')"
                }
            },
            "required": ["task"]
        }
    ),

    # Tool 2: Add corrections (learning)
    Tool(
        name="add_correction",
        description="Teach me something about this project",
        inputSchema={
            "type": "object",
            "properties": {
                "entity": {"type": "string"},
                "correction": {"type": "string"}
            },
            "required": ["entity", "correction"]
        }
    ),

    # Tool 3: Explain an entity
    Tool(
        name="explain",
        description="Explain why something is built the way it is",
        inputSchema={
            "type": "object",
            "properties": {
                "entity": {"type": "string"}
            },
            "required": ["entity"]
        }
    )
]
```

**Why only 3?**
- `get_context` is 90% of the value
- `add_correction` enables learning
- `explain` handles direct questions

**Do NOT add**: search_decisions, get_conventions, list_corrections, get_file_history, etc. until users ASK for them.

### Step 1.5: The "Aha Moment" Response

**The first response MUST be impressive.**

When a user asks Claude "add a revenue column to orders" and Lattice responds, they should think "wow, it actually knows our project."

```python
def format_context_response(
    task: str,
    decisions: list[Decision],
    conventions: list[Convention],
    corrections: list[Correction]
) -> str:
    """Format context in a way that's immediately useful to an AI assistant."""

    sections = []

    # Section 1: Relevant decisions (the "why")
    if decisions:
        sections.append("## Relevant Decisions\n")
        for d in decisions[:5]:  # Max 5, don't overwhelm
            sections.append(f"- **{d.entity}**: {d.why}")
            if d.context:
                sections.append(f"  - Context: {d.context}")

    # Section 2: Conventions to follow
    if conventions:
        sections.append("\n## Conventions to Follow\n")
        for c in conventions[:3]:  # Max 3
            sections.append(f"- {c.description}")
            sections.append(f"  - Examples: {', '.join(c.examples[:3])}")

    # Section 3: Corrections (highest priority)
    if corrections:
        sections.append("\n## ⚠️ Important Notes\n")
        for c in corrections:
            sections.append(f"- **{c.entity}**: {c.correction}")

    # Section 4: Quick tip if nothing else
    if not any([decisions, conventions, corrections]):
        sections.append("No specific context found. Proceeding with general best practices.")

    return "\n".join(sections)
```

**Test this**: Show the response to 5 data engineers. If they don't say "that's useful", iterate.

### Step 1.6: README That Sells

```markdown
# Lattice Context Layer

> Give AI assistants the institutional knowledge they need to understand your dbt project.

## 60-Second Quickstart

```bash
# Install
pip install lattice-context

# Initialize in your dbt project
cd your-dbt-project
lattice init

# Start the MCP server
lattice serve
```

Then add to Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "lattice": {
      "command": "lattice",
      "args": ["serve"]
    }
  }
}
```

Restart Claude Desktop. Ask it to help with your dbt models. It now knows your conventions.

## What It Does

Lattice automatically extracts:
- **Decisions** from your git history ("why was this column added?")
- **Conventions** from your code patterns ("columns ending in _at are timestamps")
- **Corrections** you teach it ("revenue always excludes refunds")

And serves them to AI assistants via MCP.

## Example

Before Lattice:
> You: "Add a revenue column to orders"
> Claude: "Here's a revenue column..." (uses wrong naming, wrong calculation)

After Lattice:
> You: "Add a revenue column to orders"
> Claude: "Based on your project conventions, I'll name it `revenue_amount` (your pattern for money columns). Note: Your team excludes refunds from revenue calculations per the correction added on 2024-01-15."
```

**Test**: Can someone who's never seen Lattice understand the value in 30 seconds?

---

## PHASE 2: PRODUCTION HARDENING

**Goal**: Make it reliable enough that users trust it daily.

**Exit Criteria for Phase 2**:
```
□ Error handling covers all common failures
□ Graceful degradation without LLM API key
□ Logging tells a story (can debug user issues)
□ Rate limiting prevents abuse
□ <500ms P95 response time
□ Works offline (git extraction only)
```

### Step 2.1: Error Handling That Helps

```python
# src/lattice_context/core/errors.py

class LatticeError(Exception):
    """Base error with user-friendly message."""

    def __init__(self, message: str, hint: str | None = None):
        self.message = message
        self.hint = hint
        super().__init__(message)

    def __str__(self):
        if self.hint:
            return f"{self.message}\n\nHint: {self.hint}"
        return self.message


class ManifestNotFoundError(LatticeError):
    def __init__(self, searched_paths: list[Path]):
        super().__init__(
            message="Could not find dbt manifest.json",
            hint=f"Run 'dbt compile' first, or specify path with --manifest.\n"
                 f"Searched: {', '.join(str(p) for p in searched_paths)}"
        )


class GitNotFoundError(LatticeError):
    def __init__(self):
        super().__init__(
            message="Not a git repository",
            hint="Lattice needs git history to extract decisions. "
                 "Run 'git init' or use --no-git to skip."
        )
```

**Test**: Every error a user can encounter should have a helpful hint.

### Step 2.2: Graceful Degradation

```python
# src/lattice_context/core/extraction.py

async def extract_decisions(
    commits: list[Commit],
    llm_client: LLMClient | None = None
) -> list[Decision]:
    """Extract decisions. Works with or without LLM."""

    decisions = []

    for commit in commits:
        # Level 1: Pattern-based extraction (always works)
        pattern_decisions = extract_with_patterns(commit)
        decisions.extend(pattern_decisions)

        # Level 2: LLM enhancement (if available)
        if llm_client and is_complex_commit(commit):
            try:
                llm_decisions = await extract_with_llm(commit, llm_client)
                decisions.extend(llm_decisions)
            except LLMError:
                # Log but don't fail - pattern extraction is good enough
                logger.warning(f"LLM extraction failed for {commit.sha[:7]}, using patterns only")

    return deduplicate(decisions)
```

**Key insight**: Lattice should be USEFUL even without an LLM API key. Pattern-based extraction covers 70% of cases.

### Step 2.3: Logging for Debugging

```python
# src/lattice_context/core/logging.py

import structlog

logger = structlog.get_logger()

# Good logging tells a story
logger.info("indexing_started", project_type="dbt", path="/path/to/project")
logger.info("manifest_parsed", models=142, sources=12, tests=89)
logger.info("git_analysis_started", commit_limit=500)
logger.info("decisions_extracted", count=47, from_patterns=35, from_llm=12)
logger.info("conventions_detected", count=8)
logger.info("indexing_complete", elapsed_seconds=12.3)

# When user reports issue, these logs should tell us exactly what happened
```

### Step 2.4: Performance Budget

```python
# src/lattice_context/mcp/handlers.py

import time
from functools import wraps

def with_timing(budget_ms: int):
    """Decorator to enforce performance budget."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            result = await func(*args, **kwargs)
            elapsed_ms = (time.time() - start) * 1000

            if elapsed_ms > budget_ms:
                logger.warning(
                    "performance_budget_exceeded",
                    function=func.__name__,
                    budget_ms=budget_ms,
                    actual_ms=elapsed_ms
                )

            return result
        return wrapper
    return decorator


@with_timing(budget_ms=500)
async def handle_get_context(request: GetContextRequest) -> GetContextResponse:
    """Get context. Budget: 500ms."""
    # ... implementation
```

---

## PHASE 3: USER DASHBOARD

**Goal**: Give users visibility into what Lattice knows.

**Exit Criteria for Phase 3**:
```
□ Dashboard accessible at localhost:3000 when running `lattice serve`
□ Shows: decisions, conventions, corrections
□ Can add/edit corrections from UI
□ Can trigger re-index from UI
□ Looks professional (not a prototype)
```

### Critical Question: Do Users Need a Dashboard?

**Before building, validate**:
- Can Maya do everything she needs from CLI + MCP?
- Does James need a dashboard to get value?

**The answer**: Yes, but minimal.

**Dashboard MVP**:
1. **Status page**: Is Lattice running? When was last index?
2. **Decisions list**: What does Lattice know?
3. **Corrections editor**: Add/edit corrections without CLI
4. **Onboarding wizard**: First-time setup

**Do NOT build**:
- Complex search/filter UI
- Charts/analytics
- User management
- Settings pages with 50 options

### Step 3.1: React Dashboard (Minimal)

```
ui/
├── package.json
├── vite.config.ts
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── api/            # API client
│   ├── components/
│   │   ├── StatusCard.tsx
│   │   ├── DecisionsList.tsx
│   │   ├── CorrectionsEditor.tsx
│   │   └── OnboardingWizard.tsx
│   └── pages/
│       ├── Dashboard.tsx
│       └── Onboarding.tsx
```

**Design principles**:
- Use shadcn/ui or similar (don't build components from scratch)
- Max 3 pages
- Mobile-responsive (data engineers use laptops with small screens)
- Dark mode only (developers prefer it)

### Step 3.2: FastAPI Backend

```python
# src/lattice_context/api/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Lattice Context Layer")

# Health check
@app.get("/api/health")
async def health():
    return {"status": "ok"}

# Status
@app.get("/api/status")
async def get_status(db: Database = Depends(get_db)):
    return {
        "indexed": db.is_indexed(),
        "last_indexed": db.last_indexed_at(),
        "stats": {
            "entities": db.count_entities(),
            "decisions": db.count_decisions(),
            "conventions": db.count_conventions(),
            "corrections": db.count_corrections()
        }
    }

# Decisions (read-only)
@app.get("/api/decisions")
async def list_decisions(
    limit: int = 50,
    offset: int = 0,
    db: Database = Depends(get_db)
):
    return db.list_decisions(limit=limit, offset=offset)

# Corrections (CRUD)
@app.get("/api/corrections")
async def list_corrections(db: Database = Depends(get_db)):
    return db.list_corrections()

@app.post("/api/corrections")
async def add_correction(correction: CorrectionCreate, db: Database = Depends(get_db)):
    return db.add_correction(correction)

@app.delete("/api/corrections/{id}")
async def delete_correction(id: str, db: Database = Depends(get_db)):
    return db.delete_correction(id)

# Trigger re-index
@app.post("/api/index")
async def trigger_index(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_index)
    return {"status": "indexing_started"}

# Serve React app
app.mount("/", StaticFiles(directory="ui/dist", html=True), name="ui")
```

---

## PHASE 4: MONETIZATION

**Goal**: Enable users to pay for Lattice.

**Exit Criteria for Phase 4**:
```
□ Free tier: 100 decisions, 1 project, basic features
□ Paid tier: Unlimited, multiple projects, all features
□ License key validation works
□ Upgrade flow is smooth
□ Usage tracking for billing
```

### Step 4.1: Tier Enforcement

```python
# src/lattice_context/core/licensing.py

from enum import Enum
from dataclasses import dataclass

class Tier(Enum):
    FREE = "free"
    TEAM = "team"
    BUSINESS = "business"

@dataclass
class Limits:
    max_decisions: int
    max_projects: int
    llm_extraction: bool
    corrections: bool

TIER_LIMITS = {
    Tier.FREE: Limits(
        max_decisions=100,
        max_projects=1,
        llm_extraction=False,  # Pattern-only for free
        corrections=True  # Let them correct, builds habit
    ),
    Tier.TEAM: Limits(
        max_decisions=-1,  # Unlimited
        max_projects=5,
        llm_extraction=True,
        corrections=True
    ),
    Tier.BUSINESS: Limits(
        max_decisions=-1,
        max_projects=-1,
        llm_extraction=True,
        corrections=True
    )
}


def check_limits(tier: Tier, db: Database) -> list[LimitViolation]:
    """Check if user is within their tier limits."""
    limits = TIER_LIMITS[tier]
    violations = []

    if limits.max_decisions > 0:
        count = db.count_decisions()
        if count >= limits.max_decisions:
            violations.append(LimitViolation(
                type="decisions",
                current=count,
                limit=limits.max_decisions,
                message=f"Free tier limited to {limits.max_decisions} decisions. "
                        f"Upgrade to Team for unlimited."
            ))

    return violations
```

### Step 4.2: License Key Validation

```python
# src/lattice_context/core/licensing.py

import hashlib
import base64
from datetime import datetime

def validate_license_key(key: str) -> LicenseInfo | None:
    """Validate license key. Returns None if invalid."""

    try:
        # Decode key
        decoded = base64.b64decode(key)
        payload = json.loads(decoded)

        # Check signature
        expected_sig = compute_signature(payload['data'], SECRET_KEY)
        if payload['signature'] != expected_sig:
            return None

        # Check expiry
        if datetime.fromisoformat(payload['data']['expires_at']) < datetime.now():
            return None

        return LicenseInfo(
            tier=Tier(payload['data']['tier']),
            email=payload['data']['email'],
            expires_at=datetime.fromisoformat(payload['data']['expires_at'])
        )

    except Exception:
        return None


def get_current_tier() -> Tier:
    """Get current tier from config or environment."""

    # Check environment variable first
    key = os.environ.get("LATTICE_LICENSE_KEY")
    if key:
        info = validate_license_key(key)
        if info:
            return info.tier

    # Check config file
    config = load_config()
    if config.license_key:
        info = validate_license_key(config.license_key)
        if info:
            return info.tier

    return Tier.FREE
```

### Step 4.3: Upgrade Flow

```python
# In CLI
@app.command()
def upgrade():
    """Open upgrade page."""
    tier = get_current_tier()

    if tier != Tier.FREE:
        console.print(f"You're already on the {tier.value} tier!")
        return

    console.print("Opening upgrade page...")
    webbrowser.open("https://lattice.dev/upgrade")


# In dashboard
# Show upgrade banner when approaching limits
def UpgradeBanner({ decisions, limit }) {
    const percent = (decisions / limit) * 100;

    if (percent < 80) return null;

    return (
        <div className="bg-yellow-900 p-4 rounded">
            <p>You've used {decisions} of {limit} decisions.</p>
            <a href="https://lattice.dev/upgrade" className="text-blue-400">
                Upgrade to Team for unlimited →
            </a>
        </div>
    );
}
```

---

## PHASE 5: SHIPPING

**Goal**: Package and release.

**Exit Criteria for Phase 5**:
```
□ PyPI package installable: pip install lattice-context
□ Docker image: docker run lattice-context
□ GitHub releases with changelog
□ Documentation site live
□ Landing page live
```

### Step 5.1: PyPI Publishing

```toml
# pyproject.toml
[project]
name = "lattice-context"
version = "0.1.0"
description = "Context layer for AI-assisted data engineering"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [
    {name = "Altimate AI", email = "hello@altimate.ai"}
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "typer>=0.9.0",
    "rich>=13.0.0",
    "httpx>=0.25.0",
    "pydantic>=2.0.0",
    "mcp>=0.1.0",
]

[project.optional-dependencies]
llm = ["anthropic>=0.18.0"]
dev = ["pytest>=7.0.0", "pytest-asyncio>=0.21.0", "ruff>=0.1.0"]

[project.scripts]
lattice = "lattice_context.cli:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Step 5.2: Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy source
COPY src/ src/
COPY ui/dist/ ui/dist/

# Expose ports
EXPOSE 3000

# Run
CMD ["lattice", "serve", "--host", "0.0.0.0", "--port", "3000"]
```

### Step 5.3: GitHub Actions

```yaml
# .github/workflows/publish.yml
name: Publish

on:
  release:
    types: [published]

jobs:
  pypi:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install build twine
      - run: python -m build
      - run: twine upload dist/*
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}

  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: altimateai/lattice-context:${{ github.ref_name }}
```

---

## QUALITY GATES (Check After Each Phase)

### Gate 1: The "Would I Use This?" Test

Ask yourself honestly:
- If I were Maya, would I install this?
- If I were James, would I pay for this?
- Is there anything embarrassing about this?

### Gate 2: The "Demo Test"

Can you demo the entire flow in 5 minutes without:
- Apologizing for anything
- Saying "ignore that error"
- Explaining workarounds

### Gate 3: The "Competitor Test"

If a competitor saw this, would they:
- Be worried?
- Laugh?
- Copy it?

### Gate 4: The "Support Test"

If 100 users installed this today, how many would:
- Give up during setup?
- File a bug report?
- Tweet something negative?

Target: <10% for each.

---

## ANTI-PATTERNS TO AVOID

### 1. Feature Creep

❌ "Let's also add warehouse integration"
✅ "Is the dbt experience perfect first?"

### 2. Premature Abstraction

❌ "We need a plugin system for different extractors"
✅ "Just hardcode dbt support. Add plugins when we have 3+ tools."

### 3. Over-Engineering

❌ "Let's use Postgres for better scalability"
✅ "SQLite handles 1M decisions. We don't have 1M decisions."

### 4. Perfectionism

❌ "The LLM extraction isn't perfect"
✅ "80% accuracy with patterns is good enough for MVP"

### 5. Building Without Validation

❌ "Users will love the search feature"
✅ "Did 3 users ask for search? No? Don't build it."

---

## DAILY CHECKLIST

At the end of each work session, verify:

```
□ All tests pass
□ No new TODOs in production code
□ README is up-to-date
□ Can install fresh and see value in 5 minutes
□ No regressions in core flow
□ Commit messages are meaningful
```

---

## FINAL DELIVERABLES

When the loop exits, you should have:

1. **Working Product**
   - `pip install lattice-context` works
   - 5-minute time-to-value achieved
   - Core flow (index → serve → query → correct) works

2. **Production Quality**
   - Tests pass, good coverage
   - Error handling is helpful
   - Performance is acceptable

3. **Shippable Artifacts**
   - PyPI package published
   - Docker image available
   - Documentation site live

4. **Monetization Ready**
   - Free tier limits enforced
   - License key validation works
   - Upgrade flow exists

5. **Marketing Ready**
   - Landing page with clear value prop
   - README that sells
   - Demo video or GIF

---

## REMEMBER

**The goal is not to build features. The goal is to solve Maya's problem.**

Every line of code should bring us closer to:
> "Every time I use Claude to help write a model, it just knows our conventions."

If it doesn't serve that goal, don't build it.

---

*This prompt should be fed to the Ralph Loop. It will continue iterating until all exit criteria are met.*
