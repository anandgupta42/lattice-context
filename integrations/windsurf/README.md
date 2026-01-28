# Windsurf Integration

Integrate Lattice with Windsurf AI for context-aware code generation.

## Setup

### 1. Start Lattice API Server

```bash
cd your-dbt-project
lattice api
```

The server will run on `http://localhost:8082`.

### 2. Configure Windsurf

Create a `.windsurf/rules.md` file in your project:

```markdown
# Lattice Context Rules

Before suggesting code, query the Lattice context API:

**Endpoint**: http://localhost:8082/v1/context/windsurf

**Usage**:
- Query for entities mentioned in the user's request
- Check for naming conventions
- Verify business rules
- Follow past decisions

**Example**:
```bash
curl -X POST http://localhost:8082/v1/context/windsurf?query=revenue&max_results=3
```

**Apply context to suggestions**:
- Use detected naming conventions (_amount, dim_, fct_)
- Respect business rules (ASC 606, exclude refunds)
- Reference past decisions in comments
```

### 3. Use in Windsurf

Windsurf will now have access to your team's institutional knowledge.

## Manual Testing

Test the API in Windsurf's terminal:

```bash
# Get context
curl -X POST "http://localhost:8082/v1/context/windsurf?query=customer&max_results=5"
```

## Example Workflow

**You**: "Create a fact table for customer orders"

**Windsurf** (internally):
1. Queries: `POST /v1/context/windsurf?query=customer orders fact`
2. Receives context:
   - Fact tables use `fct_` prefix
   - Join on `customer_key` (not `customer_id`)
   - Revenue calculation rules

**Windsurf suggests**:
```sql
-- models/marts/fct_customer_orders.sql
{{
  config(
    materialized='table',
    tags=['finance', 'daily']
  )
}}

SELECT
  order_key,
  customer_key,  -- Use customer_key per migration decision
  order_date,
  revenue_amount  -- Exclude tax per ASC 606
FROM {{ ref('stg_orders') }}
WHERE status != 'refunded'  -- Exclude refunds per finance rules
```

## API Endpoints

Windsurf can query:

### Main Endpoint
```bash
POST /v1/context/windsurf
?query=<your query>
&max_results=5
```

### Universal Endpoint (with tool specified)
```bash
POST /v1/context
{
  "query": "revenue calculation",
  "tool": "windsurf",
  "format": "markdown",
  "max_results": 5
}
```

## Benefits

- **Context-Aware**: Suggestions follow your team's patterns
- **Faster**: Less back-and-forth correcting conventions
- **Consistent**: All generated code matches existing style
- **Documented**: Suggestions include "why" from past decisions

## Troubleshooting

**Server not responding:**
```bash
# Check server is running
curl http://localhost:8082/health

# Should return: {"status": "healthy", "indexed": true}
```

**No context returned:**
```bash
# Verify indexing
cd your-dbt-project
lattice index

# Check what's indexed
lattice list decisions
```

**Wrong context:**
```bash
# Add corrections
lattice correct "entity_name" "This is the correct context"
```

## Advanced Configuration

### Custom System Prompt

Add to `.windsurf/rules.md`:

```markdown
# Custom Lattice Rules

1. **Always query Lattice first** before generating dbt code
2. **Naming Conventions**:
   - Check Lattice for detected patterns
   - Apply automatically to all suggestions
3. **Business Rules**:
   - Query Lattice for finance/compliance rules
   - Add comments explaining rule application
4. **Past Decisions**:
   - Reference decision IDs in comments
   - Link to source (git commit, PR)
```

### Multiple Projects

If working with multiple projects:

```bash
# Project 1
cd /path/to/project1
lattice api --port 8082

# Project 2
cd /path/to/project2
lattice api --port 8083
```

Update `.windsurf/rules.md` with the correct port for each project.

## Comparison

**Without Lattice**:
- Windsurf suggests generic dbt code
- Violates team conventions
- Ignores business rules
- Requires manual corrections

**With Lattice**:
- Windsurf suggests team-specific code
- Follows naming conventions
- Respects business rules
- Works on first try

**Time Saved**: ~70% less time fixing suggestions
