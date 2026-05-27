# llm2page

Output **MiniDoc DSL** for any report, dashboard, or structured document. Always call `render_and_open` with the full DSL when done.

## Rules
- Start every doc with `@doc title="..." theme=light`
- Never output raw HTML or Markdown tables — use DSL components only
- Numbers: no commas (`value=1840` not `value=1,840`)
- Chart/diagram keys: single words (`Jan=40` not `"Jan 2024"=40`)
- Close block tags: `[/section]` `[/columns]` `[/col]` `[/list]` `[/tabs]` `[/tab]` `[/timeline]`
- Inline markdown in paragraphs, callout/alert text, table cells, list and timeline items: `**bold**` `*italic*` `` `code` `` `[label](url)`

## Components

```
@doc title="Title" theme=light

# H1  /  ## H2  /  ### H3
> blockquote
paragraph text here

[metric label="ARR" value="$4.8M" trend=+18% color=green]
[kpi label="ARR" value="$4.8M" target="$5.0M" trend=+18% color=green]
[progress label="Q3 Goal" value=72 color=green target="$2.2M"]
[badge text="On Track" color=green]
[divider]

[alert type=info text="Message here."]
[callout icon=💡 title="Insight" text="Detail here." color=blue]

[table cols="Name,Stage,Value"
  Acme   | Negotiation | $120k
  Globex | Proposal    | $85k
]

[chart type=bar title="Revenue"
  Jan=40 Feb=55 Mar=70
]

[code lang=python title="app.py"
def hello():
    return "world"
]

[columns]
[col][metric label="MRR" value="$700K" color=blue][/col]
[col][metric label="NRR" value="118%" color=green][/col]
[/columns]

[section title="Title" style=card]
[alert type=warning text="Watch this."]
[/section]

[list style=check]
- First item
- Second item
[/list]

[timeline color=blue]
- Q1: Launched MVP — 500 users
- Q2: Series A closed
[/timeline]

[tabs]
[tab title="Overview"]
[metric label="MAU" value="18400" color=blue]
[/tab]
[tab title="Details"]
[table cols="Metric,Value"
  Uptime | 99.99%
]
[/tab]
[/tabs]

[image src="https://example.com/photo.png" alt="Description" caption="Figure 1" width=800 align=center]

[accordion title="Why this approach?"]
Explanation here — any components work inside.
[/accordion]

[accordion title="Show details" open=true]
[table cols="Key,Value"
  Uptime | 99.99%
]
[/accordion]

[diagram
flowchart TD
    A[Client] --> B[API]
    B --> C[(Database)]
]
```

**Colors:** `green` `red` `blue` `yellow` `purple` `gray`

**Alert types:** `info` `warning` `error` `success`

**Chart types:** `bar` `line` `pie` `doughnut`

**Code lang:** `python` `javascript` `typescript` `sql` `bash` `json` `yaml` `go` `rust`

**List styles:** `bullet` `numbered` `check`
