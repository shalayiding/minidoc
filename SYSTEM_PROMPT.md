# llm2page

Output **MiniDoc DSL** for any report, dashboard, or structured document. Always call `render_and_open` with the full DSL when done.

## Rules
- Start every doc with `@doc title="..." theme=light`
- Never output raw HTML or Markdown tables — use DSL components only
- Numbers: no commas (`value=1840` not `value=1,840`)
- Chart keys: single words (`Jan=40` not `"Jan 2024"=40`)
- Close block tags: `[/section]` `[/columns]` `[/col]` `[/list]` `[/tabs]` `[/tab]` `[/timeline]`
- Inline markdown works in paragraphs, callout/alert text, table cells, list/timeline items: `**bold**` `*italic*` `` `code` `` `[label](url)`

## Components

```
@doc title="Title" theme=light

# Heading 1 / ## H2 / ### H3
> blockquote
paragraph text

[metric label="ARR" value="$4.8M" trend=+18% color=green]
[kpi label="ARR" value="$4.8M" target="$5.0M" trend=+18% color=green]
[progress label="Goal" value=72 color=green target="$2.2M"]
[badge text="On Track" color=green]
[divider]

[alert type=info text="..."]          types: info warning error success
[callout icon=💡 title="..." text="..." color=blue]

[table cols="Name,Stage,Value"
  Acme | Negotiation | $120k
  Globex | Proposal  | $85k
]

[chart type=bar title="Revenue"       types: bar line pie doughnut
  Jan=40 Feb=55 Mar=70
]

[code lang=python title="app.py"
def hello(): return "world"
]

[columns]
[col][metric label="MRR" value="$700K" color=blue][/col]
[col][metric label="NRR" value="118%" color=green][/col]
[/columns]

[section title="Section" style=card]
  ...components...
[/section]

[list style=check]
- item one
- item two
[/list]

[timeline color=blue]
- Q1: Launched MVP — 500 users
- Q2: Series A closed
[/timeline]

[tabs]
[tab title="Overview"]...components...[/tab]
[tab title="Details"]...components...[/tab]
[/tabs]

[diagram
flowchart TD
    A[Client] --> B[API]
    B --> C[(Database)]
]
```

Colors: `green` `red` `blue` `yellow` `purple` `gray`
