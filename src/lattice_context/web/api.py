"""FastAPI backend for Lattice web interface."""

from __future__ import annotations

from typing import Optional

from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from lattice_context.storage.database import Database
from lattice_context.core.licensing import (
    get_current_tier,
    get_usage_stats,
    should_show_upgrade_prompt,
)


class StatsResponse(BaseModel):
    """Dashboard statistics."""
    total_entities: int
    total_decisions: int
    total_conventions: int
    total_corrections: int
    last_indexed_at: Optional[datetime]


class DecisionResponse(BaseModel):
    """Decision data."""
    id: str
    entity: str
    entity_type: str
    change_type: str
    why: str
    context: str
    source: str
    source_ref: str
    author: str
    timestamp: datetime
    confidence: float
    tags: list[str]
    tool: str


class SearchRequest(BaseModel):
    """Search request."""
    query: str
    limit: int = 20


def create_app(db_path: Path) -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="Lattice Context Layer",
        description="Institutional knowledge for AI assistants",
        version="0.1.0",
    )

    # Enable CORS for development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Database connection
    db = Database(db_path)

    @app.get("/api/stats", response_model=StatsResponse)
    async def get_stats():
        """Get dashboard statistics."""
        return StatsResponse(
            total_entities=db.count_entities(),
            total_decisions=db.count_decisions(),
            total_conventions=db.count_conventions(),
            total_corrections=db.count_corrections(),
            last_indexed_at=db.last_indexed_at(),
        )

    @app.get("/api/decisions", response_model=list[DecisionResponse])
    async def list_decisions(limit: int = 100, entity: Optional[str] = None):
        """List all decisions."""
        decisions = db.list_decisions(limit=limit)

        # Filter by entity if specified
        if entity:
            decisions = [d for d in decisions if entity.lower() in d.entity.lower()]

        return [
            DecisionResponse(
                id=d.id,
                entity=d.entity,
                entity_type=d.entity_type.value,
                change_type=d.change_type.value,
                why=d.why,
                context=d.context,
                source=d.source.value,
                source_ref=d.source_ref,
                author=d.author,
                timestamp=d.timestamp,
                confidence=d.confidence,
                tags=d.tags,
                tool=d.tool.value,
            )
            for d in decisions
        ]

    @app.get("/api/decisions/{decision_id}", response_model=DecisionResponse)
    async def get_decision(decision_id: str):
        """Get a specific decision."""
        # Get all decisions and find the matching one
        decisions = db.list_decisions(limit=10000)
        decision = next((d for d in decisions if d.id == decision_id), None)

        if not decision:
            raise HTTPException(status_code=404, detail="Decision not found")

        return DecisionResponse(
            id=decision.id,
            entity=decision.entity,
            entity_type=decision.entity_type.value,
            change_type=decision.change_type.value,
            why=decision.why,
            context=decision.context,
            source=decision.source.value,
            source_ref=decision.source_ref,
            author=decision.author,
            timestamp=decision.timestamp,
            confidence=decision.confidence,
            tags=decision.tags,
            tool=decision.tool.value,
        )

    @app.post("/api/search", response_model=list[DecisionResponse])
    async def search_decisions(request: SearchRequest):
        """Search decisions."""
        decisions = db.search_decisions(request.query, limit=request.limit)

        return [
            DecisionResponse(
                id=d.id,
                entity=d.entity,
                entity_type=d.entity_type.value,
                change_type=d.change_type.value,
                why=d.why,
                context=d.context,
                source=d.source.value,
                source_ref=d.source_ref,
                author=d.author,
                timestamp=d.timestamp,
                confidence=d.confidence,
                tags=d.tags,
                tool=d.tool.value,
            )
            for d in decisions
        ]

    @app.get("/api/conventions")
    async def list_conventions():
        """List detected conventions."""
        conventions = db.get_conventions()

        return [
            {
                "id": c.id,
                "type": c.type.value,
                "pattern": c.pattern,
                "description": c.description,
                "applies_to": [e.value for e in c.applies_to],
                "examples": c.examples,
                "frequency": c.frequency,
                "confidence": c.confidence,
                "detected_at": c.detected_at.isoformat(),
                "tool": c.tool.value,
            }
            for c in conventions
        ]

    @app.get("/api/corrections")
    async def list_corrections():
        """List user corrections."""
        corrections = db.get_corrections()

        return [
            {
                "id": c.id,
                "entity": c.entity,
                "entity_type": c.entity_type.value if c.entity_type else None,
                "correction": c.correction,
                "context": c.context,
                "added_by": c.added_by,
                "added_at": c.added_at.isoformat(),
                "scope": c.scope.value,
                "priority": c.priority.value,
            }
            for c in corrections
        ]

    @app.get("/api/entities")
    async def list_entities():
        """List unique entities."""
        decisions = db.list_decisions(limit=10000)

        # Group by entity
        entities = {}
        for d in decisions:
            if d.entity not in entities:
                entities[d.entity] = {
                    "entity": d.entity,
                    "entity_type": d.entity_type.value,
                    "decision_count": 0,
                    "last_updated": d.timestamp,
                }
            entities[d.entity]["decision_count"] += 1
            if d.timestamp > entities[d.entity]["last_updated"]:
                entities[d.entity]["last_updated"] = d.timestamp

        return list(entities.values())

    @app.get("/api/entities/{entity_name}")
    async def get_entity(entity_name: str):
        """Get entity details with all decisions."""
        decisions = db.get_decisions_for_entity(entity_name, limit=1000)
        corrections = db.get_corrections(entity=entity_name)

        if not decisions:
            raise HTTPException(status_code=404, detail="Entity not found")

        return {
            "entity": entity_name,
            "entity_type": decisions[0].entity_type.value,
            "decisions": [
                {
                    "id": d.id,
                    "change_type": d.change_type.value,
                    "why": d.why,
                    "context": d.context,
                    "source": d.source.value,
                    "source_ref": d.source_ref,
                    "author": d.author,
                    "timestamp": d.timestamp.isoformat(),
                    "confidence": d.confidence,
                    "tags": d.tags,
                    "tool": d.tool.value,
                }
                for d in decisions
            ],
            "corrections": [
                {
                    "id": c.id,
                    "correction": c.correction,
                    "context": c.context,
                    "added_by": c.added_by,
                    "added_at": c.added_at.isoformat(),
                    "priority": c.priority.value,
                }
                for c in corrections
            ],
        }

    @app.get("/api/graph")
    async def get_graph(entity_type: Optional[str] = None, limit: int = 100):
        """Get graph data for visualization.

        Returns nodes (decisions) and links (relationships) for D3.js force graph.
        """
        decisions = db.list_decisions(limit=limit)

        # Filter by entity type if specified
        if entity_type:
            decisions = [d for d in decisions if d.entity_type.value == entity_type]

        # Create nodes from decisions
        nodes = []
        for d in decisions:
            nodes.append({
                "id": d.id,
                "entity": d.entity,
                "type": d.entity_type.value,
                "why": d.why,
                "context": d.context,
                "author": d.author,
                "timestamp": d.timestamp.isoformat(),
                "confidence": d.confidence,
            })

        # Create links based on entity relationships
        links = []
        entity_decisions = {}

        # Group decisions by entity
        for d in decisions:
            if d.entity not in entity_decisions:
                entity_decisions[d.entity] = []
            entity_decisions[d.entity].append(d)

        # Link decisions about the same entity (chronologically)
        for entity, decs in entity_decisions.items():
            sorted_decs = sorted(decs, key=lambda x: x.timestamp)
            for i in range(len(sorted_decs) - 1):
                links.append({
                    "source": sorted_decs[i].id,
                    "target": sorted_decs[i + 1].id,
                    "type": "evolution",  # Same entity over time
                    "label": "evolves to"
                })

        # Link decisions with similar entities (e.g., dim_customer and fct_customer_orders)
        entities = list(entity_decisions.keys())
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                # Check if entities share keywords (simple heuristic)
                words1 = set(entity1.lower().replace('_', ' ').split())
                words2 = set(entity2.lower().replace('_', ' ').split())
                common = words1 & words2

                # If they share significant words, link their most recent decisions
                if len(common) >= 1 and len(common) / min(len(words1), len(words2)) > 0.3:
                    dec1 = entity_decisions[entity1][-1]  # Most recent
                    dec2 = entity_decisions[entity2][-1]
                    links.append({
                        "source": dec1.id,
                        "target": dec2.id,
                        "type": "related",  # Related entities
                        "label": "related to"
                    })

        return {
            "nodes": nodes,
            "links": links,
            "metadata": {
                "total_nodes": len(nodes),
                "total_links": len(links),
                "entity_types": list(set(n["type"] for n in nodes))
            }
        }

    @app.get("/api/tier")
    async def get_tier_info():
        """Get current tier and usage information."""
        tier = get_current_tier()
        decision_count = db.count_decisions()
        stats = get_usage_stats(tier, decision_count)

        return {
            **stats,
            "show_upgrade_prompt": should_show_upgrade_prompt(tier, decision_count),
            "upgrade_url": "https://altimate.ai/lattice/upgrade",
        }

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "ok"}

    # Serve static files
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

        @app.get("/")
        async def serve_index():
            """Serve the main HTML page."""
            return FileResponse(str(static_dir / "index.html"))

    return app
