# Lattice Context Layer

> Give AI assistants the institutional knowledge they need to understand your dbt project.

Lattice automatically extracts "why" decisions from your git history and dbt project, detects conventions, learns from your corrections, and serves them to AI assistants via MCP.

## The Problem

AI assistants like Claude can see *what* exists in your codebase, but not *why* it was built that way.

**Before Lattice:**
```
You: "Add a discount column to dim_customers"

Claude: "I'll add a discount_percent column to store discount percentages..."
  ❌ Wrong name (should be discount_amount)
  ❌ Wrong type (should be absolute amounts, not percentages)
  ❌ Might duplicate existing discount_amount column
```

**After Lattice:**
```
You: "Add a discount column to dim_customers"

Claude responds with Lattice context:
  ⚠️ Important Notes
  • discount_amount: Always use positive values. Discounts are stored
    as absolute amounts, not percentages

  📚 Relevant Decisions
  • dim_customers: Customer dimension with lifetime metrics

  ✓ I see discount_amount already exists with specific requirements.
    Would you like to modify it or are you looking for something else?
```

## 60-Second Quickstart

```bash
# 1. Install
pip install lattice-context

# 2. Initialize in your dbt project
cd your-dbt-project
lattice init

# 3. Index your project (extracts decisions and conventions)
lattice index

# 4. Start the MCP server
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

Restart Claude Desktop. Now when you ask it to help with your dbt models, it knows your conventions and past decisions.

## What Lattice Extracts

### 1. Decisions from Git History
```
Commit: "Switch to customer_key for joins after CRM migration"
  → Lattice extracts: "Use customer_key not customer_id for dim_customer joins"
```

### 2. Conventions from Patterns
```
Models: dim_customer, dim_product, dim_date
  → Lattice detects: "Models use dim_ prefix for dimension tables"

Columns: created_at, updated_at, processed_at
  → Lattice detects: "Timestamp columns use _at suffix"
```

### 3. Corrections You Teach
```bash
lattice correct "revenue" "Always exclude refunds and taxes per ASC 606"
```

Now every AI query about revenue includes this context.

## Features

- **Zero Config**: Auto-detects dbt projects, finds manifest.json automatically
- **Fast**: Indexes 100-model projects in <30 seconds
- **Pattern Detection**: Automatically learns naming conventions (dim_, _amount, _at patterns)
- **Git Integration**: Extracts decisions from commit messages and PR descriptions
- **Learning System**: User corrections are prioritized and always shown
- **Smart Matching**: Understands partial names ("discount" → "discount_amount")
- **MCP Native**: Works with Claude Desktop, Cursor, Claude Code
- **Web Dashboard**: Beautiful UI for exploring decisions and entities
- **Full-Text Search**: Fast search across all decisions using SQLite FTS5
- **Data Export**: Export all data to JSON for backup and sharing
- **Structured Logging**: Debug-friendly logs with --verbose flag

## Example Use Cases

### New Team Member Onboarding
**Maya** (new analytics engineer) asks: "Why does dim_customer join on customer_key?"

Claude with Lattice:
> "The join uses customer_key (not customer_id) because customer_id isn't unique after the January 2024 CRM migration. This decision was made in commit a1b2c3d."

### AI-Assisted Development
**You:** "Add a discount column to fct_orders"

Claude with Lattice:
> "I'll add discount_amount (following your *_amount pattern for money columns) and ensure it excludes refunded orders per your correction from 2024-01-15."

### Code Review Automation
**Priya** no longer has to explain the same patterns in every PR review. Claude already knows:
- Column naming conventions
- Join strategies
- Business logic rules
- Historical decisions

## CLI Commands

```bash
# Initialize
lattice init

# Index project
lattice index
lattice index --incremental  # Only new changes
lattice index --verbose      # Show details

# List indexed content
lattice list decisions           # Show all decisions
lattice list decisions --entity "customers"  # Filter by entity
lattice list conventions         # Show detected patterns
lattice list corrections         # Show user corrections

# Search
lattice search "customer"        # Full-text search

# Export data
lattice export                   # Export to JSON
lattice export --output backup.json  # Custom path

# Get context
lattice context "add revenue to orders"
lattice context --entity "dim_customer"

# Add corrections
lattice correct "revenue" "Excludes refunds per finance"

# Check status
lattice status

# Start MCP server
lattice serve

# Launch web UI
lattice ui                       # Opens browser dashboard
lattice ui --port 8080           # Custom port

# Start GitHub Copilot server
lattice copilot                  # Provides context to GitHub Copilot
lattice copilot --port 8081      # Custom port

# Start Universal API server (for Cursor, Windsurf, etc)
lattice api                      # Provides context to ANY AI tool
lattice api --port 8082          # Custom port
```

## Web Dashboard

Lattice includes a beautiful web interface for exploring your project's context:

```bash
lattice ui  # Opens browser at http://localhost:8080
```

**Features:**
- **Dashboard**: Overview with statistics and recent decisions
- **Search**: Full-text search across all decisions
- **Decision Graph**: Interactive D3.js visualization showing relationships between decisions
- **Entity Explorer**: Browse all entities and their decision history
- **Real-time**: Live data from your indexed project

**Installation:**
```bash
pip install lattice-context[web]  # Includes FastAPI and Uvicorn
```

**Use Cases:**
- **Team Sharing**: Share URL with team members to explore context
- **Debugging**: Visual interface to verify indexing worked correctly
- **Onboarding**: Help new team members understand project conventions
- **Stakeholder Demos**: Professional UI for showing value to buyers

**Decision Graph:**

The web UI includes an interactive graph visualization showing relationships between decisions:
- **Visual Overview**: See all decisions and their relationships at a glance
- **Interactive**: Click and drag nodes to rearrange, hover for details
- **Filter by Type**: Show only models, columns, tables, or views
- **Export to PNG**: Download graph for documentation and presentations
- **Relationship Types**:
  - Blue edges: Evolution (same entity over time)
  - Green edges: Related (similar entities)

Perfect for understanding large projects (400+ models) and onboarding new team members.

## GitHub Copilot Integration

Give GitHub Copilot access to your team's institutional knowledge for dramatically better suggestions.

**Why This Matters:**
- AI tools only achieve **21.8% success rate** on repository-level code without context
- External tools providing context improve AI by **18-250%**
- **37.9% of developers** use GitHub Copilot

**Quick Start:**
```bash
# Start the context server
lattice copilot

# Server runs at http://localhost:8081
# Copilot can now query for institutional knowledge
```

**Example Impact:**

*Without Lattice:*
```python
# Copilot suggests (wrong):
discount_percent = 0.1
total_discount = order_total * discount_percent
```

*With Lattice:*
```python
# Copilot suggests (correct, following team convention):
discount_amount = order_total * 0.1  # Uses _amount suffix per team convention
```

**REST API Endpoints:**
- `POST /context` - Get context for a query
- `POST /context/file` - Get context for a specific file
- `POST /context/entity` - Get all context for an entity
- `POST /context/chat` - Get formatted context for Copilot Chat
- `GET /context/all` - Export all context
- `GET /health` - Health check

**VS Code Extension:**

Install "Lattice Context for GitHub Copilot" from VS Code Marketplace to auto-start the server and integrate seamlessly with Copilot.

**Full Documentation:** See [docs/COPILOT_INTEGRATION.md](docs/COPILOT_INTEGRATION.md)

## Universal API for All Tools

Lattice provides a universal REST API that works with **any AI coding tool** - not just Copilot.

**Supported Tools:**
- **Cursor** - AI-powered code editor
- **Windsurf** - AI coding assistant
- **VS Code** - Any AI extension
- **GitHub Copilot** - Also supported
- **Any tool** - That can make HTTP requests

**Quick Start:**
```bash
# Start the universal API server
lattice api

# Server runs on http://localhost:8082
```

**Query from any tool:**
```bash
curl -X POST http://localhost:8082/v1/context \
  -H "Content-Type: application/json" \
  -d '{
    "query": "revenue calculation",
    "tool": "cursor",
    "format": "markdown"
  }'
```

**Tool-Specific Endpoints:**
- `POST /v1/context/cursor` - Optimized for Cursor
- `POST /v1/context/windsurf` - Optimized for Windsurf
- `POST /v1/context/vscode` - Optimized for VS Code extensions

**Integration Guides:**
- Cursor: See `integrations/cursor/README.md`
- Windsurf: See `integrations/windsurf/README.md`
- Full API docs: See `docs/UNIVERSAL_API.md`

**Why This Matters:**
- 84.2% of developers use multiple AI tools
- Get consistent context across all your tools
- One API serves them all

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  1. EXTRACT                                                  │
│                                                              │
│  Git History ──────▶ Pattern Matching ──▶ Decisions        │
│  dbt Manifest ─────▶ Convention Detection ─▶ Patterns       │
│  YAML Descriptions ▶ Entity Extraction ───▶ Context         │
│  User Input ───────▶ Corrections ─────────▶ Learning        │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  2. STORE                                                    │
│                                                              │
│  SQLite + FTS5 (full-text search, <500ms queries)          │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  3. SERVE                                                    │
│                                                              │
│  MCP Server ────▶ Claude Desktop, Cursor, Claude Code       │
│                                                              │
│  AI asks for context ──▶ Tiered retrieval:                 │
│    • Immediate (entities in query)                          │
│    • Related (DAG neighbors, similar entities)              │
│    • Global (conventions, common patterns)                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Installation Options

### Option 1: pip (Recommended)
```bash
pip install lattice-context
```

### Option 2: Docker
```bash
# Pull the image
docker pull altimateai/lattice-context:latest

# Run in your dbt project
cd your-dbt-project
docker run -it --rm -v $(pwd):/workspace altimateai/lattice-context:latest lattice init
docker run -it --rm -v $(pwd):/workspace altimateai/lattice-context:latest lattice index

# Start MCP server
docker run -d --name lattice --rm -v $(pwd):/workspace altimateai/lattice-context:latest lattice serve
```

### Option 3: Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  lattice:
    image: altimateai/lattice-context:latest
    volumes:
      - ./:/workspace
    command: lattice serve
    stdin_open: true
    tty: true
```

Then: `docker-compose up`

## Requirements

- Python 3.10+ (if using pip)
- Docker (if using Docker)
- dbt project with compiled manifest.json
- Git repository (optional, for decision extraction)

## Roadmap

- ✅ **Phase 1**: dbt support, git extraction, MCP server
- 🚧 **Phase 2**: Snowflake/Databricks/BigQuery warehouse integration
- 📋 **Phase 3**: Airflow/Dagster orchestrator integration
- 📋 **Phase 4**: Looker/Tableau BI integration
- 📋 **Phase 5**: GitHub Action for automatic context capture

## Why Lattice?

| Feature | Lattice | Data Catalogs | dbt MCP |
|---------|---------|---------------|---------|
| **Automatic extraction** | ✅ Git + patterns | ❌ Manual | ❌ Static |
| **Decision history ("why")** | ✅ Core feature | ⚠️ Manual | ❌ No |
| **Learning from corrections** | ✅ Yes | ❌ No | ❌ No |
| **Convention detection** | ✅ Automatic | ❌ No | ❌ No |
| **Zero behavior change** | ✅ Git-first | ❌ Requires docs | ✅ Yes |

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

We welcome contributions! This is an open-source project built to help data teams work better with AI.

## Support

- GitHub Issues: [Report bugs or request features](https://github.com/altimate-ai/lattice-context/issues)
- Documentation: [Full docs](https://lattice.dev/docs)
- Email: hello@altimate.ai

---

Built with ❤️ by [Altimate AI](https://altimate.ai)
