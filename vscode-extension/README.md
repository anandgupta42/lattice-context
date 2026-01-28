# Lattice Context for GitHub Copilot

Provides your team's institutional knowledge to GitHub Copilot, improving code suggestions with decisions, conventions, and business logic captured by Lattice.

## Features

- **Automatic Context**: Lattice context server runs in background and provides institutional knowledge to Copilot
- **File-Specific Context**: Get relevant decisions and conventions for the file you're editing
- **Chat Integration**: Ask Copilot Chat questions with your team's institutional knowledge
- **Zero Configuration**: Automatically detects Lattice projects and starts serving context

## Requirements

- [Lattice Context Layer](https://github.com/altimate-ai/lattice-context) installed (`pip install lattice-context`)
- GitHub Copilot subscription
- VS Code 1.85.0 or higher

## Installation

1. Install the extension from VS Code Marketplace
2. Install Lattice: `pip install lattice-context`
3. Initialize Lattice in your project: `lattice init && lattice index`
4. Extension will auto-start the context server

## Usage

### Automatic Context for Copilot

Once installed, the extension automatically provides context to GitHub Copilot. When you:

- Write code in a file
- Ask Copilot for suggestions
- Use Copilot Chat

Copilot will have access to your team's:
- Naming conventions (e.g., `_amount` not `_percent`)
- Business rules (e.g., "exclude tax from revenue per ASC 606")
- Migration decisions (e.g., "use customer_key not customer_id")
- Implementation patterns

### Commands

**Lattice: Start Context Server** - Manually start the context server
**Lattice: Stop Context Server** - Stop the context server
**Lattice: Get Context for Current File** - View context for active file

### Settings

- `lattice.serverPort`: Port for context server (default: 8081)
- `lattice.autoStart`: Auto-start server on VS Code startup (default: true)
- `lattice.maxContextResults`: Max context items to provide (default: 5)

## How It Works

1. **Background Server**: Extension starts a local HTTP server (`lattice copilot`)
2. **Context Extraction**: Server reads your `.lattice/index.db` for decisions and conventions
3. **Copilot Integration**: Provides context via REST API that Copilot can query
4. **Better Suggestions**: Copilot uses institutional knowledge for more accurate code

## Example

**Without Lattice:**
```python
# Copilot suggests (wrong convention):
discount_percent = 0.1
```

**With Lattice:**
```python
# Copilot suggests (correct convention from team knowledge):
discount_amount = order_total * 0.1  # Uses _amount suffix per team convention
```

## Troubleshooting

**Server won't start:**
- Make sure `lattice` is installed: `pip install lattice-context`
- Check if project has `.lattice/` directory: `lattice init && lattice index`
- View output: `View > Output > Lattice Context`

**No context appearing:**
- Verify server is running: Check status bar or run "Start Context Server"
- Index your project: `lattice index`
- Check server health: `curl http://localhost:8081/health`

**Port already in use:**
- Change port in settings: `lattice.serverPort`
- Stop conflicting process on port 8081

## API Endpoints

The context server provides these endpoints:

- `POST /context` - Get context for a query
- `POST /context/file` - Get context for a specific file
- `POST /context/entity` - Get all context for an entity
- `POST /context/chat` - Get formatted context for Copilot Chat
- `GET /context/all` - Export all context
- `GET /health` - Health check

## Support

- [Documentation](https://github.com/altimate-ai/lattice-context)
- [Issues](https://github.com/altimate-ai/lattice-context/issues)
- [Discussions](https://github.com/altimate-ai/lattice-context/discussions)

## Research

This extension is based on research showing:
- AI tools have only 21.8% success rate on repository-level code without context
- External tools providing context improve AI suggestions by 18-250%
- 37.9% of developers use GitHub Copilot

With Lattice, Copilot gets the context it needs to provide team-specific, convention-aware suggestions.

## License

MIT
