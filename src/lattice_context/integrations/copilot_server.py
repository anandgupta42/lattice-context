"""
HTTP server for GitHub Copilot integration.

Provides a REST API that Copilot extensions can query for context.
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel

from lattice_context.integrations.copilot import CopilotContextProvider
from lattice_context.core.licensing import get_current_tier, can_use_api_access


class ContextRequest(BaseModel):
    """Request for context."""

    query: str
    max_results: int = 5


class ContextResponse(BaseModel):
    """Response with context."""

    context: str
    has_results: bool


class EntityContextRequest(BaseModel):
    """Request for entity-specific context."""

    entity: str


def create_copilot_server(project_root: Path = Path(".")) -> FastAPI:
    """Create FastAPI server for Copilot integration.

    Args:
        project_root: Root directory of the project

    Returns:
        FastAPI application
    """
    app = FastAPI(
        title="Lattice Copilot Context Server",
        description="Provides institutional knowledge to GitHub Copilot",
        version="1.0.0",
    )

    # CORS middleware for browser-based extensions
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, restrict this
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize context provider
    try:
        provider = CopilotContextProvider(project_root)
    except FileNotFoundError as e:
        print(f"Warning: {e}")
        print("Server will start but return empty context until indexed.")
        provider = None

    # Check tier for API access
    def check_tier_access():
        """Check if current tier allows API access."""
        tier = get_current_tier()
        if not can_use_api_access(tier):
            raise HTTPException(
                status_code=403,
                detail=(
                    "REST API access requires Team tier or higher. "
                    "Free tier is limited to MCP (Claude Desktop) access only. "
                    "Run 'lattice upgrade' for pricing."
                ),
            )

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "indexed": provider is not None,
        }

    @app.post("/context", response_model=ContextResponse)
    async def get_context(request: ContextRequest):
        """Get context for a query.

        Args:
            request: Context request with query

        Returns:
            Context response
        """
        check_tier_access()  # Enforce tier limits

        if not provider:
            raise HTTPException(
                status_code=503,
                detail="Lattice not indexed. Run 'lattice init && lattice index' first.",
            )

        context = provider.get_context_for_query(
            request.query, max_results=request.max_results
        )

        return ContextResponse(
            context=context,
            has_results=bool(context),
        )

    @app.post("/context/file")
    async def get_file_context(request: ContextRequest):
        """Get context for a specific file.

        Args:
            request: Request with file path

        Returns:
            Context response
        """
        check_tier_access()  # Enforce tier limits

        if not provider:
            raise HTTPException(
                status_code=503,
                detail="Lattice not indexed.",
            )

        context = provider.get_context_for_file(
            request.query, max_results=request.max_results
        )

        return ContextResponse(
            context=context,
            has_results=bool(context),
        )

    @app.post("/context/entity")
    async def get_entity_context(request: EntityContextRequest):
        """Get all context for an entity.

        Args:
            request: Request with entity name

        Returns:
            Complete entity context
        """
        check_tier_access()  # Enforce tier limits

        if not provider:
            raise HTTPException(
                status_code=503,
                detail="Lattice not indexed.",
            )

        return provider.get_context_for_entity(request.entity)

    @app.get("/context/all")
    async def get_all_context():
        """Export all context.

        Returns:
            Complete context database
        """
        check_tier_access()  # Enforce tier limits

        if not provider:
            raise HTTPException(
                status_code=503,
                detail="Lattice not indexed.",
            )

        return provider.export_all_context()

    @app.post("/context/chat")
    async def get_chat_context(request: ContextRequest):
        """Get context formatted for Copilot Chat.

        Args:
            request: Chat query

        Returns:
            Formatted context for chat
        """
        check_tier_access()  # Enforce tier limits

        if not provider:
            raise HTTPException(
                status_code=503,
                detail="Lattice not indexed.",
            )

        context = provider.format_for_copilot_chat(request.query)

        return ContextResponse(
            context=context,
            has_results=bool(context),
        )

    return app


def start_server(
    project_root: Path = Path("."),
    port: int = 8081,
    host: str = "0.0.0.0",
):
    """Start the Copilot context server.

    Args:
        project_root: Root directory of the project
        port: Port to run on
        host: Host to bind to
    """
    app = create_copilot_server(project_root)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
