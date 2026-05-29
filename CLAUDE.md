# minidoc

A compact DSL → HTML compiler built for LLMs. LLM outputs minidoc DSL, compiler renders it into a polished self-contained HTML page with Pico CSS + Chart.js + Mermaid + highlight.js.

PyPI package: `minidoc-dsl` · Import: `from minidoc import compile_to_html` · CLI: `minidoc` · MCP: `minidoc-mcp`

## Project layout

```
minidoc/      ← Python package (parser, renderer, compiler, cli, _mcp)
showcase/     ← example .minidoc + .md source files (5 scenarios)
docs/         ← compiled HTML for GitHub Pages (gittracked)
result/       ← local compiled output (gitignored)
.github/workflows/publish.yml  ← auto-publish to PyPI on git tag
```

## Dev setup

```bash
uv venv && uv pip install -e .
uv run python -c "from minidoc import compile_to_html; print('ok')"
```

## Running

```bash
# compile a .minidoc file
uv run minidoc showcase/q3_business_report.minidoc -o result/out.html

# run MCP server locally
uv run minidoc-mcp
```

## Publishing

Bump version in `pyproject.toml`, then:

```bash
git tag v0.x.x && git push origin main --tags
```

GitHub Actions builds and publishes to PyPI automatically.

## Stack

| Layer | Choice |
|-------|--------|
| CSS | Pico CSS v2 CDN (classless, CSS-variable theming) |
| Charts | Chart.js CDN |
| Diagrams | Mermaid.js v11 ESM CDN |
| Syntax highlight | highlight.js CDN (github-dark theme) |
| Packaging | uv + pyproject.toml (hatchling) |
| MCP server | FastMCP (stdio), entry point `minidoc-mcp` |

## Commit style

Short imperative messages, no co-author trailer. Example: `add chart renderer` not `Add Chart.js rendering support for bar/line/pie chart types`.

## MiniDoc DSL — how to generate reports

@SYSTEM_PROMPT.md
