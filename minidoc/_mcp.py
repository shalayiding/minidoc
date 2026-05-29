import os
import subprocess
import sys
from pathlib import Path
from importlib.resources import files

from fastmcp import FastMCP
from .compiler import compile_to_html

mcp = FastMCP("minidoc")

_DSL_REFERENCE = """
MiniDoc DSL — quick reference
==============================
Every document starts with: @doc title="Your Title" theme=light

HEADINGS & TEXT
  # H1  ## H2  ### H3
  > blockquote
  paragraph (supports **bold** *italic* `code` [link](url))
  [divider]

METRICS
  [metric label="ARR" value="$4.8M" trend=+18% color=green]
  [kpi label="ARR" value="$4.8M" target="$5.0M" trend=+18% color=green]
  [progress label="Goal" value=72 color=green target="$2.2M"]
  [badge text="On Track" color=green]

ALERTS
  [alert type=info text="Message."]          types: info warning error success
  [callout icon=💡 title="Title" text="Detail." color=blue]

TABLE
  [table cols="Name,Stage,Value"
    Acme   | Negotiation | $120k
    Globex | Proposal    | $85k
  ]

CHART
  [chart type=bar title="Revenue"
    Jan=40 Feb=55 Mar=72
  ]
  types: bar line pie doughnut

CODE
  [code lang=python title="app.py"
  def hello(): return "world"
  ]
  langs: python javascript typescript sql bash json yaml go rust

DIAGRAM (Mermaid)
  [diagram
  flowchart TD
      A[Client] --> B[API] --> C[(DB)]
  ]

LAYOUT
  [columns][col] ... [/col][col] ... [/col][/columns]
  [section title="Title" style=card] ... [/section]
  [tabs][tab title="A"] ... [/tab][tab title="B"] ... [/tab][/tabs]
  [accordion title="Show more"] ... [/accordion]

LISTS & TIMELINE
  [list style=check]
  - Item one
  - Item two
  [/list]                               styles: bullet numbered check

  [timeline color=blue]
  - Q1: Launched MVP — 500 users
  - Q2: Series A — $4M
  [/timeline]

IMAGE
  [image src="https://..." alt="..." caption="Fig 1" width=800 align=center]

COLORS: green red blue yellow purple gray
RULES: no commas in numbers (value=1840 not 1,840) · always close block tags
"""


def _resolve_path(output_path: str) -> Path:
    if not output_path:
        p = Path.cwd() / "result" / "output.html"
    else:
        p = Path(output_path).expanduser()
        if not p.suffix:
            p = p.with_suffix(".html")
        if not p.is_absolute():
            p = Path.cwd() / p
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


@mcp.prompt()
def minidoc_guide() -> str:
    """MiniDoc DSL reference — load this at the start of any reporting session."""
    return files("minidoc").joinpath("SYSTEM_PROMPT.md").read_text(encoding="utf-8")


@mcp.tool()
def render_minidoc(dsl: str, output_path: str = "") -> str:
    """Compile MiniDoc DSL string to a self-contained HTML file.

    Use this tool to render a report, dashboard, or document from MiniDoc DSL.
    The output is a polished HTML file with charts, diagrams, and layout — open
    in any browser or forward as an attachment.

    output_path examples:
      ""                     → ./result/output.html
      "report"               → ./result/report.html
      "~/docs/report.html"   → absolute path
    Returns the absolute path to the written file.
""" + _DSL_REFERENCE
    path = _resolve_path(output_path)
    path.write_text(compile_to_html(dsl), encoding="utf-8")
    return str(path)


@mcp.tool()
def render_and_open(dsl: str, output_path: str = "") -> str:
    """Compile MiniDoc DSL to HTML, save to output_path, and open in the browser.

    Use this when you want to immediately preview the rendered result.
    output_path works the same as render_minidoc.
    Returns the absolute path to the written file.
""" + _DSL_REFERENCE
    path = render_minidoc(dsl, output_path)
    if sys.platform == "darwin":
        subprocess.Popen(["open", path])
    elif sys.platform.startswith("linux"):
        subprocess.Popen(["xdg-open", path])
    elif sys.platform == "win32":
        os.startfile(path)
    return path


@mcp.tool()
def compile_file(input_path: str, output_path: str = "") -> str:
    """Convert a .minidoc source file to HTML.

    Reads the DSL from input_path and writes the compiled HTML to output_path.
    If output_path is omitted, writes next to the source file with a .html extension.

    input_path:  path to the .minidoc file (absolute or relative to cwd)
    output_path: where to write HTML; defaults to same dir/name as input
    Returns the absolute path to the written HTML file.
    """
    src = Path(input_path).expanduser()
    if not src.is_absolute():
        src = Path.cwd() / src
    if not src.exists():
        raise FileNotFoundError(f"File not found: {src}")
    dsl = src.read_text(encoding="utf-8")
    out = _resolve_path(output_path) if output_path else src.with_suffix(".html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(compile_to_html(dsl), encoding="utf-8")
    return str(out)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
