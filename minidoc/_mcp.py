import os
import subprocess
import sys
from pathlib import Path
from importlib.resources import files

from importlib.metadata import version as _pkg_version
from fastmcp import FastMCP
from .compiler import compile_to_html

mcp = FastMCP("minidoc", version=_pkg_version("minidoc-dsl"))

_DSL_REFERENCE = """
═══════════════════════════════════════════
MINIDOC DSL — HOW TO WRITE A .minidoc FILE
═══════════════════════════════════════════

Every .minidoc file must start with:
  @doc title="Your Title" theme=light

──────────────── TEXT ────────────────
  # H1  ## H2  ### H3
  > blockquote
  paragraph text  (**bold** *italic* `code` [link](url))
  [divider]

──────────────── METRICS ────────────────
  [metric label="ARR" value="$4.8M" trend=+18% color=green]
  [kpi label="ARR" value="$4.8M" target="$5.0M" trend=+18% color=green]
  [progress label="Goal" value=72 color=green target="$2.2M"]
  [badge text="On Track" color=green]

──────────────── ALERTS ────────────────
  [alert type=info text="Message."]
  [callout icon=💡 title="Insight" text="Detail." color=blue]
  alert types: info  warning  error  success

──────────────── TABLE ────────────────
  [table cols="Name,Stage,Value"
    Acme   | Negotiation | $120k
    Globex | Proposal    | $85k
  ]

──────────────── CHART ────────────────
  [chart type=bar title="Revenue"
    Jan=40 Feb=55 Mar=72
  ]
  types: bar  line  pie  doughnut

──────────────── CODE ────────────────
  [code lang=python title="app.py"
  def hello(): return "world"
  ]
  langs: python  javascript  typescript  sql  bash  json  yaml  go  rust

──────────────── DIAGRAM (Mermaid) ────────────────
  [diagram
  flowchart TD
      A[Client] --> B[API] --> C[(DB)]
  ]

──────────────── LAYOUT ────────────────
  [columns]
  [col][metric label="MRR" value="$700K" color=blue][/col]
  [col][metric label="NRR" value="118%" color=green][/col]
  [/columns]

  [section title="Title" style=card]
  content here
  [/section]

  [tabs]
  [tab title="Overview"] ... [/tab]
  [tab title="Details"]  ... [/tab]
  [/tabs]

  [accordion title="Show more"] ... [/accordion]

──────────────── LISTS & TIMELINE ────────────────
  [list style=check]
  - Item one
  - Item two
  [/list]
  styles: bullet  numbered  check

  [timeline color=blue]
  - Q1: Launched MVP — 500 users
  - Q2: Series A — $4M
  [/timeline]

──────────────── IMAGE ────────────────
  [image src="https://..." alt="..." caption="Fig 1" width=800 align=center]

──────────────── RULES ────────────────
  Colors:      green  red  blue  yellow  purple  gray
  No commas:   value=1840  (not value=1,840)
  Chart keys:  single words  Jan=40  (not "Jan 2024"=40)
  Close tags:  [/section] [/columns] [/col] [/list] [/tabs] [/tab] [/timeline]
═══════════════════════════════════════════
"""


@mcp.prompt()
def minidoc_guide() -> str:
    """MiniDoc DSL reference — load this at the start of any reporting session."""
    return files("minidoc").joinpath("SYSTEM_PROMPT.md").read_text(encoding="utf-8")


@mcp.tool()
def get_guide() -> str:
    """Return the full MiniDoc DSL reference.

    Call this first to learn how to write .minidoc files before calling compile_file.
    Returns the complete syntax reference including all components, rules, and examples.
    """
    return files("minidoc").joinpath("SYSTEM_PROMPT.md").read_text(encoding="utf-8")


@mcp.tool()
def compile_file(input_path: str, output_path: str = "", open: bool = False) -> str:
    """Compile a .minidoc file to a self-contained HTML file.

    WORKFLOW:
      1. Write the MiniDoc DSL content to a .minidoc file using your file writing tool
      2. Call this tool with the file path to compile it to HTML

    PARAMETERS:
      input_path:  path to the .minidoc file (absolute or relative to cwd)
      output_path: where to write HTML (default: same location as input with .html extension)
      open:        if True, open the compiled HTML in the browser (default: False)

    Returns the absolute path to the compiled HTML file.
""" + _DSL_REFERENCE
    src = Path(input_path).expanduser()
    if not src.is_absolute():
        src = Path.cwd() / src
    if not src.exists():
        raise FileNotFoundError(f"File not found: {src}")

    if output_path:
        out = Path(output_path).expanduser()
        if not out.suffix:
            out = out.with_suffix(".html")
        if not out.is_absolute():
            out = Path.cwd() / out
    else:
        out = src.with_suffix(".html")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(compile_to_html(src.read_text(encoding="utf-8")), encoding="utf-8")

    if open:
        if sys.platform == "darwin":
            subprocess.Popen(["open", str(out)])
        elif sys.platform.startswith("linux"):
            subprocess.Popen(["xdg-open", str(out)])
        elif sys.platform == "win32":
            os.startfile(str(out))

    return str(out)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
