<div align="center">

# minidoc

**A compact DSL for LLMs to generate readable, shareable HTML documents.**

LLMs already generate reports, dashboards, and design docs — but Markdown has limited expressiveness (no charts, no diagrams, no tabs), and raw HTML costs too many tokens to generate reliably. minidoc gives your LLM a better option: a constrained DSL that compiles to polished, self-contained HTML with charts, diagrams, and interactive layout — ready to share with anyone, no tools required.

[![PyPI](https://img.shields.io/pypi/v/minidoc-dsl?color=blue)](https://pypi.org/project/minidoc-dsl)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

[English](README.md) · [中文](README_zh.md)

| Example | Audience | Markdown | minidoc DSL | Live HTML |
|---------|----------|----------|-------------|-----------|
| URL Shortener — System Design | Engineering | [.md](showcase/url_shortener_system_design.md) | [.minidoc](showcase/url_shortener_system_design.minidoc) | [→ Open](https://shalayiding.github.io/minidoc/url_shortener.html) |
| Q3 Business Review | Executive | [.md](showcase/q3_business_report.md) | [.minidoc](showcase/q3_business_report.minidoc) | [→ Open](https://shalayiding.github.io/minidoc/q3_business_report.html) |
| Incident Postmortem | DevOps | [.md](showcase/incident_postmortem.md) | [.minidoc](showcase/incident_postmortem.minidoc) | [→ Open](https://shalayiding.github.io/minidoc/incident_postmortem.html) |
| Sales Pipeline Dashboard | Sales | [.md](showcase/sales_pipeline.md) | [.minidoc](showcase/sales_pipeline.minidoc) | [→ Open](https://shalayiding.github.io/minidoc/sales_pipeline.html) |
| ML Experiment Log | Data Science | [.md](showcase/ml_experiment.md) | [.minidoc](showcase/ml_experiment.minidoc) | [→ Open](https://shalayiding.github.io/minidoc/ml_experiment.html) |

</div>

---

## Why minidoc

When you ask an LLM to produce a report, it has three options:

**Option 1 — Generate Markdown.** Easy for the LLM, but Markdown has limited expressiveness — charts, diagrams, tabs, and metric cards simply can't be represented. Everything degrades to tables and plain text. Hard to share with non-technical stakeholders.

**Option 2 — Generate raw HTML.** The output looks good, but it costs 3× more tokens, and LLMs make frequent mistakes — unclosed tags, broken CSS units, broken JavaScript. Output quality varies every run.

**Option 3 — Generate minidoc DSL.** Same token cost as Markdown. The compiler handles all the HTML, CSS, and JS. Output is a polished, self-contained HTML file the reader can open in any browser — or forward as an email attachment.

## Real numbers: URL shortener system design

We wrote the same system design document in both Markdown and minidoc DSL and measured the difference.

| | LLM → Markdown | LLM → Raw HTML | LLM → minidoc DSL |
|---|---|---|---|
| Token cost | 3,908 | ~13,000+ | **4,598** |
| LLM reliability | High | Low — CSS/JS errors | High — constrained syntax |
| Charts & diagrams | ❌ | ✅ fragile | ✅ declarative |
| Tabs / accordions | ❌ | ✅ fragile | ✅ built-in |
| KPI / metric cards | ❌ | ✅ fragile | ✅ built-in |
| Shareable without tools | ❌ needs renderer | ✅ | ✅ |
| Compiled output | flat text | ~13,000 tokens | **13,394 tokens** |

minidoc costs about the same as Markdown to generate, but produces an HTML document as rich as raw HTML — without the token waste or the reliability problems.

> Benchmark source: [`showcase/`](showcase/) — measured with `tiktoken` (cl100k_base).

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
uvx minidoc-mcp
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
| **URL Shortener — System Design**<br>Architecture · Data model · Scalability · Design decisions | [View .md](showcase/url_shortener_system_design.md) | [View .minidoc](showcase/url_shortener_system_design.minidoc) | [Open HTML →](https://shalayiding.github.io/minidoc/url_shortener.html) |

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
