# minidoc

MiniDoc DSL → HTML compiler. LLM outputs compact DSL (~300 tokens), compiler renders it into a full HTML page with Pico CSS + Chart.js + Mermaid + highlight.js.

## Project layout

```
minidoc/    ← Python package (parser, renderer, compiler, cli)
examples/    ← .minidoc sample files
mcp/         ← MCP server (FastMCP, stdio transport)
result/      ← compiled HTML output (gitignored)
```

## Dev setup

```bash
uv venv && uv pip install -e .
uv run python -c "from minidoc import compile_to_html; print('ok')"
```

## Running

```bash
# compile a .minidoc file
uv run minidoc examples/netflix_architecture.minidoc -o result/out.html

# start MCP server
uv run python mcp/server.py
```

## Stack

| Layer | Choice |
|-------|--------|
| CSS | Pico CSS v2 CDN (classless, CSS-variable theming) |
| Charts | Chart.js CDN |
| Diagrams | Mermaid.js v11 ESM CDN |
| Syntax highlight | highlight.js CDN (github-dark theme) |
| Packaging | uv + pyproject.toml |
| MCP server | FastMCP (stdio) |

## Commit style

Short imperative messages, no co-author trailer. Example: `add chart renderer` not `Add Chart.js rendering support for bar/line/pie chart types`.

## MiniDoc DSL — how to generate reports

@SYSTEM_PROMPT.md
