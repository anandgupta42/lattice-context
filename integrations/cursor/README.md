# Cursor Integration

Integrate Lattice with Cursor AI for context-aware code suggestions.

## Setup

### 1. Start Lattice API Server

```bash
cd your-dbt-project
lattice api
```

The server will run on `http://localhost:8082` by default.

### 2. Configure Cursor

Cursor can use external APIs for context. Create a `.cursorrules` file in your project:

```
# .cursorrules
[Lattice Context]
When helping with dbt code, always check http://localhost:8082/v1/context/cursor
for institutional knowledge about entities, conventions, and decisions.

Use this context to:
- Follow team naming conventions
- Respect business rules
- Reference past decisions
- Understand entity relationships
```

### 3. Use in Cursor

Cursor will now query Lattice when you:
- Ask questions about your dbt project
- Request code suggestions
- Get help with refactoring

## Manual Query (Optional)

You can also query the API manually in Cursor's terminal:

```bash
# Get context for a specific entity
curl -X POST http://localhost:8082/v1/context/cursor \
  -H "Content-Type: application/json" \
  -d '{"query": "dim_customers"}'
```

## Example

**You ask Cursor**: "Add a discount column to dim_customers"

**Cursor queries Lattice**:
```bash
POST /v1/context/cursor
{"query": "discount dim_customers"}
```

**Lattice responds** with context:
- Team uses `_amount` suffix (not `_percent`)
- Discounts stored as absolute values
- Business rule: Exclude refunded orders

**Cursor suggests** (now with context):
```sql
-- dim_customers.sql
SELECT
  customer_key,
  customer_name,
  discount_amount  -- Uses _amount suffix per team convention
FROM ...
```

## Troubleshooting

**Cursor not finding context:**
1. Verify server is running: `curl http://localhost:8082/health`
2. Check `.cursorrules` file exists in project root
3. Try manual query to test API

**Context not relevant:**
- Index your project: `lattice index`
- Add corrections: `lattice correct "entity" "context"`

## Advanced

### Custom Port

If you run the API on a different port:

```bash
lattice api --port 9000
```

Update `.cursorrules` to use `http://localhost:9000`.

### Project-Specific Rules

Add more specific rules to `.cursorrules`:

```
When working with revenue calculations:
1. Check Lattice context for ASC 606 compliance rules
2. Always exclude refunds and taxes
3. Follow team conventions from http://localhost:8082/v1/context/cursor
```

## Benefits

- **Better Suggestions**: Cursor follows your team's conventions
- **Business Rules**: Respects finance and compliance requirements
- **Faster Development**: Less time fixing convention violations
- **Consistent Code**: All suggestions align with existing patterns
