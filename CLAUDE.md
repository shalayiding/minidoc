# llm2page

MiniDoc DSL → HTML compiler. LLM outputs compact DSL (~300 token), compiler renders it into a full HTML page with Pico CSS + Chart.js.

## Project layout

```
llm2page/          ← Python package (parser, renderer, compiler, cli)
examples/          ← .minidoc sample files and compiled .html output
mcp/               ← MCP server (to be built — Week 2)
```

## Dev setup

```bash
uv venv && uv pip install -e .
uv run python -c "from llm2page import compile_to_html; print('ok')"
```

## Running

```bash
# compile a .minidoc file
uv run python -m llm2page.cli examples/q3_report.minidoc -o examples/q3_report.html

# or via CLI entry point
uv run llm2page examples/q3_report.minidoc -o out.html
```

## Stack

| Layer | Choice |
|-------|--------|
| CSS | Pico CSS CDN (classless, CSS-variable theming) |
| Charts | Chart.js CDN (canvas-based, DSL→JS mapping) |
| Packaging | uv + pyproject.toml |
| MCP server | fastmcp (Week 2) |

## Commit style

Short imperative messages, no co-author trailer. Example: `add chart renderer` not `Add Chart.js rendering support for bar/line/pie chart types`.

## MiniDoc DSL — how to generate reports

@SYSTEM_PROMPT.md
