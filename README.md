<div align="center">

# minidoc

**Stop writing documentation in Markdown. Write it once, render it beautifully.**

A compact DSL that compiles to polished, self-contained HTML — with charts, diagrams, tabs, metrics, and syntax highlighting. Write the same amount, get dramatically more.

[![PyPI](https://img.shields.io/pypi/v/minidoc-dsl?color=blue)](https://pypi.org/project/minidoc-dsl)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

[English](README.md) · [中文](README_zh.md)

**[→ Live examples](https://shalayiding.github.io/minidoc/)**

</div>

---

## The problem with Markdown documentation

Markdown is everywhere — READMEs, wikis, design docs, postmortems. It's easy to write, but hard to read at scale. By the time a document has tables, code blocks, and a system diagram, it's a wall of symbols that no one wants to open.

minidoc was built to fix that. Write a compact DSL (or have an LLM write it), get back a self-contained HTML file with real charts, interactive tabs, Mermaid diagrams, and a clean visual layout. The kind of document people actually open.

## Real benchmark: URL shortener system design

We compiled the same system design document in both Markdown and minidoc DSL and measured the result.

| | Markdown | minidoc DSL |
|---|---|---|
| Input size to write | 3,908 tokens | 4,598 tokens (~same effort) |
| Output | Flat text + tables | **Interactive HTML, 13,394 tokens of rendered output** |
| Charts | ❌ not supported | ✅ Chart.js — bar, line, pie, doughnut |
| Architecture diagrams | ❌ not supported | ✅ Mermaid — flowchart, sequence, ER |
| Tabs / accordions | ❌ not supported | ✅ built-in |
| KPI / metric cards | ❌ not supported | ✅ built-in |
| Syntax highlighting | Basic (renderer-dependent) | ✅ highlight.js, github-dark |
| Shareable | Needs a Markdown renderer | ✅ Open in any browser, no tools needed |

You write roughly the same amount. minidoc compiles it into something Markdown never could.

> Source: [`benchmark/url_shortener/`](benchmark/url_shortener/) — minidoc DSL vs Markdown, measured with `tiktoken` (cl100k_base).

---

## Quick start

```bash
pip install minidoc
```

Create `report.minidoc`:

```
@doc title="Q3 Report" theme=light

# Q3 Business Review

[columns]
[col][metric label="MRR" value="$48K" trend=+12% color=green][/col]
[col][metric label="Churn" value="2.1%" trend=-0.4% color=blue][/col]
[col][metric label="NPS" value="61" trend=+8 color=purple][/col]
[/columns]

[chart type=bar title="Monthly Revenue"
  Jan=38 Feb=41 Mar=44 Apr=46 May=48
]

[table cols="Initiative,Owner,Status"
  Mobile redesign | Design team | ✅ Done
  API v2          | Backend     | 🔄 In progress
  SOC 2           | Security    | 📋 Planned
]
```

Compile:

```bash
minidoc report.minidoc -o report.html
```

Open `report.html` in any browser. No internet required after compile.

---

## Features

- **Token-efficient** — the entire DSL reference fits in a single system prompt
- **LLM-reliable** — constrained syntax means fewer hallucinations and malformed output
- **Zero runtime** — compiled HTML is fully self-contained; share it as an email attachment or static file
- **Rich component library** — metrics, KPIs, charts, tables, diagrams, code blocks, timelines, tabs, accordions
- **MCP server** — native integration with Claude and any MCP-compatible agent
- **Dark mode** — `theme=dark` via Pico CSS CSS variables
- **Mermaid diagrams** — flowchart, sequence, ER, Gantt — all declarative
- **Syntax highlighting** — 100+ languages via highlight.js

---

## Usage

### CLI

```bash
# Compile a file
minidoc report.minidoc -o output.html

# Read from stdin
echo '@doc title="Hello" theme=light
# Hello World' | minidoc -o hello.html
```

### Python API

```python
from minidoc import compile_to_html

dsl = """
@doc title="My Report" theme=light
# Hello
[metric label="Users" value="1,240" color=blue]
"""

html = compile_to_html(dsl)
with open("report.html", "w") as f:
    f.write(html)
```

### MCP server (for Claude and LLM agents)

Start the server:

```bash
uv run python mcp/server.py
```

Add to `.mcp.json` (or Claude Code settings):

```json
{
  "mcpServers": {
    "minidoc": {
      "type": "stdio",
      "command": "uvx",
      "args": ["minidoc-mcp"]
    }
  }
}
```

**Available tools:**

| Tool | Description |
|------|-------------|
| `render_and_open(dsl, name?)` | Compile DSL, save to `result/`, open in browser |
| `render_minidoc(dsl, name?)` | Compile and save, return file path |

**Available prompts:**

| Prompt | Description |
|--------|-------------|
| `minidoc_guide` | Loads the full DSL reference into the model context |

**Recommended workflow in Claude:**
1. Start with the `minidoc_guide` prompt to load the DSL reference
2. Ask Claude to generate a report
3. Claude calls `render_and_open` — the result opens in your browser instantly

---

## DSL reference

### Document header

```
@doc title="Title" theme=light
```

`theme`: `light` (default) · `dark`

### Text

```
# H1  /  ## H2  /  ### H3
> blockquote
paragraph text with **bold**, *italic*, `code`, [link](url)
[divider]
```

### Metrics

```
[metric label="ARR" value="$4.8M" trend=+18% color=green]
[kpi label="ARR" value="$4.8M" target="$5.0M" trend=+18% color=green]
[progress label="Q3 Goal" value=72 color=green target="$2.2M"]
[badge text="On Track" color=green]
```

### Data

```
[table cols="Name,Stage,Value"
  Acme   | Negotiation | $120k
  Globex | Proposal    | $85k
]

[chart type=bar title="Revenue"
  Jan=40 Feb=55 Mar=72
]
```

### Content blocks

```
[alert type=info text="Message here."]
[callout icon=💡 title="Insight" text="Detail here." color=blue]

[code lang=python title="app.py"
def hello():
    return "world"
]

[diagram
flowchart TD
    A[Client] --> B[API] --> C[(Database)]
]

[image src="https://..." alt="..." caption="Figure 1" width=800]
```

### Layout

```
[columns]
[col][metric label="MRR" value="$700K"][/col]
[col][metric label="NRR" value="118%"][/col]
[/columns]

[section title="Title" style=card]
content here
[/section]

[tabs]
[tab title="Overview"] ... [/tab]
[tab title="Details"]  ... [/tab]
[/tabs]

[accordion title="Show more"] ... [/accordion]
```

### Lists & timelines

```
[list style=check]
- Shipped feature A
- Fixed bug B
[/list]

[timeline color=blue]
- Q1: Launched MVP — 500 users
- Q2: Series A closed — $4M
[/timeline]
```

**Colors:** `green` `red` `blue` `yellow` `purple` `gray`  
**Alert types:** `info` `warning` `error` `success`  
**Chart types:** `bar` `line` `pie` `doughnut`  
**Code languages:** `python` `javascript` `typescript` `sql` `bash` `json` `yaml` `go` `rust`  
**List styles:** `bullet` `numbered` `check`

---

## Example documents

| Example | Markdown | minidoc DSL | Rendered HTML |
|---------|----------|-------------|---------------|
| **URL Shortener — System Design**<br>Architecture · Data model · Scalability · Design decisions | [View .md](benchmark/url_shortener/url_shortener_system_design.md) | [View .minidoc](benchmark/url_shortener/url_shortener_system_design.minidoc) | [Open HTML →](https://shalayiding.github.io/minidoc/url_shortener.html) |

---

## Frontend stack

Compiled HTML files load all dependencies from CDN — no bundler, no build step, no Node.js.

| Layer | Library |
|-------|---------|
| CSS | [Pico CSS v2](https://picocss.com) — classless, CSS-variable theming |
| Charts | [Chart.js](https://chartjs.org) |
| Diagrams | [Mermaid.js v11](https://mermaid.js.org) |
| Syntax highlight | [highlight.js](https://highlightjs.org) — github-dark theme |

---

## License

MIT
