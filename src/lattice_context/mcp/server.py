"""MCP server for serving context to AI assistants."""

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from lattice_context.core.types import (
    Correction,
    CorrectionPriority,
    CorrectionScope,
)
from lattice_context.mcp.retrieval import ContextRetriever
from lattice_context.storage.database import Database


class LatticeServer:
    """MCP server for Lattice Context Layer."""

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.lattice_dir = project_path / ".lattice"
        self.db = Database(self.lattice_dir / "index.db")
        self.retriever = ContextRetriever(self.db)
        self.server = Server("lattice-context")
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Setup MCP tool handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="get_context",
                    description="Get relevant context for a data engineering task. Use this when you need to understand project conventions, past decisions, or why things are built a certain way.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task": {
                                "type": "string",
                                "description": "What you're trying to do (e.g., 'add revenue column to orders model')",
                            },
                        },
                        "required": ["task"],
                    },
                ),
                Tool(
                    name="add_correction",
                    description="Teach Lattice something about this project. Use this to add important context that isn't captured elsewhere.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "entity": {
                                "type": "string",
                                "description": "Entity name (e.g., model name, column name)",
                            },
                            "correction": {
                                "type": "string",
                                "description": "The correction or important note",
                            },
                        },
                        "required": ["entity", "correction"],
                    },
                ),
                Tool(
                    name="explain",
                    description="Explain why an entity (model, column, etc.) exists and how it's built. Returns decision history and context.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "entity": {
                                "type": "string",
                                "description": "Entity name to explain",
                            },
                        },
                        "required": ["entity"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls."""
            if name == "get_context":
                return await self._handle_get_context(arguments)
            if name == "add_correction":
                return await self._handle_add_correction(arguments)
            if name == "explain":
                return await self._handle_explain(arguments)
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    async def _handle_get_context(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle get_context tool call."""
        task = arguments.get("task", "")

        if not task:
            return [TextContent(type="text", text="Error: task parameter is required")]

        # Retrieve context
        response = await self.retriever.get_context(task)

        # Format response
        formatted = self._format_context_response(response)

        return [TextContent(type="text", text=formatted)]

    async def _handle_add_correction(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle add_correction tool call."""
        entity = arguments.get("entity", "")
        correction_text = arguments.get("correction", "")

        if not entity or not correction_text:
            return [TextContent(type="text", text="Error: entity and correction are required")]

        # Create correction
        correction_id = hashlib.sha256(f"{entity}:{correction_text}".encode()).hexdigest()[:12]
        correction = Correction(
            id=f"corr_{correction_id}",
            entity=entity,
            entity_type=None,  # Will be inferred
            correction=correction_text,
            context="",
            added_by="user",
            added_at=datetime.now(),
            scope=CorrectionScope.ENTITY,
            priority=CorrectionPriority.HIGH,
        )

        self.db.add_correction(correction)

        return [TextContent(
            type="text",
            text=f"✓ Correction added for '{entity}'\n\nThis will be included in future context requests."
        )]

    async def _handle_explain(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle explain tool call."""
        entity = arguments.get("entity", "")

        if not entity:
            return [TextContent(type="text", text="Error: entity parameter is required")]

        # Get decisions for this entity
        decisions = self.db.get_decisions_for_entity(entity)
        corrections = self.db.get_corrections(entity)

        if not decisions and not corrections:
            return [TextContent(
                type="text",
                text=f"No context found for '{entity}'.\n\nConsider adding a correction with add_correction if you have important information about this entity."
            )]

        # Format explanation
        sections = [f"# {entity}\n"]

        if corrections:
            sections.append("## Important Notes\n")
            for corr in corrections:
                sections.append(f"- **{corr.correction}**")
                if corr.context:
                    sections.append(f"  - {corr.context}")
            sections.append("")

        if decisions:
            sections.append("## Decision History\n")
            for dec in decisions[:5]:  # Max 5 decisions
                timestamp_str = dec.timestamp.strftime("%Y-%m-%d")
                sections.append(f"### {dec.change_type.value.title()} ({timestamp_str})")
                sections.append(f"{dec.why}\n")
                if dec.context:
                    sections.append(f"*{dec.context}*\n")

        return [TextContent(type="text", text="\n".join(sections))]

    def _format_context_response(self, response: dict[str, Any]) -> str:
        """Format context response for AI consumption."""
        sections = []

        # High-priority corrections first
        corrections = response.get("corrections", [])
        if corrections:
            sections.append("## ⚠️ Important Notes\n")
            for corr in corrections[:3]:  # Max 3
                sections.append(f"- **{corr.entity}**: {corr.correction}")
                if corr.context:
                    sections.append(f"  - {corr.context}")
            sections.append("")

        # Relevant decisions
        decisions = response.get("immediate_decisions", [])
        if decisions:
            sections.append("## Relevant Decisions\n")
            for dec in decisions[:5]:  # Max 5
                sections.append(f"- **{dec.entity}** ({dec.change_type.value}): {dec.why}")
                if dec.context:
                    sections.append(f"  - Context: {dec.context}")
            sections.append("")

        # Conventions
        conventions = response.get("conventions", [])
        if conventions:
            sections.append("## Conventions to Follow\n")
            for conv in conventions[:3]:  # Max 3
                pattern_desc = f"{conv.pattern} for {', '.join(e.value for e in conv.applies_to)}"
                sections.append(f"- **{pattern_desc}**")
                sections.append(f"  - Examples: {', '.join(conv.examples[:3])}")
            sections.append("")

        # Related context
        related_decisions = response.get("related_decisions", [])
        if related_decisions:
            sections.append("## Related Context\n")
            for dec in related_decisions[:3]:  # Max 3
                sections.append(f"- {dec.entity}: {dec.why}")
            sections.append("")

        if not sections:
            sections.append("No specific context found. Proceeding with general best practices.")

        return "\n".join(sections)

    async def run(self) -> None:
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


async def serve(project_path: Path) -> None:
    """Serve MCP server."""
    server = LatticeServer(project_path)
    await server.run()
