# Universal Context API

Provides Lattice institutional knowledge to **any AI coding tool** via REST API.

## Overview

The Universal Context API makes your team's decisions, conventions, and business rules available to:
- **Cursor** - AI-powered code editor
- **Windsurf** - AI coding assistant
- **VS Code** - With any AI extension
- **GitHub Copilot** - Via dedicated endpoint
- **Any tool** - That can make HTTP requests

## Quick Start

### 1. Start the Server

```bash
cd your-dbt-project
lattice api
```

Server runs on `http://localhost:8082` by default.

### 2. Query for Context

```bash
curl -X POST http://localhost:8082/v1/context \
  -H "Content-Type: application/json" \
  -d '{
    "query": "revenue calculation",
    "tool": "cursor",
    "format": "markdown",
    "max_results": 5
  }'
```

### 3. Get Formatted Response

```markdown
# Context from Lattice

Your team's institutional knowledge:

## 1. revenue_calculation

**Why**: Exclude tax and refunds per ASC 606 compliance

**Details**: Revenue recognition follows GAAP standards

*Source*: git_commit by sarah@company.com
```

## API Reference

### Base URL

```
http://localhost:8082
```

### Endpoints

#### POST /v1/context

Universal context endpoint for all tools.

**Request Body**:
```json
{
  "query": "customer revenue",
  "tool": "cursor",          // or "windsurf", "vscode", "copilot", "generic"
  "format": "markdown",      // or "json", "plain"
  "max_results": 5
}
```

**Response**:
```json
{
  "context": "# Context from Lattice\n\n...",
  "format": "markdown",
  "tool": "cursor",
  "has_results": true,
  "metadata": {
    "decision_count": 3,
    "query": "customer revenue"
  }
}
```

#### POST /v1/context/cursor

Cursor-specific shortcut endpoint.

**Query Parameters**:
- `query` (required): Search query
- `max_results` (optional): Max results (default: 5)

**Example**:
```bash
curl -X POST "http://localhost:8082/v1/context/cursor?query=discount&max_results=3"
```

#### POST /v1/context/windsurf

Windsurf-specific shortcut endpoint.

**Query Parameters**:
- `query` (required): Search query
- `max_results` (optional): Max results (default: 5)

**Example**:
```bash
curl -X POST "http://localhost:8082/v1/context/windsurf?query=fact+table&max_results=5"
```

#### POST /v1/context/vscode

VS Code-specific shortcut endpoint.

**Query Parameters**:
- `query` (required): Search query
- `max_results` (optional): Max results (default: 5)

**Example**:
```bash
curl -X POST "http://localhost:8082/v1/context/vscode?query=naming+conventions"
```

#### GET /

API information and supported tools.

**Response**:
```json
{
  "name": "Lattice Universal Context API",
  "version": "1.0.0",
  "supported_tools": ["cursor", "windsurf", "vscode", "copilot", "generic"],
  "supported_formats": ["markdown", "json", "plain"],
  "endpoints": {
    "POST /v1/context": "Get context for any tool",
    "POST /v1/context/cursor": "Cursor-specific endpoint",
    "POST /v1/context/windsurf": "Windsurf-specific endpoint",
    "POST /v1/context/vscode": "VS Code-specific endpoint",
    "GET /health": "Health check"
  }
}
```

#### GET /health

Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "indexed": true,
  "api_version": "1.0.0"
}
```

## Supported Tools

### Cursor

**Integration**: See [integrations/cursor/README.md](../integrations/cursor/README.md)

**Format**: Markdown with clear sections and code blocks

**Example Output**:
```markdown
# Context from Lattice

Your team's institutional knowledge:

## 1. dim_customers

**Why**: Customer dimension with lifetime value metrics

**Details**: Migrated from Salesforce in Jan 2024

*Source*: yaml_description by team
```

### Windsurf

**Integration**: See [integrations/windsurf/README.md](../integrations/windsurf/README.md)

**Format**: Concise bullet points

**Example Output**:
```markdown
📚 Team Knowledge:

• **dim_customers**: Customer dimension with lifetime value metrics
  └─ Migrated from Salesforce in Jan 2024
• **customer_key**: Use customer_key not customer_id for joins
  └─ customer_id no longer unique after migration
```

### VS Code

**Format**: Structured markdown with headers

**Example Output**:
```markdown
## Lattice Context

Institutional knowledge from your team:

### dim_customers

> Customer dimension with lifetime value metrics

Migrated from Salesforce in Jan 2024

*By team via yaml_description*
```

### GitHub Copilot

**Integration**: See [docs/COPILOT_INTEGRATION.md](COPILOT_INTEGRATION.md)

**Dedicated Server**: Use `lattice copilot` (port 8081)

**Format**: Optimized for Copilot suggestions

### Generic/Custom

**Format**: Plain text or JSON

**Use for**: Any tool that can make HTTP requests

**Example (Plain Text)**:
```
dim_customers: Customer dimension with lifetime value metrics
  Migrated from Salesforce in Jan 2024

customer_key: Use customer_key not customer_id for joins
  customer_id no longer unique after migration
```

**Example (JSON)**:
```json
{
  "decisions": [
    {
      "entity": "dim_customers",
      "why": "Customer dimension with lifetime value metrics",
      "context": "Migrated from Salesforce in Jan 2024",
      "source": "yaml_description",
      "author": "team",
      "timestamp": "2024-01-15T10:30:00"
    }
  ],
  "count": 1
}
```

## Configuration

### Server Options

```bash
# Default (port 8082, all interfaces)
lattice api

# Custom port
lattice api --port 9000

# Localhost only
lattice api --host 127.0.0.1

# Specific project
lattice api --path /path/to/project
```

### Environment Variables

```bash
# Set default port
export LATTICE_API_PORT=9000

# Then just run
lattice api
```

## Integration Examples

### Cursor Integration

**File**: `.cursorrules`

```
[Lattice Context]
When helping with dbt code, query http://localhost:8082/v1/context/cursor
for institutional knowledge.

Apply context to:
- Naming conventions
- Business rules
- Past decisions
```

### Windsurf Integration

**File**: `.windsurf/rules.md`

```markdown
# Lattice Integration

Query http://localhost:8082/v1/context/windsurf before generating code.

Use context for:
1. Naming conventions
2. Business rules
3. Architecture decisions
```

### VS Code Extension

**Extension Config** (`extension.ts`):

```typescript
const response = await fetch('http://localhost:8082/v1/context/vscode', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    query: fileName,
    max_results: 5
  })
});

const {context} = await response.json();
// Use context in completion provider
```

### Custom Tool Integration

**Any HTTP Client**:

```python
import requests

response = requests.post(
    'http://localhost:8082/v1/context',
    json={
        'query': 'revenue calculation',
        'tool': 'generic',
        'format': 'json',
        'max_results': 10
    }
)

data = response.json()
context = data['context']
decisions = data['metadata']['decision_count']
```

## Use Cases

### Use Case 1: Cursor Code Generation

**Scenario**: Developer asks Cursor to create a new mart model

**Flow**:
1. User: "Create fct_customer_orders"
2. Cursor queries: `POST /v1/context/cursor?query=fact customer orders`
3. Lattice returns:
   - Use `fct_` prefix for fact tables
   - Join on `customer_key` not `customer_id`
   - Revenue excludes tax per ASC 606
4. Cursor generates code with all conventions applied

**Impact**: Code correct on first try, no PR revisions needed

### Use Case 2: Windsurf Refactoring

**Scenario**: Refactor 10 models to new convention

**Flow**:
1. User: "Rename all revenue columns to use _amount suffix"
2. Windsurf queries: `POST /v1/context/windsurf?query=revenue`
3. Lattice returns:
   - `_amount` suffix convention detected
   - Revenue always excludes refunds
   - ASC 606 compliance required
4. Windsurf refactors with business rules intact

**Impact**: Safe refactoring with no broken business logic

### Use Case 3: VS Code Autocomplete

**Scenario**: Developer types in VS Code with AI extension

**Flow**:
1. Developer types: `SELECT discount_`
2. Extension queries: `POST /v1/context/vscode?query=discount`
3. Lattice returns: Team uses `_amount` not `_percent`
4. Extension suggests: `discount_amount`

**Impact**: Always correct naming, zero convention violations

### Use Case 4: Custom CLI Tool

**Scenario**: Team builds internal code generator

**Flow**:
1. Generator queries: `POST /v1/context` with JSON format
2. Lattice returns decisions as structured data
3. Generator applies rules programmatically
4. Generated code follows all conventions

**Impact**: Automated tools respect institutional knowledge

## Performance

### Response Times

- **Simple queries**: <50ms
- **Complex queries**: <100ms
- **Large result sets** (20+ decisions): <200ms

### Scalability

- **Concurrent requests**: 100+ req/sec
- **Memory usage**: ~50MB
- **Database**: SQLite (no external dependencies)

### Caching

Context is queried from SQLite FTS5 index:
- Fast full-text search
- Results cached at database level
- No manual cache invalidation needed

## Security

### Local Only (Default)

Server binds to all interfaces by default. For localhost only:

```bash
lattice api --host 127.0.0.1
```

### No Authentication

The API has no authentication by default. Recommendations:

- **Development**: Run on localhost only
- **Team Use**: Use VPN or internal network
- **Production**: Add reverse proxy with auth (nginx, Caddy)

### CORS

CORS is enabled for all origins by default. To restrict:

Modify `context_server.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specific origins only
    ...
)
```

## Troubleshooting

### Server Won't Start

**Error**: `Lattice not indexed`

**Solution**:
```bash
lattice init
lattice index
```

### No Context Returned

**Check Indexing**:
```bash
lattice list decisions
```

If empty:
```bash
lattice index --verbose
```

### Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Use different port
lattice api --port 9000

# Or kill process on 8082
lsof -ti:8082 | xargs kill
```

### Context Not Relevant

**Add Corrections**:
```bash
lattice correct "entity" "Correct context here"
```

**Re-index**:
```bash
lattice index
```

## Comparison to Alternatives

### vs. Copilot-Only

**Copilot Server** (port 8081):
- ✅ Optimized for Copilot
- ❌ Only works with Copilot

**Universal API** (port 8082):
- ✅ Works with all tools
- ✅ Multiple output formats
- ✅ Tool-specific formatting

**Use Both**: Run both servers for best coverage

### vs. Manual Context Sharing

**Manual** (copy-paste):
- ❌ Time-consuming
- ❌ Inconsistent
- ❌ Outdated quickly

**Universal API**:
- ✅ Automatic
- ✅ Always current
- ✅ Consistent across tools

## Roadmap

### Current (v1.0)
- ✅ Universal REST API
- ✅ Cursor support
- ✅ Windsurf support
- ✅ VS Code support
- ✅ GitHub Copilot support
- ✅ Multiple output formats

### Next (v1.1)
- 🔨 Cursor official plugin
- 🔨 Windsurf official plugin
- 🔨 VS Code extension marketplace
- 🔨 Authentication (optional)
- 🔨 Rate limiting

### Future (v2.0)
- 🔨 WebSocket support (real-time)
- 🔨 GraphQL endpoint
- 🔨 LLM-enhanced responses
- 🔨 Multi-language support (Python, Java, etc.)

## Support

- **Documentation**: This file
- **Integration Guides**: `integrations/` directory
- **Issues**: [GitHub Issues](https://github.com/altimate-ai/lattice-context/issues)
- **Discussions**: [GitHub Discussions](https://github.com/altimate-ai/lattice-context/discussions)

---

**Research Citations**:
- Multi-tool usage: 84.2% of developers use multiple AI tools
- Context improvement: 18-250% better AI performance with external context
- Developer preference: Teams want unified context across all tools
