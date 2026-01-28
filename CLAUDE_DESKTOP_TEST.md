# Claude Desktop Integration Test Guide

**Purpose:** Validate end-to-end integration between Lattice and Claude Desktop via MCP.

**Status:** Ready for manual testing

---

## Prerequisites

Before testing, ensure:
- [x] Lattice installed (`pip install -e .` or `pip install lattice-context`)
- [x] Claude Desktop installed (latest version)
- [x] Sample dbt project available for testing
- [x] Terminal access for debugging

---

## Test Procedure

### Phase 1: Setup (5 minutes)

#### Step 1: Install Lattice
```bash
# Option A: From source
cd /path/to/lattice-context
pip install -e .

# Option B: From PyPI (after release)
pip install lattice-context

# Verify installation
lattice --version
lattice --help
```

**Expected:** Version and help displayed correctly.

#### Step 2: Initialize in dbt Project
```bash
cd /path/to/your/dbt-project

# Ensure manifest exists
dbt compile

# Initialize Lattice
lattice init

# Index project
lattice index
```

**Expected:**
- `.lattice/` directory created
- `index.db` populated
- Summary shows: X entities, Y conventions, Z decisions

#### Step 3: Test CLI Context Query
```bash
# Test context retrieval
lattice context "add revenue column to orders"
```

**Expected:** Context returned with relevant decisions/conventions.

#### Step 4: Configure Claude Desktop

**Location:** `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

**Config:**
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

**Alternative (if using venv):**
```json
{
  "mcpServers": {
    "lattice": {
      "command": "/full/path/to/venv/bin/lattice",
      "args": ["serve"]
    }
  }
}
```

#### Step 5: Restart Claude Desktop

Close and reopen Claude Desktop completely.

---

### Phase 2: Basic Integration (10 minutes)

#### Test 1: Server Connection

**In Claude Desktop, type:**
```
Can you list the MCP servers you have available?
```

**Expected:** Claude mentions "lattice" in the list.

**If not visible:** Check Claude Desktop logs at `~/Library/Logs/Claude/mcp.log`

#### Test 2: Tool Discovery

**Ask Claude:**
```
What tools does the lattice server provide?
```

**Expected:** Claude lists:
- `get_context`
- `add_correction`
- `explain`

#### Test 3: Get Context Tool

**Ask Claude:**
```
Use the lattice get_context tool with task "add revenue column to orders"
```

**Expected:**
- Tool executes successfully
- Returns structured context
- Shows relevant decisions/conventions/corrections

**Verify response includes:**
- Decisions section (if any from git/YAML)
- Conventions section (if detected patterns)
- Corrections section (if any added)

#### Test 4: Natural Query (No Explicit Tool Call)

**Ask Claude:**
```
I need to add a discount column to the dim_customers model.
What naming conventions should I follow?
```

**Expected:**
- Claude automatically uses `get_context` tool
- Provides answer based on project context
- Mentions specific conventions from your project

---

### Phase 3: Advanced Features (15 minutes)

#### Test 5: Multiple Queries

**Series of questions:**
```
1. "What's the naming pattern for monetary columns?"
2. "How should timestamp columns be named?"
3. "Are there any conventions for dimension tables?"
```

**Expected:** Each query returns relevant project-specific context.

#### Test 6: Add Correction

**Ask Claude:**
```
Use the lattice add_correction tool to add this correction:
Entity: "revenue"
Correction: "Always exclude refunds and taxes per ASC 606"
```

**Expected:**
- Tool executes successfully
- Correction is stored
- Confirmation message returned

**Verify:**
```bash
# In terminal
lattice context "revenue"
```

Should now show the correction in output.

#### Test 7: Correction Recall

**Ask Claude:**
```
I need to add a revenue column. What should I know?
```

**Expected:** Claude's response includes the correction about excluding refunds/taxes.

#### Test 8: Explain Tool

**Ask Claude:**
```
Use the lattice explain tool for entity "dim_customer"
```

**Expected:**
- Historical context about the entity
- Decisions related to it
- Any relevant conventions

---

### Phase 4: Real-World Scenarios (20 minutes)

#### Scenario 1: New Column Addition

**Context:** You want to add a new column.

**Ask Claude:**
```
I want to add a discount column to fct_orders.
Help me write the SQL following our project conventions.
```

**Expected:**
- Claude queries lattice for context
- Suggests column name following conventions (e.g., `discount_amount` if `_amount` pattern detected)
- Writes SQL that matches project style
- Warns about any relevant corrections

**Validate:**
- Does Claude use the right naming pattern?
- Does it follow detected conventions?
- Does it incorporate corrections?

#### Scenario 2: Model Creation

**Ask Claude:**
```
I need to create a new dimension table for products.
What naming conventions should I follow and what's the standard structure?
```

**Expected:**
- Claude uses lattice to check conventions
- Suggests appropriate prefix (e.g., `dim_products` if `dim_` pattern exists)
- Recommends common columns based on existing dimensions

#### Scenario 3: Debugging Query

**Ask Claude:**
```
I'm seeing unexpected results when joining orders and customers.
What join keys does our project typically use?
```

**Expected:**
- Claude queries for relevant decisions
- Mentions historical decisions about join keys
- References any corrections about specific joins

#### Scenario 4: Onboarding Question

**Simulate new team member:**
```
I'm new to this project. Can you explain why we use customer_key
instead of customer_id for joins?
```

**Expected:**
- Claude uses explain tool
- Returns historical context from git commits
- Explains the reasoning (if captured in history)

---

### Phase 5: Error Handling (10 minutes)

#### Test 9: Invalid Query

**Ask Claude:**
```
Get context for "xyzabc123nonexistent"
```

**Expected:**
- Tool executes without crashing
- Returns gracefully (no results or general context)
- Claude handles empty response appropriately

#### Test 10: Server Interruption

**Procedure:**
1. Start a query in Claude Desktop
2. Manually kill the lattice server (Ctrl+C if running)
3. Try another query

**Expected:**
- Claude Desktop shows error but doesn't crash
- Clear error message about server unavailable
- Can recover when server restarts

#### Test 11: Malformed Request

**Ask Claude to:**
```
Use lattice get_context with an empty task string
```

**Expected:**
- Graceful error handling
- Helpful error message
- Server doesn't crash

---

## Validation Checklist

### Connectivity ✓/✗
- [ ] Lattice appears in Claude Desktop's MCP server list
- [ ] All three tools are discoverable
- [ ] Server starts without errors
- [ ] Connection is stable during conversation

### Functionality ✓/✗
- [ ] `get_context` returns relevant results
- [ ] `add_correction` stores corrections successfully
- [ ] `explain` provides historical context
- [ ] Claude automatically uses tools when appropriate

### Performance ✓/✗
- [ ] Tool calls complete in <2 seconds
- [ ] No noticeable lag in Claude Desktop
- [ ] Server handles rapid successive queries
- [ ] Memory usage is reasonable

### User Experience ✓/✗
- [ ] Context is genuinely helpful
- [ ] Responses are well-formatted
- [ ] Error messages are clear
- [ ] Corrections are prioritized in responses

### Real-World Value ✓/✗
- [ ] New column suggestions follow conventions
- [ ] Historical decisions inform answers
- [ ] Corrections are applied consistently
- [ ] Onboarding questions get useful answers

---

## Troubleshooting

### Issue: Lattice Not Appearing in MCP List

**Check:**
```bash
# Verify lattice is in PATH
which lattice

# Test command directly
lattice serve

# Check Claude Desktop logs
tail -f ~/Library/Logs/Claude/mcp.log
```

**Fix:**
- Use full path in config: `/full/path/to/lattice`
- Ensure lattice is executable
- Restart Claude Desktop completely

### Issue: "Server Failed to Start"

**Check:**
```bash
# Test server manually
lattice serve

# Look for Python errors
# Check if .lattice directory exists in current dir
```

**Fix:**
- Ensure in dbt project directory
- Run `lattice init` first
- Check permissions on .lattice directory

### Issue: Context Not Relevant

**Check:**
```bash
# Verify indexing worked
lattice status

# Check what was indexed
sqlite3 .lattice/index.db "SELECT COUNT(*) FROM decisions;"
sqlite3 .lattice/index.db "SELECT COUNT(*) FROM conventions;"
```

**Fix:**
- Re-run `lattice index --verbose`
- Add corrections for important concepts
- Ensure dbt models have descriptions

### Issue: Slow Responses

**Check:**
```bash
# Test query speed directly
time lattice context "test query"

# Check database size
ls -lh .lattice/index.db
```

**Fix:**
- Should be <500ms for queries
- If slow, check for database corruption
- Re-index if needed

---

## Success Criteria

**The integration is successful if:**

1. **Connection Works:** All tools are callable from Claude Desktop
2. **Context is Useful:** Returned context helps with real tasks
3. **Performance is Good:** Queries complete in <2 seconds
4. **Stable Operation:** No crashes during 30-minute session
5. **Real Value:** User would actually use this in daily work

**Minimum Acceptable:**
- At least 3 useful responses out of 5 queries
- Tools work 90%+ of the time
- Performance <2s average
- Zero server crashes

**Excellent:**
- Consistently helpful responses
- Tools work 100% of the time
- Performance <500ms average
- Seamless experience

---

## Reporting Results

After testing, document:

### What Worked ✅
- List specific successful scenarios
- Note particularly impressive responses
- Highlight valuable features

### What Didn't Work ❌
- List failures with details
- Include error messages
- Note UX friction points

### Performance Metrics
- Average query time: ___ms
- Successful queries: ___/___
- Server crashes: ___
- Overall stability: ___/10

### User Experience Rating
- Ease of setup: ___/10
- Response quality: ___/10
- Tool discoverability: ___/10
- Overall usefulness: ___/10

### Recommendations
- Must-fix issues before launch
- Nice-to-have improvements
- Documentation gaps
- Feature requests

---

## Next Steps After Testing

**If test passes (>80% success rate):**
- ✅ Mark criterion as complete
- ✅ Document any quirks in README
- ✅ Proceed with launch

**If test has issues (50-80%):**
- Fix critical bugs
- Re-test
- Document known limitations

**If test fails (<50%):**
- Investigate root causes
- Major fixes needed
- Re-architect if necessary

---

## Test Environment Details

**Fill in after testing:**

```
Date: _______________
Tester: _______________
Claude Desktop Version: _______________
Lattice Version: _______________
dbt Project: _______________ (size: ___ models)
OS: _______________
Python: _______________

Test Duration: ___ minutes
Overall Success Rate: ___%
Would Recommend: Yes / No

Notes:
_______________________________________________
_______________________________________________
_______________________________________________
```

---

**This test validates the final unchecked item in the release checklist.**

Once completed, all release criteria will be verified and the product is ready for public launch.
