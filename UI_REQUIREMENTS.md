# Lattice Context Layer - UI Requirements

## User Request
> "one thing you can focus on is to build a comprehensive UI for it"

## Proposed Screens

### 1. Dashboard
**Purpose:** Daily overview, recent decisions, gaps
**Who Uses It:** Everyone
**Key Features:**
- Recent decisions timeline
- Coverage metrics (% of entities documented)
- Gap analysis (entities without decisions)
- Activity feed (recent indexing, corrections)
- Quick stats (total decisions, conventions, corrections)

### 2. Entity Explorer
**Purpose:** Deep dive into any model/table/column
**Who Uses It:** ICs (Individual Contributors), during development
**Key Features:**
- Entity detail view
- Decision history for entity
- Related entities graph
- Corrections applied
- Convention compliance
- Quick edit/add corrections

### 3. Decision Graph
**Purpose:** Visualize how decisions connect
**Who Uses It:** Debugging, onboarding
**Key Features:**
- Interactive graph visualization
- Entity relationships
- Decision dependencies
- Click to explore
- Filter by entity type, time range
- Export graph image

### 4. Search Interface
**Purpose:** "Why was X built this way?"
**Who Uses It:** Everyone, on-demand
**Key Features:**
- Full-text search
- Filters (entity type, date, author, confidence)
- Sort by relevance/date/confidence
- Search suggestions
- Recent searches
- Save searches

### 5. ROI Dashboard
**Purpose:** Prove value to buyers
**Who Uses It:** Team Leads, Buyers
**Key Features:**
- Time saved metrics
- Questions answered
- Context retrievals
- Team adoption metrics
- Before/after comparisons
- Cost justification

---

## Technical Implementation Options

### Option 1: Web Dashboard (Recommended)
**Tech Stack:**
- FastAPI backend (Python)
- React/Vue frontend
- Recharts for visualizations
- D3.js for graph
- Tailwind CSS for styling

**Pros:**
- Professional UI
- Best user experience
- Easy to share (URL)
- Cross-platform
- Can integrate with existing tools

**Cons:**
- More complex to build
- Requires server

### Option 2: Terminal UI (TUI)
**Tech Stack:**
- Rich + Textual (Python)
- Terminal-based
- No browser needed

**Pros:**
- Fits CLI tool aesthetic
- No browser required
- Fast to build
- Works in SSH sessions

**Cons:**
- Limited interactivity
- Harder to visualize graphs
- Not as shareable

### Option 3: Desktop App
**Tech Stack:**
- Electron
- React/Vue
- Native look and feel

**Pros:**
- Native performance
- Offline capable
- OS integration

**Cons:**
- Most complex
- Large bundle size
- Separate codebase

---

## Recommended Approach

**Phase 1: Web Dashboard (MVP)**
Build a FastAPI-based web dashboard with:
1. Dashboard screen (overview)
2. Search interface (most requested)
3. Entity Explorer (developer focus)

**Phase 2: Advanced Features**
4. Decision Graph (visualization)
5. ROI Dashboard (buyer focus)

**Phase 3: Enhancement**
- Real-time updates
- Export capabilities
- Team sharing
- API for integrations

---

## Implementation Plan

### Step 1: Backend API
Create FastAPI server that exposes:
- GET /api/decisions - List decisions
- GET /api/decisions/:id - Get decision
- GET /api/search - Search decisions
- GET /api/entities - List entities
- GET /api/entities/:id - Entity details
- GET /api/stats - Dashboard stats
- GET /api/graph - Graph data

### Step 2: Frontend Structure
```
ui/
├── src/
│   ├── components/
│   │   ├── Dashboard.tsx
│   │   ├── EntityExplorer.tsx
│   │   ├── DecisionGraph.tsx
│   │   ├── Search.tsx
│   │   └── ROIDashboard.tsx
│   ├── api/
│   │   └── client.ts
│   └── App.tsx
├── package.json
└── vite.config.ts
```

### Step 3: Integration
- Add `lattice ui` command to start server
- Auto-open browser on launch
- Serve static files from FastAPI
- Use existing Database class

---

## Next Steps

1. Create FastAPI backend with API endpoints
2. Build React frontend with Vite
3. Implement Dashboard screen first
4. Add Search interface
5. Build Entity Explorer
6. Add Decision Graph visualization
7. Create ROI Dashboard
8. Package everything with `lattice ui` command

---

## User Value

**With UI:**
- ✅ Beautiful visualizations
- ✅ Easy exploration
- ✅ Team collaboration
- ✅ Proof of value
- ✅ Better onboarding

**vs CLI only:**
- ❌ Text-based output
- ❌ Limited exploration
- ❌ Hard to share
- ❌ No visualizations
- ❌ Steeper learning curve

**The UI will make Lattice accessible to non-technical stakeholders and dramatically improve the user experience.**
