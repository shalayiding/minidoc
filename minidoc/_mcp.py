import os
import subprocess
import sys
from pathlib import Path
from importlib.resources import files

from fastmcp import FastMCP
from .compiler import compile_to_html

mcp = FastMCP("minidoc")


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
    """Compile MiniDoc DSL to an HTML file.

    output_path examples:
      ""                        → ./result/output.html (current dir)
      "report"                  → ./result/report.html
      "~/docs/report.html"      → absolute path, any directory
      "/tmp/out.html"           → absolute path
    Returns the absolute path to the written file.
    """
    path = _resolve_path(output_path)
    path.write_text(compile_to_html(dsl), encoding="utf-8")
    return str(path)


@mcp.tool()
def render_and_open(dsl: str, output_path: str = "") -> str:
    """Compile MiniDoc DSL to HTML, write to output_path, open in browser."""
    path = render_minidoc(dsl, output_path)
    if sys.platform == "darwin":
        subprocess.Popen(["open", path])
    elif sys.platform.startswith("linux"):
        subprocess.Popen(["xdg-open", path])
    elif sys.platform == "win32":
        os.startfile(path)
    return path


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
