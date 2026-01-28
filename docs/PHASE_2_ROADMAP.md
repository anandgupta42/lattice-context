# Phase 2 Roadmap - Team Collaboration & Advanced Features

**Date**: 2026-01-28
**Based on**: RESEARCH_BASED_ROADMAP.md
**Status**: Ready to implement
**Version**: v0.2.0

---

## What's Already Built (v0.1.0) ✅

From the research roadmap, these are COMPLETE:

1. ✅ **Enhanced Search & Discovery** (Phase 1.1) - FTS5 search, list commands, export
2. ✅ **Decision Graph Visualization** (Phase 1.2) - D3.js force-directed graph in web UI
3. ✅ **GitHub Copilot Integration** (Phase 1.3) - REST API with 6 endpoints
4. ✅ **Context API for All Tools** (Phase 3.2) - Universal API for Cursor, Windsurf, VS Code

**Conclusion**: We've already built most of Phase 1 and Phase 3!

---

## Phase 2 Focus: Team Collaboration Features

Based on research showing:
- **70% of organizations** face knowledge loss from turnover
- **30-45% annual turnover** in data teams
- **80% of processes undocumented**

### Feature 1: Team Workspace (HIGH PRIORITY)

**Problem**: Knowledge leaves with employees, no collaborative knowledge building

**Solution**: Collaborative decision management

**Features**:
```
1. Comments on decisions
   - Add context or corrections
   - @mention team members
   - Thread conversations

2. Voting system
   - Upvote/downvote decisions
   - Mark as "verified" or "outdated"
   - Filter by score

3. Contributors tracking
   - Who added/edited decisions
   - Activity feed
   - Attribution

4. Shared corrections
   - Team-wide corrections
   - Approval workflow
   - Version history
```

**Implementation Plan**:

**Database Schema** (add to database.py):
```sql
CREATE TABLE decision_comments (
    id TEXT PRIMARY KEY,
    decision_id TEXT NOT NULL,
    author TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    parent_id TEXT,  -- for threading
    FOREIGN KEY (decision_id) REFERENCES decisions(id)
);

CREATE TABLE decision_votes (
    decision_id TEXT NOT NULL,
    user_email TEXT NOT NULL,
    vote INTEGER NOT NULL,  -- 1 for upvote, -1 for downvote
    created_at TIMESTAMP NOT NULL,
    PRIMARY KEY (decision_id, user_email)
);

CREATE TABLE decision_metadata (
    decision_id TEXT PRIMARY KEY,
    status TEXT,  -- 'active', 'outdated', 'verified'
    last_verified_at TIMESTAMP,
    last_verified_by TEXT
);
```

**API Endpoints** (add to web/api.py):
```python
@app.post("/api/decisions/{decision_id}/comments")
async def add_comment(decision_id: str, comment: CommentCreate):
    """Add comment to a decision."""
    pass

@app.get("/api/decisions/{decision_id}/comments")
async def get_comments(decision_id: str):
    """Get all comments for a decision."""
    pass

@app.post("/api/decisions/{decision_id}/vote")
async def vote_decision(decision_id: str, vote: VoteCreate):
    """Upvote or downvote a decision."""
    pass

@app.get("/api/decisions/{decision_id}/score")
async def get_score(decision_id: str):
    """Get vote score for a decision."""
    pass

@app.post("/api/decisions/{decision_id}/verify")
async def verify_decision(decision_id: str, user: str):
    """Mark decision as verified by user."""
    pass
```

**CLI Commands** (new file: cli/team_cmd.py):
```bash
lattice team comment <decision_id> "This is still accurate"
lattice team vote <decision_id> up
lattice team verify <decision_id>
lattice team activity  # Show recent team activity
```

**UI Enhancements** (web dashboard):
```
Decision Card:
┌─────────────────────────────────────────────┐
│ ⬆ 5 ⬇ 0  Revenue Calculation               │
│ ✓ Verified by maya@company.com             │
│                                             │
│ Revenue excludes refunds per accounting.   │
│                                             │
│ 💬 2 comments                               │
│ └─ james@co: "Updated last quarter"        │
│ └─ sarah@co: "Applies to all regions"      │
│                                             │
│ [Add Comment] [Upvote] [Verify]            │
└─────────────────────────────────────────────┘
```

**Effort**: 2 weeks
**Value**: HIGH - Solves knowledge loss problem

---

### Feature 2: Change Notifications (MEDIUM PRIORITY)

**Problem**: Teams can't track changes, miss important updates

**Solution**: Real-time notifications for decision changes

**Features**:
```
1. Slack integration
   - New decisions extracted
   - Corrections added
   - Comments posted
   - Weekly digest

2. Email notifications
   - Daily summary
   - @mention alerts
   - Decision updates

3. Webhook support
   - Custom integrations
   - MS Teams, Discord
   - Generic webhooks
```

**Implementation Plan**:

**Configuration** (add to config.py):
```python
class NotificationSettings(BaseModel):
    slack_webhook: Optional[str] = None
    slack_channel: str = "#data-eng"
    email_enabled: bool = False
    email_recipients: list[str] = []
    webhook_url: Optional[str] = None
```

**Notification Service** (new file: core/notifications.py):
```python
class NotificationService:
    async def notify_new_decision(self, decision: Decision):
        """Send notification for new decision."""
        if config.slack_webhook:
            await self._send_slack(
                f"📊 New decision: {decision.why}",
                decision
            )

    async def notify_comment(self, comment: Comment):
        """Send notification for new comment."""
        pass

    async def send_weekly_digest(self):
        """Send weekly summary of activity."""
        pass
```

**CLI Commands**:
```bash
lattice notifications enable --slack-webhook=https://...
lattice notifications test
lattice notifications digest  # Manual trigger
```

**Effort**: 1 week
**Value**: MEDIUM - Improves team awareness

---

### Feature 3: Multi-Repository Support (HIGH PRIORITY - Enterprise)

**Problem**: Enterprises have multiple dbt projects, need unified view

**Solution**: Index and search across multiple repositories

**Features**:
```
1. Multi-repo indexing
   - Configure multiple projects
   - Index all repos
   - Unified search

2. Cross-repo conventions
   - Detect shared patterns
   - Highlight differences
   - Suggest standardization

3. Repository filtering
   - Search within specific repo
   - Compare conventions across repos
   - Per-repo statistics
```

**Implementation Plan**:

**Database Schema**:
```sql
CREATE TABLE repositories (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    url TEXT,
    indexed_at TIMESTAMP,
    decision_count INTEGER DEFAULT 0
);

-- Add repository_id to existing tables
ALTER TABLE decisions ADD COLUMN repository_id TEXT;
ALTER TABLE conventions ADD COLUMN repository_id TEXT;
ALTER TABLE corrections ADD COLUMN repository_id TEXT;
```

**Configuration** (update config.py):
```python
class LatticeConfig(BaseModel):
    repositories: list[RepositoryConfig] = []

class RepositoryConfig(BaseModel):
    name: str
    path: Path
    enabled: bool = True
```

**CLI Commands**:
```bash
lattice repo add --name="core" --path="../dbt-core"
lattice repo list
lattice index --repo="core"
lattice search "revenue" --repo="core"
lattice repo sync  # Sync all repos
```

**MCP Tool Update**:
```python
@server.tool()
async def get_context(query: str, repository: Optional[str] = None):
    """Get context, optionally filtered by repository."""
    if repository:
        return await retrieval.get_context_for_repo(query, repository)
    return await retrieval.get_context(query)
```

**Effort**: 2 weeks
**Value**: HIGH - Critical for enterprise sales

---

### Feature 4: LLM-Enhanced Extraction (MEDIUM PRIORITY - Paid Feature)

**Problem**: Pattern-based extraction misses nuanced decisions

**Solution**: Use Claude API to extract complex decisions

**Features**:
```
1. Smart commit analysis
   - Understand intent from diffs
   - Summarize long commits
   - Extract implicit decisions

2. Convention inference
   - Detect unwritten rules
   - Suggest conventions
   - Validate consistency

3. Quality scoring
   - Confidence scores
   - Manual review queue
   - Training data collection
```

**Implementation Plan**:

**Extractor Enhancement** (update git_extractor.py):
```python
class EnhancedGitExtractor:
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client
        self.pattern_extractor = PatternBasedExtractor()

    async def extract_decision(self, commit: Commit) -> Decision:
        # Try pattern-based first
        decision = self.pattern_extractor.extract(commit)

        # Enhance with LLM if available
        if self.llm_client and self._is_complex(commit):
            enhanced = await self._llm_extract(commit)
            decision = self._merge(decision, enhanced)

        return decision

    async def _llm_extract(self, commit: Commit) -> Decision:
        prompt = f"""
        Analyze this git commit and extract the key business decision:

        Message: {commit.message}
        Changed files: {commit.files}
        Diff summary: {commit.diff[:500]}

        Focus on:
        1. WHY this change was made
        2. What business rule or convention it represents
        3. What entity it affects

        Return JSON:
        {{
            "why": "business reason",
            "entity": "affected model/table",
            "confidence": 0.0-1.0
        }}
        """
        return await self.llm_client.complete(prompt)
```

**Configuration**:
```python
class ExtractionConfig(BaseModel):
    use_llm: bool = False  # Requires TEAM tier
    llm_provider: str = "anthropic"
    llm_model: str = "claude-sonnet-4.5"
    confidence_threshold: float = 0.7
```

**CLI Commands**:
```bash
lattice index --llm  # Use LLM enhancement
lattice extract review  # Review low-confidence extractions
```

**Monetization**:
- FREE tier: Pattern-based only
- TEAM tier: LLM-enhanced extraction
- BUSINESS tier: Unlimited LLM calls

**Effort**: 2 weeks
**Value**: MEDIUM - Improves quality, monetization opportunity

---

## Build Priority Order

### Sprint 1 (Weeks 1-2): Team Workspace Foundation
- [ ] Database schema for comments, votes, metadata
- [ ] API endpoints for team features
- [ ] CLI commands: comment, vote, verify
- [ ] UI: comment threads on decision cards
- [ ] UI: vote buttons and scores
- [ ] Testing: 10+ tests for team features

**Deliverable**: Team can comment and vote on decisions

### Sprint 2 (Weeks 3-4): Multi-Repository Support
- [ ] Repository management in database
- [ ] CLI: repo add, list, sync
- [ ] Update indexing to handle multiple repos
- [ ] Update search to filter by repo
- [ ] MCP: add repository parameter
- [ ] UI: repository selector
- [ ] Testing: multi-repo test suite

**Deliverable**: Users can index and search multiple projects

### Sprint 3 (Weeks 5-6): Notifications & LLM Enhancement
- [ ] Notification service foundation
- [ ] Slack webhook integration
- [ ] Email notification system
- [ ] CLI: notification configuration
- [ ] LLM-enhanced extraction (optional)
- [ ] Quality scoring system
- [ ] Testing: notification delivery tests

**Deliverable**: Teams get notified of changes, LLM extraction available

---

## Success Metrics (v0.2.0)

### Usage Metrics
- **Comments**: 50+ comments within first month
- **Votes**: 200+ votes on decisions
- **Multi-repo users**: 10+ teams with 3+ repos
- **Notifications**: 1,000+ Slack messages sent
- **LLM extractions**: 500+ enhanced decisions

### Business Metrics
- **Team tier conversions**: 20+ teams ($1,000 MRR)
- **Enterprise tier**: 5+ companies ($2,500 MRR)
- **Churn rate**: <5%
- **NPS**: 50+

### Quality Metrics
- **Decision accuracy**: 90%+ (with LLM)
- **User satisfaction**: 4.5/5 stars
- **Support tickets**: <10/month
- **Uptime**: 99.9%

---

## Release Plan

### v0.2.0-beta (Week 2)
- Team workspace features
- Limited beta: 20 users
- Feedback collection

### v0.2.0-rc (Week 4)
- Multi-repo support
- Wider beta: 100 users
- Performance testing

### v0.2.0 (Week 6)
- Notifications + LLM
- Public release
- Marketing campaign
- Documentation update

---

## Documentation Updates Needed

### User Documentation
- [ ] Update README with team features
- [ ] Update QUICKSTART with multi-repo setup
- [ ] Add TEAM_COLLABORATION.md guide
- [ ] Update FEATURES.md with new capabilities

### Technical Documentation
- [ ] API reference for team endpoints
- [ ] Multi-repo configuration guide
- [ ] Notification setup guide
- [ ] LLM extraction documentation

### Integration Guides
- [ ] Slack integration setup
- [ ] Multi-repo GitHub Actions
- [ ] Enterprise deployment guide

---

## Migration Path from v0.1.0

### Database Migrations
```sql
-- Add new tables
CREATE TABLE IF NOT EXISTS decision_comments (...);
CREATE TABLE IF NOT EXISTS decision_votes (...);
CREATE TABLE IF NOT EXISTS repositories (...);

-- Add columns to existing tables
ALTER TABLE decisions ADD COLUMN IF NOT EXISTS repository_id TEXT;
ALTER TABLE decisions ADD COLUMN IF NOT EXISTS vote_score INTEGER DEFAULT 0;
```

### Config Migration
```python
# Old config
{
    "project_path": "/path/to/project"
}

# New config (auto-migrates)
{
    "repositories": [
        {
            "name": "main",
            "path": "/path/to/project",
            "enabled": true
        }
    ]
}
```

### Breaking Changes
- None! All changes are additive
- v0.1.0 projects work without changes
- New features opt-in

---

## Risk Assessment

### Technical Risks
- **Multi-repo complexity**: MEDIUM
  - Mitigation: Start with simple implementation
  - Fallback: Per-repo instances

- **Notification reliability**: LOW
  - Mitigation: Queue-based delivery
  - Fallback: Manual polling

- **LLM costs**: MEDIUM
  - Mitigation: Tier-based limits
  - Fallback: Pattern-only mode

### Business Risks
- **Feature bloat**: LOW
  - Mitigation: Research-driven priorities
  - Validation: User interviews

- **Adoption rate**: MEDIUM
  - Mitigation: Free tier unchanged
  - Growth: Team features drive upgrades

---

## Next Steps

**Immediate (Today)**:
1. Create Sprint 1 tasks in GitHub Projects
2. Set up development branch: `feature/team-workspace`
3. Begin database schema design

**Week 1**:
1. Implement team workspace database
2. Build API endpoints
3. Start CLI commands

**Week 2**:
1. Complete team workspace
2. Build UI components
3. Write tests
4. Beta release

---

**Ready to start Sprint 1: Team Workspace Foundation**

**Estimated Timeline**: 6 weeks to v0.2.0 release
**Estimated Impact**: 3x user value, 5x enterprise readiness
**Estimated Revenue**: $3,500+ MRR

Let's build! 🚀
