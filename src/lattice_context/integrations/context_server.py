"""
Universal Context Server for all AI coding tools.

Provides Lattice context to Cursor, Windsurf, VS Code, and any tool
that can make HTTP requests.
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel
from enum import Enum

from lattice_context.integrations.copilot import CopilotContextProvider
from lattice_context.core.licensing import get_current_tier, can_use_api_access


class ToolType(str, Enum):
    """Supported AI coding tools."""
    CURSOR = "cursor"
    WINDSURF = "windsurf"
    VSCODE = "vscode"
    COPILOT = "copilot"
    GENERIC = "generic"


class FormatType(str, Enum):
    """Output format types."""
    MARKDOWN = "markdown"
    JSON = "json"
    PLAIN = "plain"


class UniversalContextRequest(BaseModel):
    """Universal context request."""

    query: str
    tool: ToolType = ToolType.GENERIC
    format: FormatType = FormatType.MARKDOWN
    max_results: int = 5


class UniversalContextResponse(BaseModel):
    """Universal context response."""

    context: str
    format: str
    tool: str
    has_results: bool
    metadata: dict


class ToolFormatter:
    """Format context for specific AI tools."""

    @staticmethod
    def format_for_cursor(context: str, decisions: list) -> str:
        """Format context for Cursor AI.

        Cursor prefers markdown with clear sections and code blocks.
        """
        if not decisions:
            return "No relevant context found."

        formatted = "# Context from Lattice\n\n"
        formatted += "Your team's institutional knowledge:\n\n"

        for i, d in enumerate(decisions, 1):
            formatted += f"## {i}. {d['entity']}\n\n"
            formatted += f"**Why**: {d['why']}\n\n"

            if d.get('context'):
                formatted += f"**Details**: {d['context']}\n\n"

            formatted += f"*Source*: {d['source']} by {d['author']}\n\n"
            formatted += "---\n\n"

        return formatted

    @staticmethod
    def format_for_windsurf(context: str, decisions: list) -> str:
        """Format context for Windsurf.

        Windsurf prefers concise, bullet-point style.
        """
        if not decisions:
            return "No context available"

        formatted = "📚 Team Knowledge:\n\n"

        for d in decisions:
            formatted += f"• **{d['entity']}**: {d['why']}\n"
            if d.get('context'):
                formatted += f"  └─ {d['context']}\n"

        return formatted

    @staticmethod
    def format_for_vscode(context: str, decisions: list) -> str:
        """Format context for VS Code extensions.

        VS Code prefers structured markdown with clear headers.
        """
        if not decisions:
            return "## No Context Found\n\nNo relevant institutional knowledge for this query."

        formatted = "## Lattice Context\n\n"
        formatted += "Institutional knowledge from your team:\n\n"

        for d in decisions:
            formatted += f"### {d['entity']}\n\n"
            formatted += f"> {d['why']}\n\n"

            if d.get('context'):
                formatted += f"{d['context']}\n\n"

            formatted += f"*By {d['author']} via {d['source']}*\n\n"

        return formatted

    @staticmethod
    def format_plain(decisions: list) -> str:
        """Format as plain text."""
        if not decisions:
            return "No context found."

        lines = []
        for d in decisions:
            lines.append(f"{d['entity']}: {d['why']}")
            if d.get('context'):
                lines.append(f"  {d['context']}")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def format_json(decisions: list) -> dict:
        """Format as JSON (return dict, FastAPI handles serialization)."""
        return {
            "decisions": decisions,
            "count": len(decisions)
        }


def create_universal_context_server(project_root: Path = Path(".")) -> FastAPI:
    """Create universal context API server.

    Args:
        project_root: Root directory of the project

    Returns:
        FastAPI application
    """
    app = FastAPI(
        title="Lattice Universal Context API",
        description="Provides institutional knowledge to all AI coding tools",
        version="1.0.0",
    )

    # CORS middleware for browser-based tools
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
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

    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "name": "Lattice Universal Context API",
            "version": "1.0.0",
            "supported_tools": [tool.value for tool in ToolType],
            "supported_formats": [fmt.value for fmt in FormatType],
            "endpoints": {
                "POST /v1/context": "Get context for any tool",
                "POST /v1/context/cursor": "Cursor-specific endpoint",
                "POST /v1/context/windsurf": "Windsurf-specific endpoint",
                "POST /v1/context/vscode": "VS Code-specific endpoint",
                "GET /health": "Health check"
            }
        }

    @app.post("/v1/context", response_model=UniversalContextResponse)
    async def get_universal_context(request: UniversalContextRequest):
        """Universal context endpoint for all tools.

        Args:
            request: Context request with query, tool, and format

        Returns:
            Formatted context for the specified tool
        """
        check_tier_access()  # Enforce tier limits

        if not provider:
            raise HTTPException(
                status_code=503,
                detail="Lattice not indexed. Run 'lattice init && lattice index' first.',
            )

        # Get context from provider - always use search for consistency
        search_results = provider.db.search_decisions(request.query, limit=request.max_results)
        decisions = [
            {
                "entity": d.entity,
                "why": d.why,
                "context": d.context,
                "source": d.source.value,
                "author": d.author,
                "timestamp": d.timestamp.isoformat(),
            }
            for d in search_results
        ]

        # Format based on tool and format
        formatter = ToolFormatter()

        if request.format == FormatType.JSON:
            context = formatter.format_json(decisions)
            context_str = str(context)  # For response
        elif request.tool == ToolType.CURSOR:
            context_str = formatter.format_for_cursor("", decisions)
        elif request.tool == ToolType.WINDSURF:
            context_str = formatter.format_for_windsurf("", decisions)
        elif request.tool == ToolType.VSCODE:
            context_str = formatter.format_for_vscode("", decisions)
        elif request.format == FormatType.PLAIN:
            context_str = formatter.format_plain(decisions)
        else:
            # Default markdown
            context_str = formatter.format_for_cursor("", decisions)

        return UniversalContextResponse(
            context=context_str,
            format=request.format.value,
            tool=request.tool.value,
            has_results=len(decisions) > 0,
            metadata={
                "decision_count": len(decisions),
                "query": request.query,
            }
        )

    @app.post("/v1/context/cursor")
    async def get_cursor_context(query: str, max_results: int = 5):
        """Cursor-specific context endpoint.

        Shortcut for Cursor integration.
        """
        request = UniversalContextRequest(
            query=query,
            tool=ToolType.CURSOR,
            format=FormatType.MARKDOWN,
            max_results=max_results
        )
        return await get_universal_context(request)

    @app.post("/v1/context/windsurf")
    async def get_windsurf_context(query: str, max_results: int = 5):
        """Windsurf-specific context endpoint.

        Shortcut for Windsurf integration.
        """
        request = UniversalContextRequest(
            query=query,
            tool=ToolType.WINDSURF,
            format=FormatType.MARKDOWN,
            max_results=max_results
        )
        return await get_universal_context(request)

    @app.post("/v1/context/vscode")
    async def get_vscode_context(query: str, max_results: int = 5):
        """VS Code-specific context endpoint.

        Shortcut for VS Code extensions.
        """
        request = UniversalContextRequest(
            query=query,
            tool=ToolType.VSCODE,
            format=FormatType.MARKDOWN,
            max_results=max_results
        )
        return await get_universal_context(request)

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "indexed": provider is not None,
            "api_version": "1.0.0"
        }

    return app


def start_server(
    project_root: Path = Path("."),
    port: int = 8082,
    host: str = "0.0.0.0",
):
    """Start the universal context server.

    Args:
        project_root: Root directory of the project
        port: Port to run on (default: 8082)
        host: Host to bind to (default: 0.0.0.0)
    """
    app = create_universal_context_server(project_root)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
