"""Simplified MCP server implementation without requiring the SDK initially.

This is a minimal implementation for testing. For production, install the mcp package.
"""

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from lattice_context.core.types import Correction, CorrectionPriority, CorrectionScope
from lattice_context.mcp.retrieval import ContextRetriever
from lattice_context.storage.database import Database


class SimpleMCPServer:
    """Simplified MCP server using JSON-RPC over stdio."""

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.lattice_dir = project_path / ".lattice"
        self.db = Database(self.lattice_dir / "index.db")
        self.retriever = ContextRetriever(self.db)

    async def handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Handle a JSON-RPC request."""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "get_context",
                            "description": "Get relevant context for a data engineering task",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "task": {"type": "string"}
                                },
                                "required": ["task"]
                            }
                        },
                        {
                            "name": "add_correction",
                            "description": "Add a correction or important note",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "entity": {"type": "string"},
                                    "correction": {"type": "string"}
                                },
                                "required": ["entity", "correction"]
                            }
                        },
                        {
                            "name": "explain",
                            "description": "Explain an entity",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "entity": {"type": "string"}
                                },
                                "required": ["entity"]
                            }
                        }
                    ]
                }
            }

        if method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            if tool_name == "get_context":
                result = await self._handle_get_context(arguments)
            elif tool_name == "add_correction":
                result = await self._handle_add_correction(arguments)
            elif tool_name == "explain":
                result = await self._handle_explain(arguments)
            else:
                result = f"Unknown tool: {tool_name}"

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {"type": "text", "text": result}
                    ]
                }
            }

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "0.1.0",
                    "serverInfo": {
                        "name": "lattice-context",
                        "version": "0.1.0"
                    },
                    "capabilities": {
                        "tools": {}
                    }
                }
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }

    async def _handle_get_context(self, arguments: dict[str, Any]) -> str:
        """Handle get_context tool call."""
        task = arguments.get("task", "")
        response = await self.retriever.get_context(task)
        return self._format_context_response(response)

    async def _handle_add_correction(self, arguments: dict[str, Any]) -> str:
        """Handle add_correction tool call."""
        entity = arguments.get("entity", "")
        correction_text = arguments.get("correction", "")

        correction_id = hashlib.sha256(f"{entity}:{correction_text}".encode()).hexdigest()[:12]
        correction = Correction(
            id=f"corr_{correction_id}",
            entity=entity,
            entity_type=None,
            correction=correction_text,
            context="",
            added_by="user",
            added_at=datetime.now(),
            scope=CorrectionScope.ENTITY,
            priority=CorrectionPriority.HIGH,
        )

        self.db.add_correction(correction)
        return f"✓ Correction added for '{entity}'"

    async def _handle_explain(self, arguments: dict[str, Any]) -> str:
        """Handle explain tool call."""
        entity = arguments.get("entity", "")
        decisions = self.db.get_decisions_for_entity(entity)
        corrections = self.db.get_corrections(entity)

        if not decisions and not corrections:
            return f"No context found for '{entity}'"

        sections = [f"# {entity}\n"]

        if corrections:
            sections.append("## Important Notes\n")
            for corr in corrections:
                sections.append(f"- {corr.correction}")

        if decisions:
            sections.append("\n## Decision History\n")
            for dec in decisions[:5]:
                sections.append(f"- {dec.why}")

        return "\n".join(sections)

    def _format_context_response(self, response: dict[str, Any]) -> str:
        """Format context response."""
        sections = []

        corrections = response.get("corrections", [])
        if corrections:
            sections.append("## ⚠️ Important Notes\n")
            for corr in corrections[:3]:
                sections.append(f"- **{corr.entity}**: {corr.correction}")

        decisions = response.get("immediate_decisions", [])
        if decisions:
            sections.append("\n## Relevant Decisions\n")
            for dec in decisions[:5]:
                sections.append(f"- **{dec.entity}**: {dec.why}")

        conventions = response.get("conventions", [])
        if conventions:
            sections.append("\n## Conventions\n")
            for conv in conventions[:3]:
                sections.append(f"- {conv.pattern}: {', '.join(conv.examples[:3])}")

        if not sections:
            sections.append("No specific context found.")

        return "\n".join(sections)

    async def run(self) -> None:
        """Run the server."""
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break

                request = json.loads(line)
                response = await self.handle_request(request)
                print(json.dumps(response), flush=True)

            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }), flush=True)


async def serve_simple(project_path: Path) -> None:
    """Serve simple MCP server."""
    server = SimpleMCPServer(project_path)
    await server.run()
