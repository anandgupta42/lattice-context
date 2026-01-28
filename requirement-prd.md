# Lattice Context Layer: Product Specification

> **The "Why" Layer for the Modern Data Stack**
>
> Give AI assistants the institutional knowledge they need to understand your data stack—automatically extracted from git history, enriched with user corrections, and served via MCP.

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Solution Overview](#solution-overview)
3. [Target Users](#target-users)
4. [Core Concepts](#core-concepts)
5. [Technical Architecture](#technical-architecture)
6. [Data Stack Coverage](#data-stack-coverage)
7. [Feature Specification](#feature-specification)
8. [MCP Tools Reference](#mcp-tools-reference)
9. [CLI Reference](#cli-reference)
10. [Configuration](#configuration)
11. [Roadmap](#roadmap)
12. [Success Metrics](#success-metrics)
13. [Competitive Positioning](#competitive-positioning)
14. [Pricing Strategy](#pricing-strategy)
15. [Go-To-Market](#go-to-market)

---

## Problem Statement

### The Context Gap in AI-Assisted Data Engineering

Modern data teams use AI assistants (Claude, ChatGPT, Copilot, Cursor) to write SQL, build dbt models, configure pipelines, and define metrics. But these AI assistants face a critical limitation:

**They can see WHAT exists, but not WHY it was built that way.**

#### The Symptoms

| Symptom | Example | Impact |
|---------|---------|--------|
| **Repeated mistakes** | AI suggests `customer_id` when team uses `customer_key` | Broken joins, debugging time |
| **Inconsistent patterns** | AI uses `snake_case` when team uses `camelCase` | Code review friction |
| **Missing business context** | AI doesn't know "revenue" excludes refunds | Wrong metrics |
| **Lost decisions** | No one remembers why model X uses LEFT JOIN | Technical debt |
| **Slow onboarding** | New hires ask same questions for months | Productivity loss |

#### The Root Cause

```
┌─────────────────────────────────────────────────────────────────┐
│                    WHERE KNOWLEDGE LIVES                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   📧 Slack threads (unsearchable, disappear)                   │
│   📝 Confluence pages (outdated, ignored)                       │
│   🧠 Senior engineer's head (leaves company)                   │
│   💬 PR descriptions (disconnected from code)                   │
│   📋 Jira tickets (never linked to implementation)             │
│   🗣️ Verbal explanations (never documented)                    │
│                                                                 │
│   ═══════════════════════════════════════════════════════════  │
│                                                                 │
│   🤖 AI Assistant: "I have no idea why this exists"            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Quantified Impact

- **65% of developers** cite "missing context" as the top AI code quality issue (Qodo 2025)
- **40% of data professional time** spent firefighting due to lack of context (Forrester)
- **3-6 months** average onboarding time for data engineers
- **$37K-$75K** cost per new hire during ramp-up period

### What Existing Tools Don't Solve

| Tool Category | What They Provide | What's Missing |
|--------------|-------------------|----------------|
| **Data Catalogs** (Atlan, Alation) | Asset inventory, tags, ownership | Decision history, automatic extraction |
| **dbt MCP Server** | Model metadata, lineage, metrics | Why decisions were made |
| **Git/GitHub** | Commit history, PR descriptions | Structured extraction, AI-ready format |
| **Confluence/Notion** | Manual documentation | Always outdated, disconnected from code |

### The Opportunity

**Automatically extract the "why" from where it already exists (git history, PRs, code comments) and serve it to AI assistants via MCP.**

---

## Solution Overview

### What Lattice Does

```
┌─────────────────────────────────────────────────────────────────┐
│                         LATTICE                                 │
│                   Context Layer for Data                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    EXTRACTION LAYER                       │  │
│  │                                                           │  │
│  │   Git History ──┐                                        │  │
│  │   PR Descriptions ──┼──▶ LLM Summarization ──▶ Decisions │  │
│  │   Code Comments ──┤                                      │  │
│  │   Config Files ──┘                                       │  │
│  │                                                           │  │
│  │   Convention Detection ──────────────────────▶ Patterns  │  │
│  │                                                           │  │
│  │   User Corrections ──────────────────────────▶ Learning  │  │
│  │                                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                     STORAGE LAYER                         │  │
│  │                                                           │  │
│  │   SQLite + FTS5 (full-text search)                       │  │
│  │   JSONL (append-only corrections)                        │  │
│  │   Embeddings (semantic search)                           │  │
│  │                                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    SERVING LAYER                          │  │
│  │                                                           │  │
│  │   MCP Server ───▶ Claude Desktop, Cursor, Claude Code    │  │
│  │   REST API ────▶ Custom integrations                     │  │
│  │   CLI ─────────▶ Scripts, CI/CD                          │  │
│  │                                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Core Value Propositions

1. **Zero Behavior Change Required**: Extracts from existing git history, PRs, and configs
2. **Automatic Decision Capture**: LLM summarizes commit context into structured decisions
3. **Learning System**: User corrections improve context quality over time
4. **Universal Interface**: MCP server works with any AI assistant
5. **Data Stack Native**: Purpose-built for dbt, warehouses, orchestrators, and BI tools

---

## Target Users

### Primary: Analytics Engineers / Data Engineers

- Use dbt daily
- Work with Snowflake/Databricks/BigQuery
- Configure Airflow/Dagster pipelines
- Define metrics in Looker/Tableau
- Already using AI assistants (Claude, Copilot, Cursor)

### Secondary: Data Team Leads

- Responsible for onboarding new team members
- Care about institutional knowledge preservation
- Budget holders for data tools

### Tertiary: Platform Engineers (Data Platform)

- Maintain data infrastructure
- Evaluate and integrate tools
- Care about standardization

### User Personas

#### Persona 1: Maya (Analytics Engineer, 3 years experience)

> "Every time I use Claude to help write a dbt model, I have to explain our naming conventions, why we use certain join strategies, and what columns actually mean. It would be amazing if it just knew."

**Pain Points:**
- Repeating context to AI assistants
- Inconsistent AI-generated code
- Not knowing why legacy models are built certain ways

**Success Metric:** AI suggestions match team patterns 80%+ of the time

#### Persona 2: James (Data Team Lead, 8 years experience)

> "We lost Sarah last month—she was here for 5 years. Half of our institutional knowledge walked out the door. The new hire keeps asking questions nobody can answer."

**Pain Points:**
- Knowledge loss when people leave
- Slow onboarding (3-6 months)
- Answering the same questions repeatedly

**Success Metric:** New hire productive in 6 weeks instead of 3 months

#### Persona 3: Priya (Senior Data Engineer, 6 years experience)

> "I spend 30% of my time in code review explaining why things are done a certain way. If AI could just learn our patterns, reviews would be so much faster."

**Pain Points:**
- Repetitive code review feedback
- AI tools suggesting anti-patterns
- Documenting decisions manually

**Success Metric:** Code review time reduced by 40%

---

## Core Concepts

### 1. Decisions

A **Decision** is a captured piece of institutional knowledge about why something in the data stack is built a certain way.

```typescript
interface Decision {
  id: string;

  // What changed
  entity: string;           // e.g., "dim_customer", "revenue", "daily_pipeline"
  entityType: EntityType;   // model, column, metric, dag, table, etc.
  changeType: ChangeType;   // created, modified, removed, renamed

  // Why it changed
  why: string;              // Extracted rationale
  context: string;          // Additional context

  // Source
  source: DecisionSource;   // git_commit, pr_description, user_correction, etc.
  sourceRef: string;        // commit SHA, PR number, etc.

  // Metadata
  author: string;
  timestamp: Date;
  confidence: number;       // 0-1, extraction confidence

  // Categorization
  tags: string[];
  tool: DataTool;           // dbt, airflow, snowflake, looker, etc.
}

type EntityType =
  | 'model' | 'column' | 'metric' | 'dimension'
  | 'table' | 'view' | 'schema' | 'database'
  | 'dag' | 'task' | 'schedule' | 'sensor'
  | 'dashboard' | 'explore' | 'measure' | 'filter';

type ChangeType =
  | 'created' | 'modified' | 'removed' | 'renamed'
  | 'logic_changed' | 'dependency_added' | 'dependency_removed'
  | 'test_added' | 'documentation_added';

type DecisionSource =
  | 'git_commit' | 'pr_description' | 'pr_comment'
  | 'code_comment' | 'yaml_description' | 'user_correction'
  | 'jira_ticket' | 'linear_issue';

type DataTool =
  | 'dbt' | 'sqlmesh'
  | 'snowflake' | 'databricks' | 'bigquery' | 'redshift'
  | 'airflow' | 'dagster' | 'prefect'
  | 'looker' | 'tableau' | 'metabase' | 'mode';
```

### 2. Conventions

A **Convention** is a detected pattern in naming, structure, or organization.

```typescript
interface Convention {
  id: string;

  // Pattern
  type: ConventionType;
  pattern: string;          // e.g., "is_*", "dim_*", "*_at"
  appliesTo: EntityType[];

  // Evidence
  examples: string[];
  frequency: number;        // How often this pattern appears
  confidence: number;       // 0-1

  // Metadata
  detectedAt: Date;
  tool: DataTool;
}

type ConventionType =
  | 'prefix' | 'suffix' | 'case' | 'separator'
  | 'directory_structure' | 'file_naming'
  | 'column_ordering' | 'test_pattern';
```

### 3. Corrections

A **Correction** is user-provided knowledge that overrides or supplements extracted context.

```typescript
interface Correction {
  id: string;

  // Target
  entity: string;
  entityType: EntityType;

  // Correction
  correction: string;       // The actual correction text
  context: string;          // When this applies

  // Metadata
  addedBy: string;
  addedAt: Date;

  // Scope
  scope: 'global' | 'entity' | 'pattern';
  priority: 'high' | 'medium' | 'low';
}
```

### 4. Context Request/Response

```typescript
interface ContextRequest {
  // What the user is working on
  task?: string;            // Natural language task description
  files?: string[];         // Files being modified
  entities?: string[];      // Specific entities to get context for

  // Constraints
  maxTokens?: number;       // Token budget
  tools?: DataTool[];       // Filter by tool

  // Options
  includeDecisions?: boolean;
  includeConventions?: boolean;
  includeCorrections?: boolean;
}

interface ContextResponse {
  // Tiered content
  tiers: {
    immediate: TierContent;   // Directly relevant
    related: TierContent;     // DAG neighbors, related entities
    global: TierContent;      // Conventions, common patterns
  };

  // Extracted items
  decisions: Decision[];
  conventions: Convention[];
  corrections: Correction[];

  // Metadata
  totalTokens: number;
  sources: string[];
}

interface TierContent {
  content: string;
  tokens: number;
  sources: string[];
}
```

---

## Technical Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│   │   Claude    │  │   Cursor    │  │   Claude    │  │   Custom    │   │
│   │   Desktop   │  │             │  │    Code     │  │    Apps     │   │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘   │
│          │                │                │                │           │
│          └────────────────┼────────────────┼────────────────┘           │
│                           │                │                            │
│                      MCP Protocol      REST API                         │
│                           │                │                            │
└───────────────────────────┼────────────────┼────────────────────────────┘
                            │                │
┌───────────────────────────┼────────────────┼────────────────────────────┐
│                           ▼                ▼         SERVING LAYER      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                         MCP SERVER                               │   │
│   │                                                                  │   │
│   │   Tools:                                                         │   │
│   │   • get_context      • get_decision     • search_decisions      │   │
│   │   • get_conventions  • get_corrections  • add_correction        │   │
│   │   • get_entity_history                  • explain_entity        │   │
│   │                                                                  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                       RETRIEVAL ENGINE                           │   │
│   │                                                                  │   │
│   │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │   │
│   │   │  Tier 1:    │  │  Tier 2:    │  │  Tier 3:    │            │   │
│   │   │  Immediate  │  │  Related    │  │  Global     │            │   │
│   │   │  (2500 tok) │  │  (2500 tok) │  │  (2000 tok) │            │   │
│   │   └─────────────┘  └─────────────┘  └─────────────┘            │   │
│   │                                                                  │   │
│   │   Token Budget Manager | Relevance Scoring | Deduplication      │   │
│   │                                                                  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└───────────────────────────────────────────────────────────────────────────┘
                                    │
┌───────────────────────────────────┼───────────────────────────────────────┐
│                                   ▼              STORAGE LAYER            │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│   │    SQLite +     │  │      JSONL      │  │    Embeddings   │         │
│   │      FTS5       │  │   (Append-Only) │  │    (sqlite-vec) │         │
│   │                 │  │                 │  │                 │         │
│   │  • decisions    │  │  • corrections  │  │  • decision     │         │
│   │  • conventions  │  │  • audit_log    │  │    embeddings   │         │
│   │  • entities     │  │                 │  │  • entity       │         │
│   │  • relationships│  │                 │  │    embeddings   │         │
│   └─────────────────┘  └─────────────────┘  └─────────────────┘         │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
                                    │
┌───────────────────────────────────┼───────────────────────────────────────┐
│                                   ▼            EXTRACTION LAYER           │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│   ┌─────────────────────────────────────────────────────────────────┐    │
│   │                      DECISION EXTRACTOR                          │    │
│   │                                                                  │    │
│   │   ┌───────────────┐    ┌───────────────┐    ┌───────────────┐  │    │
│   │   │  Git Parser   │───▶│ LLM Summarizer│───▶│   Normalizer  │  │    │
│   │   └───────────────┘    └───────────────┘    └───────────────┘  │    │
│   │                                                                  │    │
│   │   Inputs: commits, PRs, comments, YAML descriptions            │    │
│   │   Output: structured Decision objects                           │    │
│   │                                                                  │    │
│   └─────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│   ┌─────────────────────────────────────────────────────────────────┐    │
│   │                    CONVENTION DETECTOR                           │    │
│   │                                                                  │    │
│   │   Pattern Mining | Frequency Analysis | Confidence Scoring      │    │
│   │                                                                  │    │
│   │   Detects: prefixes, suffixes, case patterns, structures        │    │
│   │                                                                  │    │
│   └─────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│   ┌─────────────────────────────────────────────────────────────────┐    │
│   │                      TOOL CONNECTORS                             │    │
│   │                                                                  │    │
│   │   ┌─────┐ ┌─────────┐ ┌───────┐ ┌──────┐ ┌───────┐ ┌──────┐   │    │
│   │   │ dbt │ │Snowflake│ │Airflow│ │Looker│ │Dagster│ │ ...  │   │    │
│   │   └─────┘ └─────────┘ └───────┘ └──────┘ └───────┘ └──────┘   │    │
│   │                                                                  │    │
│   └─────────────────────────────────────────────────────────────────┘    │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Language | TypeScript | Type safety, ecosystem, team familiarity |
| Storage | SQLite + FTS5 | Portable, fast, full-text search built-in |
| Embeddings | sqlite-vec | Semantic search without external dependencies |
| MCP | @modelcontextprotocol/sdk | Standard protocol |
| LLM | Claude API (Haiku) | Cost-effective summarization |
| CLI | Commander.js | Standard Node.js CLI framework |
| Git | simple-git | Git operations |

### Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         INDEXING FLOW                                │
└─────────────────────────────────────────────────────────────────────┘

   Git Repo                    Extraction                    Storage
   ────────                    ──────────                    ───────

   commits ──────────────────▶ parse commit ─────────────▶ decisions
   (git log)                   message, diff                 table
                                    │
                                    ▼
                              LLM summarize
                              (if complex)
                                    │
                                    ▼
                              extract "why"
                              detect change type

   PRs ──────────────────────▶ parse description ────────▶ decisions
   (GitHub API)                extract rationale           table

   dbt manifest ─────────────▶ parse models ─────────────▶ entities
   (manifest.json)             columns, tests              table
                                    │
                                    ▼
                              detect conventions ────────▶ conventions
                              (pattern mining)             table

   YAML descriptions ────────▶ extract descriptions ─────▶ decisions
   (schema.yml)                link to entities            table


┌─────────────────────────────────────────────────────────────────────┐
│                         RETRIEVAL FLOW                               │
└─────────────────────────────────────────────────────────────────────┘

   AI Request                  Retrieval                    Response
   ──────────                  ─────────                    ────────

   "Add revenue column
    to orders model"
         │
         ▼
   ┌─────────────┐
   │ Parse task  │
   │ Extract:    │
   │ • entities  │────────────▶ Tier 1: Immediate
   │ • intent    │             Query decisions for
   │ • files     │             "orders", "revenue"
   └─────────────┘                    │
                                      ▼
                              Tier 2: Related
                              Query DAG neighbors
                              of "orders" model
                                      │
                                      ▼
                              Tier 3: Global
                              Get conventions for
                              columns, naming
                                      │
                                      ▼
                              Apply token budget
                              Rank by relevance
                              Deduplicate
                                      │
                                      ▼
                              ┌─────────────┐
                              │  Response   │
                              │             │
                              │ • decisions │
                              │ • patterns  │
                              │ • warnings  │
                              └─────────────┘
```

---

## Data Stack Coverage

### Overview

Lattice extracts decision context from across the modern data stack:

```
┌─────────────────────────────────────────────────────────────────────┐
│                      MODERN DATA STACK                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   INGEST              TRANSFORM           STORE              SERVE  │
│   ──────              ─────────           ─────              ─────  │
│                                                                      │
│   ┌─────────┐        ┌─────────┐        ┌─────────┐       ┌──────┐ │
│   │Fivetran │        │   dbt   │        │Snowflake│       │Looker│ │
│   │Airbyte  │───────▶│ SQLMesh │───────▶│Databricks───────▶│Tableau│
│   │Stitch   │        │         │        │BigQuery │       │Mode  │ │
│   └─────────┘        └─────────┘        └─────────┘       └──────┘ │
│                           │                  │                      │
│                           │                  │                      │
│                      ┌────┴────┐        ┌────┴────┐                │
│                      │         │        │         │                │
│                      ▼         ▼        ▼         ▼                │
│                 ┌─────────┐        ┌─────────────────┐             │
│                 │ORCHESTRATE       │   DDL CHANGES   │             │
│                 │                  │                 │             │
│                 │ Airflow │        │ Schema changes  │             │
│                 │ Dagster │        │ Table creates   │             │
│                 │ Prefect │        │ Column mods     │             │
│                 └─────────┘        └─────────────────┘             │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│                        LATTICE COVERAGE                             │
│                                                                      │
│   ✅ Phase 1: dbt/SQLMesh (Transform)                               │
│   ✅ Phase 2: Snowflake/Databricks/BigQuery (DDL)                   │
│   ✅ Phase 3: Airflow/Dagster/Prefect (Orchestrate)                 │
│   ✅ Phase 4: Looker/Tableau (BI/Metrics)                           │
│   ⏳ Phase 5: Fivetran/Airbyte (Ingest) - Future                    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Tool-Specific Details

#### 1. dbt / SQLMesh (Transform Layer)

**Sources:**
- `manifest.json` - Model metadata, columns, tests
- `schema.yml` - Descriptions, documentation
- Git history - Model changes, PR context
- `target/run_results.json` - Test results

**Entities Extracted:**
| Entity | Source | Decision Types |
|--------|--------|----------------|
| Models | manifest.json | created, modified, renamed, removed |
| Columns | manifest.json | added, removed, type_changed |
| Tests | manifest.json | added, removed |
| Sources | manifest.json | added, removed |
| Macros | manifest.json | created, modified |
| Exposures | manifest.json | created, modified |

**Conventions Detected:**
- Model naming: `dim_*`, `fct_*`, `stg_*`, `int_*`
- Column naming: `*_id`, `*_at`, `*_date`, `is_*`, `has_*`
- Test patterns: unique, not_null, relationships
- Directory structure: staging/, marts/, intermediate/

**Git Analysis:**
```python
# Patterns we look for in dbt commits
patterns = [
    r"add(?:ed|ing)?\s+(?:column|field)\s+(\w+)",
    r"(?:remove|drop)(?:ed|ing)?\s+(?:column|field)\s+(\w+)",
    r"(?:change|update|modify)(?:ed|ing)?\s+(?:join|logic)",
    r"(?:rename|refactor)(?:ed|ing)?\s+(\w+)\s+to\s+(\w+)",
    r"(?:fix|correct)(?:ed|ing)?\s+(\w+)",
]
```

#### 2. Snowflake / Databricks / BigQuery (Warehouse Layer)

**Sources:**
- Query history / DDL audit logs
- `INFORMATION_SCHEMA.COLUMNS` (schema snapshots)
- Git (if using Flyway/Liquibase/Atlas)
- Terraform state (if IaC)

**Entities Extracted:**
| Entity | Source | Decision Types |
|--------|--------|----------------|
| Tables | DDL logs | created, dropped, altered |
| Columns | DDL logs | added, dropped, type_changed |
| Views | DDL logs | created, modified |
| Schemas | DDL logs | created, renamed |
| Clustering | DDL logs | key_changed |
| Partitioning | DDL logs | strategy_changed |

**Snowflake-Specific:**
```sql
-- Query to extract DDL history
SELECT
  query_id,
  query_text,
  user_name,
  start_time,
  -- Parse DDL type
  CASE
    WHEN query_text ILIKE 'CREATE%TABLE%' THEN 'table_created'
    WHEN query_text ILIKE 'ALTER%TABLE%ADD%COLUMN%' THEN 'column_added'
    WHEN query_text ILIKE 'ALTER%TABLE%DROP%COLUMN%' THEN 'column_dropped'
    WHEN query_text ILIKE 'DROP%TABLE%' THEN 'table_dropped'
  END as change_type
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE query_type = 'DDL'
  AND start_time > DATEADD(day, -90, CURRENT_TIMESTAMP())
ORDER BY start_time DESC;
```

**Databricks-Specific:**
```sql
-- Query Unity Catalog audit logs
SELECT
  event_time,
  action_name,
  request_params,
  user_identity
FROM system.access.audit
WHERE action_name IN ('createTable', 'alterTable', 'dropTable')
ORDER BY event_time DESC;
```

**BigQuery-Specific:**
```sql
-- Query INFORMATION_SCHEMA for DDL
SELECT
  ddl,
  creation_time,
  last_modified_time
FROM `project.dataset.INFORMATION_SCHEMA.TABLES`
WHERE table_type = 'BASE TABLE';
```

#### 3. Airflow / Dagster / Prefect (Orchestration Layer)

**Sources:**
- DAG definition files (Python)
- Git history on DAG changes
- Airflow metadata DB (optional)
- dagster.yaml / workspace.yaml

**Entities Extracted:**
| Entity | Source | Decision Types |
|--------|--------|----------------|
| DAGs | Python files | created, modified, removed |
| Tasks | Python files | added, removed, reordered |
| Schedules | Python files | changed |
| Dependencies | Python files | added, removed |
| Sensors | Python files | created, modified |
| Connections | Variables | added, modified |

**Airflow DAG Parsing:**
```python
# Extract decisions from Airflow DAGs
class AirflowExtractor:
    def extract_from_dag(self, dag_file: str) -> list[Decision]:
        # Parse AST to find:
        # - DAG definition (dag_id, schedule, default_args)
        # - Task definitions (task_id, dependencies)
        # - Significant patterns (retries, timeouts, pools)
        pass
```

**Git Analysis for Orchestrators:**
```python
# Patterns for orchestrator commits
patterns = [
    r"(?:change|update)(?:ed|ing)?\s+schedule\s+(?:to|from)",
    r"add(?:ed|ing)?\s+(?:retry|timeout|pool)",
    r"(?:add|remove)(?:ed|ing)?\s+(?:task|sensor|operator)",
    r"(?:reorder|change)(?:ed|ing)?\s+(?:dependencies|dag)",
]
```

#### 4. Looker / Tableau / Metabase (BI Layer)

**Sources:**
- LookML files (Git-based)
- Looker API (explores, views, measures)
- Tableau workbook files (.twb/.twbx)
- Metabase API (questions, dashboards)

**Entities Extracted:**
| Entity | Source | Decision Types |
|--------|--------|----------------|
| Explores | LookML | created, modified |
| Views | LookML | created, modified |
| Measures | LookML | added, modified, removed |
| Dimensions | LookML | added, modified, removed |
| Filters | LookML | added, modified |
| Dashboards | API | created, modified |

**LookML Parsing:**
```python
# Extract decisions from LookML
class LookMLExtractor:
    def extract_from_view(self, lookml_file: str) -> list[Decision]:
        # Parse LookML to find:
        # - View definitions
        # - Measure definitions (sql, type, filters)
        # - Dimension definitions
        # - Derived tables and their SQL
        pass
```

**Git Analysis for BI:**
```python
# Patterns for BI commits
patterns = [
    r"(?:add|create)(?:ed|ing)?\s+(?:measure|metric|dimension)",
    r"(?:change|update|fix)(?:ed|ing)?\s+(?:calculation|formula)",
    r"(?:add|remove)(?:ed|ing)?\s+filter",
    r"(?:update|change)(?:ed|ing)?\s+(?:dashboard|explore)",
]
```

---

## Feature Specification

### Phase 1: Core Platform + dbt

#### F1.1: CLI Initialization

```bash
# Initialize Lattice in a project
lattice init

# Creates:
# .lattice/
#   config.yml        # Configuration
#   corrections.jsonl # User corrections
#   index.db          # SQLite database
```

**Config file:**
```yaml
# .lattice/config.yml
version: 1

# Project info
project:
  name: "analytics"
  type: "dbt"  # dbt, airflow, looker, etc.

# Tool connections
tools:
  dbt:
    manifest_path: "target/manifest.json"
    project_path: "."

# Extraction settings
extraction:
  git:
    enabled: true
    depth: 1000  # commits to analyze
    branch: "main"
  llm:
    enabled: true
    provider: "anthropic"
    model: "claude-3-haiku-20240307"

# Retrieval settings
retrieval:
  token_budgets:
    tier1_immediate: 2500
    tier2_related: 2500
    tier3_global: 2000
  include_code_snippets: true

# Convention detection
conventions:
  enabled: true
  min_confidence: 0.7
  min_frequency: 3
```

#### F1.2: Indexing

```bash
# Full index
lattice index

# Incremental index (since last run)
lattice index --incremental

# Index specific tool
lattice index --tool dbt
```

**Indexing process:**
1. Parse tool-specific configs (manifest.json, etc.)
2. Extract entities and relationships
3. Analyze git history for decisions
4. Detect conventions from patterns
5. Generate embeddings for semantic search
6. Store in SQLite with FTS5 indexes

#### F1.3: Context Retrieval

```bash
# Get context for a task
lattice context "add revenue column to orders model"

# Get context for specific entity
lattice context --entity "dim_customer"

# Get context for files
lattice context --files "models/marts/orders.sql"

# Output formats
lattice context "..." --format json
lattice context "..." --format markdown
```

#### F1.4: MCP Server

```bash
# Start MCP server (stdio mode for Claude Desktop/Cursor)
lattice serve

# Start with HTTP transport
lattice serve --transport http --port 3001
```

**MCP Configuration for Claude Desktop:**
```json
{
  "mcpServers": {
    "lattice": {
      "command": "npx",
      "args": ["@altimate/lattice", "serve"],
      "cwd": "/path/to/your/project"
    }
  }
}
```

#### F1.5: Corrections Management

```bash
# Add a correction
lattice correct "dim_customer" "Always join on customer_key, not customer_id"

# Add with context
lattice correct "revenue" "Excludes refunds and taxes" --context "Per ASC 606 compliance"

# List corrections
lattice corrections list

# Remove a correction
lattice corrections remove <id>
```

#### F1.6: Decision Search

```bash
# Search decisions
lattice search "why was revenue column added"

# Search by entity
lattice search --entity "orders"

# Search by change type
lattice search --type "column_added"

# Search by date range
lattice search --since "2024-01-01" --until "2024-06-01"
```

### Phase 2: Warehouse Integration

#### F2.1: Snowflake Connector

```yaml
# .lattice/config.yml
tools:
  snowflake:
    enabled: true
    account: "${SNOWFLAKE_ACCOUNT}"
    user: "${SNOWFLAKE_USER}"
    password: "${SNOWFLAKE_PASSWORD}"
    warehouse: "COMPUTE_WH"
    database: "ANALYTICS"
    schema: "PUBLIC"

    # What to track
    track:
      - schema_changes
      - table_creates
      - column_modifications

    # History depth
    history_days: 90
```

#### F2.2: Databricks Connector

```yaml
tools:
  databricks:
    enabled: true
    host: "${DATABRICKS_HOST}"
    token: "${DATABRICKS_TOKEN}"

    # Unity Catalog settings
    catalog: "main"
    schema: "analytics"

    track:
      - ddl_changes
      - table_properties
```

#### F2.3: BigQuery Connector

```yaml
tools:
  bigquery:
    enabled: true
    project: "my-gcp-project"
    credentials: "${GOOGLE_APPLICATION_CREDENTIALS}"

    datasets:
      - "analytics"
      - "staging"

    track:
      - schema_changes
      - table_creates
```

### Phase 3: Orchestrator Integration

#### F3.1: Airflow Connector

```yaml
tools:
  airflow:
    enabled: true
    dag_folder: "dags/"

    # Optional: connect to Airflow metadata DB
    metadata_db: "${AIRFLOW_CONN_STRING}"

    track:
      - dag_changes
      - schedule_changes
      - task_dependencies
```

#### F3.2: Dagster Connector

```yaml
tools:
  dagster:
    enabled: true
    workspace_file: "workspace.yaml"

    track:
      - asset_changes
      - job_changes
      - schedule_changes
```

#### F3.3: Prefect Connector

```yaml
tools:
  prefect:
    enabled: true
    flows_folder: "flows/"

    # Optional: Prefect Cloud
    api_key: "${PREFECT_API_KEY}"

    track:
      - flow_changes
      - schedule_changes
```

### Phase 4: BI Integration

#### F4.1: Looker Connector

```yaml
tools:
  looker:
    enabled: true

    # Git-based LookML
    lookml_project: "looker/"

    # Optional: Looker API
    api_url: "${LOOKER_API_URL}"
    client_id: "${LOOKER_CLIENT_ID}"
    client_secret: "${LOOKER_CLIENT_SECRET}"

    track:
      - view_changes
      - measure_changes
      - explore_changes
```

#### F4.2: Tableau Connector

```yaml
tools:
  tableau:
    enabled: true

    # Workbook files
    workbooks_folder: "tableau/"

    # Optional: Tableau Server/Cloud
    server_url: "${TABLEAU_SERVER}"
    token: "${TABLEAU_TOKEN}"
    site: "default"

    track:
      - calculated_fields
      - data_source_changes
```

### Phase 5: GitHub Action

#### F5.1: PR Context Capture

```yaml
# .github/workflows/lattice-context.yml
name: Lattice Context

on:
  pull_request:
    types: [opened, synchronize]
  issue_comment:
    types: [created]

jobs:
  capture:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: altimate-ai/lattice-action@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          mode: auto  # auto, analyze, collect
```

#### F5.2: Question Generation

When a PR is opened, Lattice analyzes the diff and posts questions:

```markdown
## 🔍 Lattice Context Capture

I noticed some changes that future AI assistants might benefit from understanding:

### High Priority
- [ ] Why was `revenue` column added to `fct_orders`?
- [ ] Why did the join logic change in `dim_customer`?

### Medium Priority
- [ ] What's the purpose of `is_refunded` flag?

---
Reply with `@lattice` followed by your answers to capture this context.

Example:
> @lattice
> - revenue: Needed for the new finance dashboard (JIRA-123)
> - join logic: Switched to customer_key because customer_id isn't unique after migration
```

#### F5.3: Response Collection

When someone replies with `@lattice`, the action:
1. Parses the response
2. Matches answers to questions
3. Creates Decision records
4. Commits to `.lattice/decisions.jsonl`

---

## MCP Tools Reference

### get_context

Get context relevant to a task or entity.

**Parameters:**
```typescript
{
  task?: string;          // Natural language description
  entities?: string[];    // Specific entities
  files?: string[];       // File paths
  maxTokens?: number;     // Token budget (default: 8000)
  tools?: string[];       // Filter by tool
}
```

**Returns:**
```typescript
{
  tiers: {
    immediate: { content: string; tokens: number; sources: string[] };
    related: { content: string; tokens: number; sources: string[] };
    global: { content: string; tokens: number; sources: string[] };
  };
  decisions: Decision[];
  conventions: Convention[];
  corrections: Correction[];
  totalTokens: number;
}
```

**Example:**
```
AI: I need to add a revenue column to the orders model.

[Calls get_context with task="add revenue column to orders model"]

Response includes:
- Previous decisions about "orders" model
- Column naming conventions (detected: *_amount for money columns)
- Correction: "Revenue should exclude refunds per finance requirements"
- Related models in the DAG (customers, products)
```

### get_decision

Get decision history for a specific entity.

**Parameters:**
```typescript
{
  entity: string;         // Entity name
  limit?: number;         // Max decisions (default: 10)
  changeTypes?: string[]; // Filter by change type
}
```

**Returns:**
```typescript
{
  entity: string;
  entityType: string;
  decisions: Decision[];
}
```

### search_decisions

Search across all decisions.

**Parameters:**
```typescript
{
  query: string;          // Search query
  tools?: string[];       // Filter by tool
  changeTypes?: string[]; // Filter by change type
  since?: string;         // Date filter
  until?: string;         // Date filter
  limit?: number;         // Max results
}
```

**Returns:**
```typescript
{
  query: string;
  results: Decision[];
  totalCount: number;
}
```

### get_conventions

Get detected conventions and patterns.

**Parameters:**
```typescript
{
  tools?: string[];       // Filter by tool
  types?: string[];       // Convention types
  minConfidence?: number; // Min confidence (0-1)
}
```

**Returns:**
```typescript
{
  conventions: Convention[];
}
```

### add_correction

Add a user correction.

**Parameters:**
```typescript
{
  entity: string;         // Entity name
  correction: string;     // Correction text
  context?: string;       // When this applies
  scope?: 'global' | 'entity' | 'pattern';
  priority?: 'high' | 'medium' | 'low';
}
```

**Returns:**
```typescript
{
  id: string;
  created: boolean;
}
```

### get_corrections

Get corrections for an entity.

**Parameters:**
```typescript
{
  entity?: string;        // Filter by entity
  scope?: string;         // Filter by scope
}
```

**Returns:**
```typescript
{
  corrections: Correction[];
}
```

### explain_entity

Get a comprehensive explanation of an entity.

**Parameters:**
```typescript
{
  entity: string;         // Entity name
  includeHistory?: boolean;
  includeRelated?: boolean;
}
```

**Returns:**
```typescript
{
  entity: string;
  entityType: string;
  description: string;    // Generated summary
  decisions: Decision[];
  corrections: Correction[];
  conventions: Convention[];
  related: string[];      // Related entities
}
```

---

## CLI Reference

### Commands

```bash
# Initialization
lattice init [--force]

# Indexing
lattice index [--tool <tool>] [--incremental] [--verbose]

# Context retrieval
lattice context <query> [--entity <name>] [--files <paths>] [--format json|markdown]

# MCP server
lattice serve [--transport stdio|http] [--port <port>]

# Corrections
lattice correct <entity> <correction> [--context <text>] [--scope <scope>]
lattice corrections list [--entity <name>]
lattice corrections remove <id>

# Search
lattice search <query> [--entity <name>] [--type <type>] [--tool <tool>]
lattice search --since <date> --until <date>

# Status
lattice status
lattice stats

# Export
lattice export [--format json|csv] [--output <path>]
```

### Examples

```bash
# Initialize in a dbt project
cd my-dbt-project
lattice init

# Index the project
lattice index

# Get context for a task
lattice context "add customer lifetime value to dim_customer"

# Start MCP server for Claude Desktop
lattice serve

# Add a correction
lattice correct "revenue" "Always exclude refunds and taxes"

# Search for column-related decisions
lattice search "column" --type column_added --tool dbt

# Check status
lattice status

# Output:
# ✓ Indexed: 142 models, 1,847 columns
# ✓ Decisions: 523 extracted
# ✓ Conventions: 18 detected
# ✓ Corrections: 7 active
# Last indexed: 2 hours ago
```

---

## Configuration

### Full Configuration Reference

```yaml
# .lattice/config.yml
version: 1

# ═══════════════════════════════════════════════════════════════════
# PROJECT SETTINGS
# ═══════════════════════════════════════════════════════════════════

project:
  name: "analytics"
  description: "Main analytics data warehouse"

# ═══════════════════════════════════════════════════════════════════
# TOOL CONNECTIONS
# ═══════════════════════════════════════════════════════════════════

tools:
  # ─────────────────────────────────────────────────────────────────
  # dbt
  # ─────────────────────────────────────────────────────────────────
  dbt:
    enabled: true
    manifest_path: "target/manifest.json"
    project_path: "."
    profiles_path: "~/.dbt/profiles.yml"

  # ─────────────────────────────────────────────────────────────────
  # Snowflake
  # ─────────────────────────────────────────────────────────────────
  snowflake:
    enabled: false
    account: "${SNOWFLAKE_ACCOUNT}"
    user: "${SNOWFLAKE_USER}"
    password: "${SNOWFLAKE_PASSWORD}"
    warehouse: "COMPUTE_WH"
    database: "ANALYTICS"
    schema: "PUBLIC"
    history_days: 90
    track:
      - schema_changes
      - table_creates
      - column_modifications

  # ─────────────────────────────────────────────────────────────────
  # Databricks
  # ─────────────────────────────────────────────────────────────────
  databricks:
    enabled: false
    host: "${DATABRICKS_HOST}"
    token: "${DATABRICKS_TOKEN}"
    catalog: "main"
    schema: "analytics"
    track:
      - ddl_changes
      - table_properties

  # ─────────────────────────────────────────────────────────────────
  # BigQuery
  # ─────────────────────────────────────────────────────────────────
  bigquery:
    enabled: false
    project: "my-gcp-project"
    credentials: "${GOOGLE_APPLICATION_CREDENTIALS}"
    datasets:
      - "analytics"
    track:
      - schema_changes

  # ─────────────────────────────────────────────────────────────────
  # Airflow
  # ─────────────────────────────────────────────────────────────────
  airflow:
    enabled: false
    dag_folder: "dags/"
    metadata_db: "${AIRFLOW_CONN_STRING}"
    track:
      - dag_changes
      - schedule_changes
      - task_dependencies

  # ─────────────────────────────────────────────────────────────────
  # Dagster
  # ─────────────────────────────────────────────────────────────────
  dagster:
    enabled: false
    workspace_file: "workspace.yaml"
    track:
      - asset_changes
      - job_changes

  # ─────────────────────────────────────────────────────────────────
  # Looker
  # ─────────────────────────────────────────────────────────────────
  looker:
    enabled: false
    lookml_project: "looker/"
    api_url: "${LOOKER_API_URL}"
    client_id: "${LOOKER_CLIENT_ID}"
    client_secret: "${LOOKER_CLIENT_SECRET}"
    track:
      - view_changes
      - measure_changes

# ═══════════════════════════════════════════════════════════════════
# EXTRACTION SETTINGS
# ═══════════════════════════════════════════════════════════════════

extraction:
  # Git history analysis
  git:
    enabled: true
    depth: 1000
    branch: "main"
    include_merge_commits: false

  # LLM summarization for complex commits
  llm:
    enabled: true
    provider: "anthropic"  # anthropic, openai
    model: "claude-3-haiku-20240307"
    api_key: "${ANTHROPIC_API_KEY}"

    # When to use LLM
    triggers:
      min_diff_lines: 50      # Use LLM if diff > 50 lines
      complex_patterns: true  # Use LLM for refactors, renames

  # PR/Issue integration
  github:
    enabled: true
    token: "${GITHUB_TOKEN}"
    extract_pr_descriptions: true
    extract_pr_comments: true
    extract_issue_links: true

  # Jira/Linear integration
  issue_tracker:
    enabled: false
    type: "jira"  # jira, linear
    url: "${JIRA_URL}"
    token: "${JIRA_TOKEN}"

# ═══════════════════════════════════════════════════════════════════
# RETRIEVAL SETTINGS
# ═══════════════════════════════════════════════════════════════════

retrieval:
  # Token budgets per tier
  token_budgets:
    tier1_immediate: 2500
    tier2_related: 2500
    tier3_global: 2000

  # Content options
  include_code_snippets: true
  max_snippet_lines: 20
  include_diff_context: true

  # Relevance scoring
  scoring:
    recency_weight: 0.3       # Recent decisions score higher
    frequency_weight: 0.2     # Frequently referenced entities
    correction_weight: 0.5    # User corrections highest priority

# ═══════════════════════════════════════════════════════════════════
# CONVENTION DETECTION
# ═══════════════════════════════════════════════════════════════════

conventions:
  enabled: true
  min_confidence: 0.7
  min_frequency: 3

  # What to detect
  detect:
    - prefixes        # dim_, fct_, stg_
    - suffixes        # _id, _at, _date
    - case_patterns   # snake_case, camelCase
    - directory_structure
    - test_patterns

# ═══════════════════════════════════════════════════════════════════
# STORAGE
# ═══════════════════════════════════════════════════════════════════

storage:
  path: ".lattice"

  # Database settings
  database:
    type: "sqlite"
    wal_mode: true

  # Embeddings
  embeddings:
    enabled: true
    model: "text-embedding-3-small"
    dimensions: 512

# ═══════════════════════════════════════════════════════════════════
# PRIVACY & SECURITY
# ═══════════════════════════════════════════════════════════════════

privacy:
  # What NOT to index
  exclude_patterns:
    - "**/*.env"
    - "**/*secret*"
    - "**/*password*"
    - "**/credentials*"

  # Redaction
  redact:
    - email_addresses
    - ip_addresses
    - api_keys
```

---

## Roadmap

### Phase 1: Foundation + dbt (Weeks 1-6)

**Goal:** Prove value with dbt users

| Week | Milestone | Deliverables |
|------|-----------|--------------|
| 1-2 | Core infrastructure | SQLite storage, CLI skeleton, basic types |
| 3-4 | dbt extraction | Manifest parser, git history analyzer, decision extractor |
| 5 | Convention detection | Pattern mining, confidence scoring |
| 6 | MCP server | All core tools, Claude Desktop integration |

**Success Criteria:**
- [ ] 10 beta users running daily
- [ ] NPS > 30
- [ ] <5 second indexing for typical dbt project

### Phase 2: Warehouse Integration (Weeks 7-10)

**Goal:** Capture DDL decision context

| Week | Milestone | Deliverables |
|------|-----------|--------------|
| 7 | Snowflake connector | DDL extraction, schema snapshots |
| 8 | Databricks connector | Unity Catalog integration |
| 9 | BigQuery connector | INFORMATION_SCHEMA extraction |
| 10 | Cross-tool linking | Link dbt models to warehouse tables |

**Success Criteria:**
- [ ] 3 warehouse connectors working
- [ ] Decisions linked across dbt ↔ warehouse

### Phase 3: Orchestrator Integration (Weeks 11-14)

**Goal:** Capture pipeline decision context

| Week | Milestone | Deliverables |
|------|-----------|--------------|
| 11-12 | Airflow connector | DAG parsing, git analysis |
| 13 | Dagster connector | Asset/job extraction |
| 14 | Prefect connector | Flow extraction |

**Success Criteria:**
- [ ] 3 orchestrator connectors working
- [ ] Schedule/dependency decisions captured

### Phase 4: BI Integration (Weeks 15-18)

**Goal:** Capture metric decision context

| Week | Milestone | Deliverables |
|------|-----------|--------------|
| 15-16 | Looker connector | LookML parsing, API integration |
| 17 | Tableau connector | Workbook parsing |
| 18 | Cross-stack linking | Link metrics to dbt models |

**Success Criteria:**
- [ ] Measure/dimension decisions captured
- [ ] End-to-end lineage: BI ↔ dbt ↔ warehouse

### Phase 5: GitHub Action + Polish (Weeks 19-22)

**Goal:** Proactive context capture

| Week | Milestone | Deliverables |
|------|-----------|--------------|
| 19-20 | GitHub Action | PR analysis, question generation |
| 21 | Response collection | @lattice parsing, decision creation |
| 22 | Documentation & launch | Docs site, marketing, launch |

**Success Criteria:**
- [ ] GitHub Action working in 10+ repos
- [ ] 30%+ response rate on context questions

### Phase 6: Scale & Enterprise (Weeks 23+)

**Goal:** Enterprise readiness

| Feature | Description |
|---------|-------------|
| Team features | Shared corrections, role-based access |
| SSO/SAML | Enterprise authentication |
| Audit logging | Compliance requirements |
| Self-hosted option | On-prem deployment |
| API rate limiting | Multi-tenant support |

---

## Success Metrics

### Product Metrics

| Metric | Target (6 months) | Measurement |
|--------|-------------------|-------------|
| Daily Active Users | 500 | CLI + MCP usage |
| Projects Indexed | 1,000 | Unique .lattice folders |
| Decisions Extracted | 100K | Total across all users |
| Corrections Added | 5K | User-provided corrections |
| MCP Queries/Day | 10K | get_context calls |

### Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Extraction Accuracy | >85% | Sampled decision review |
| Retrieval Relevance | >80% | User feedback |
| Convention Precision | >90% | True positive rate |
| Index Time (dbt) | <10s | P95 for 200 models |
| Query Time | <500ms | P95 for MCP calls |

### Business Metrics

| Metric | Target (12 months) | Notes |
|--------|-------------------|-------|
| Paying Customers | 50 | Teams, not individuals |
| ARR | $300K | $500/mo avg per team |
| NPS | >40 | Quarterly survey |
| Churn | <5%/month | Logo churn |

### User Outcome Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Onboarding Time Reduction | 30% | Self-reported |
| AI Error Reduction | 40% | Before/after comparison |
| Code Review Time Reduction | 25% | Self-reported |

---

## Competitive Positioning

### Positioning Statement

> **For data teams** who use AI assistants to write SQL and build pipelines,
> **Lattice** is a context layer
> **that** automatically extracts institutional knowledge from git history and serves it via MCP,
> **unlike** data catalogs that require manual documentation or dbt MCP that only shows what exists,
> **Lattice** captures **why** decisions were made and learns from corrections.

### Competitive Matrix

| Capability | Lattice | Data Catalogs | dbt MCP | Dexicon |
|------------|---------|---------------|---------|---------|
| **Automatic extraction** | ✅ Git + LLM | ❌ Manual | ❌ Static | ✅ Sessions |
| **Decision history** | ✅ Core feature | ⚠️ Manual | ❌ No | ⚠️ Sessions |
| **Data stack native** | ✅ dbt, warehouse, BI | ✅ Broad | ✅ dbt only | ❌ Code only |
| **MCP server** | ✅ Yes | ⚠️ Coming | ✅ Yes | ✅ Yes |
| **User corrections** | ✅ Core feature | ⚠️ Comments | ❌ No | ❌ No |
| **Convention detection** | ✅ Automatic | ❌ No | ❌ No | ❌ No |
| **Zero behavior change** | ✅ Git-first | ❌ Requires input | ✅ Yes | ❌ Requires sessions |

### Differentiation Summary

1. **vs. Data Catalogs (Atlan, Alation)**: They require manual documentation. Lattice extracts automatically.

2. **vs. dbt MCP Server**: dbt serves "what exists" (metadata, lineage). Lattice serves "why it exists" (decisions, rationale).

3. **vs. Dexicon**: Dexicon captures coding sessions. Lattice extracts from git history + configs without requiring new behavior.

4. **vs. Manual ADRs**: ADRs require discipline to write. Lattice extracts from commits you're already making.

---

## Pricing Strategy

### Pricing Tiers

| Tier | Price | Limits | Target |
|------|-------|--------|--------|
| **Free** | $0 | 1 project, 100 decisions, dbt only | Individual evaluation |
| **Team** | $49/user/mo | 5 projects, unlimited decisions, all tools | Small data teams (3-10) |
| **Business** | $99/user/mo | Unlimited projects, SSO, audit logs | Mid-market (10-50) |
| **Enterprise** | Custom | Self-hosted, SLA, dedicated support | Enterprise (50+) |

### Pricing Rationale

- **Comparable to**: Monte Carlo ($2K-10K/mo), Atlan ($500-2K/mo per user)
- **Value anchored to**: Onboarding cost savings ($37K-75K per hire)
- **ROI calculation**: If Lattice saves 1 month onboarding time per hire, and you hire 3 people/year, that's $37K+ annual value vs. ~$6K cost (10 users × $49 × 12).

### Free Tier Strategy

Purpose: Product-led growth, individual adoption → team adoption

Limitations designed to push to Team:
- Single project only
- 100 decisions (fills up in ~1 week of active use)
- dbt only (no warehouse/orchestrator)
- No corrections (view only)

---

## Go-To-Market

### Launch Strategy

**Week 1-2: Private Beta**
- Recruit 20 beta users from dbt Slack
- Focus on feedback, not features
- Fix critical bugs

**Week 3-4: Public Beta**
- Launch on dbt Slack #tools-showcase
- Post on r/dataengineering
- Twitter/X announcement

**Week 5-8: Product Hunt + Content**
- Product Hunt launch
- Blog post: "How We Extract 'Why' from Git History"
- YouTube demo video

**Week 9+: Ongoing**
- Weekly changelog
- Community office hours
- Conference talks (Coalesce, Data Council)

### Channels

| Channel | Tactic | Goal |
|---------|--------|------|
| **dbt Slack** | #tools-showcase, #advice-dbt-help | Early adopters |
| **Reddit** | r/dataengineering, r/analytics | Awareness |
| **Twitter/X** | Data influencers, thought leadership | Brand |
| **LinkedIn** | Data team leads, managers | Enterprise |
| **Content** | Blog, YouTube, podcasts | SEO, education |
| **Partnerships** | dbt, Snowflake, Databricks partners | Distribution |

### Content Strategy

**Blog topics:**
1. "Why Data Catalogs Don't Solve the Tribal Knowledge Problem"
2. "How to Extract Decisions from Git History with LLMs"
3. "The Hidden Cost of Context Switching in Data Teams"
4. "MCP: The Protocol That Will Change How AI Understands Your Data"
5. "Onboarding Data Engineers in Weeks, Not Months"

**Demo scenarios:**
1. New hire asks: "Why is dim_customer built this way?"
2. AI suggests wrong join strategy, Lattice catches it
3. Team member leaves, knowledge stays
4. Convention enforcement without manual documentation

---

## Appendix

### A. Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         LATTICE SCHEMA                               │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   entities  │       │  decisions  │       │ corrections │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)     │       │ id (PK)     │
│ name        │◄──────┤ entity_id   │       │ entity_id   │──────►│
│ type        │       │ change_type │       │ correction  │       │
│ tool        │       │ why         │       │ context     │       │
│ path        │       │ source      │       │ added_by    │       │
│ metadata    │       │ source_ref  │       │ added_at    │       │
│ created_at  │       │ author      │       │ scope       │       │
│ updated_at  │       │ timestamp   │       │ priority    │       │
└─────────────┘       │ confidence  │       └─────────────┘
      │               │ tags        │
      │               │ tool        │
      │               └─────────────┘
      │
      │               ┌─────────────┐
      │               │ conventions │
      │               ├─────────────┤
      └──────────────►│ id (PK)     │
                      │ type        │
                      │ pattern     │
                      │ applies_to  │
                      │ examples    │
                      │ frequency   │
                      │ confidence  │
                      │ tool        │
                      └─────────────┘

┌─────────────┐       ┌─────────────┐
│relationships│       │  embeddings │
├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)     │
│ from_entity │       │ entity_id   │
│ to_entity   │       │ decision_id │
│ rel_type    │       │ vector      │
│ tool        │       │ text        │
└─────────────┘       └─────────────┘
```

### B. Sample Extracted Decisions

**Example 1: Column Addition (dbt)**
```json
{
  "id": "dec_abc123",
  "entity": "revenue",
  "entityType": "column",
  "changeType": "created",
  "why": "Needed for the new finance dashboard to track monthly recurring revenue. Per JIRA-456, finance team requested this metric.",
  "context": "Added to fct_orders model, calculated as sum of line_items excluding refunds",
  "source": "pr_description",
  "sourceRef": "PR #234",
  "author": "jane@company.com",
  "timestamp": "2024-03-15T10:30:00Z",
  "confidence": 0.92,
  "tags": ["finance", "metrics"],
  "tool": "dbt"
}
```

**Example 2: Join Logic Change (dbt)**
```json
{
  "id": "dec_def456",
  "entity": "dim_customer",
  "entityType": "model",
  "changeType": "logic_changed",
  "why": "Switched from customer_id to customer_key for joins because customer_id is not unique after the CRM migration. See incident report INC-789.",
  "context": "All downstream models should use customer_key for joins to this model",
  "source": "git_commit",
  "sourceRef": "a1b2c3d",
  "author": "bob@company.com",
  "timestamp": "2024-02-20T14:45:00Z",
  "confidence": 0.85,
  "tags": ["migration", "breaking-change"],
  "tool": "dbt"
}
```

**Example 3: Schedule Change (Airflow)**
```json
{
  "id": "dec_ghi789",
  "entity": "daily_revenue_pipeline",
  "entityType": "dag",
  "changeType": "schedule_changed",
  "why": "Changed from 6am to 4am UTC to ensure data is ready before European markets open. Requested by EMEA sales team.",
  "context": "Previous 6am schedule caused delays in morning reports",
  "source": "git_commit",
  "sourceRef": "d4e5f6g",
  "author": "alice@company.com",
  "timestamp": "2024-01-10T09:15:00Z",
  "confidence": 0.88,
  "tags": ["scheduling", "emea"],
  "tool": "airflow"
}
```

### C. Sample Conventions Detected

```json
[
  {
    "id": "conv_001",
    "type": "prefix",
    "pattern": "dim_",
    "appliesTo": ["model"],
    "examples": ["dim_customer", "dim_product", "dim_date", "dim_geography"],
    "frequency": 12,
    "confidence": 0.95,
    "tool": "dbt"
  },
  {
    "id": "conv_002",
    "type": "prefix",
    "pattern": "fct_",
    "appliesTo": ["model"],
    "examples": ["fct_orders", "fct_events", "fct_sessions"],
    "frequency": 8,
    "confidence": 0.92,
    "tool": "dbt"
  },
  {
    "id": "conv_003",
    "type": "suffix",
    "pattern": "_at",
    "appliesTo": ["column"],
    "examples": ["created_at", "updated_at", "deleted_at", "processed_at"],
    "frequency": 47,
    "confidence": 0.98,
    "tool": "dbt"
  },
  {
    "id": "conv_004",
    "type": "prefix",
    "pattern": "is_",
    "appliesTo": ["column"],
    "examples": ["is_active", "is_deleted", "is_primary", "is_verified"],
    "frequency": 23,
    "confidence": 0.96,
    "tool": "dbt"
  }
]
```

### D. LLM Prompts

**Decision Extraction Prompt:**
```
You are analyzing a git commit to extract the decision context.

Commit message: {commit_message}
Diff summary: {diff_summary}
Files changed: {files}

Extract the following:
1. What entity was changed? (model name, column name, etc.)
2. What type of change was it? (created, modified, removed, renamed, logic_changed)
3. Why was this change made? (the rationale, business reason)
4. Any additional context that would help someone understand this decision?

Respond in JSON format:
{
  "entity": "string",
  "entityType": "model|column|test|source|...",
  "changeType": "created|modified|removed|...",
  "why": "string - the rationale",
  "context": "string - additional context",
  "confidence": 0.0-1.0
}

If you cannot determine the "why" from the commit, set confidence to 0.5 or lower.
Only extract if there's meaningful decision context, not routine changes.
```

**Convention Detection Prompt:**
```
You are analyzing naming patterns in a codebase.

Entity names: {entity_names}
Entity type: {entity_type}

Identify naming conventions:
1. Common prefixes (e.g., "dim_", "fct_", "stg_")
2. Common suffixes (e.g., "_id", "_at", "_date")
3. Case patterns (snake_case, camelCase, etc.)
4. Other patterns

For each pattern found, provide:
- The pattern
- Examples that match
- Frequency (count)
- Confidence (0-1)

Only report patterns with 3+ occurrences and >70% confidence.
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-01-27 | Claude | Initial specification |

---

*This document is the source of truth for the Lattice Context Layer product. Update it as the product evolves.*
