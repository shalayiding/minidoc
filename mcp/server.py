import importlib
import os
import tempfile
import subprocess
import sys
from pathlib import Path
from fastmcp import FastMCP

mcp = FastMCP("llm2page")

_PROMPT_FILE = Path(__file__).parent.parent / "SYSTEM_PROMPT.md"


def _compile(dsl: str) -> str:
    """Always use fresh llm2page code — reload on every call during development."""
    import llm2page.parser
    import llm2page.renderer
    import llm2page.compiler
    import llm2page
    importlib.reload(llm2page.parser)
    importlib.reload(llm2page.renderer)
    importlib.reload(llm2page.compiler)
    importlib.reload(llm2page)
    return llm2page.compile_to_html(dsl)


@mcp.prompt()
def minidoc_guide() -> str:
    """MiniDoc DSL reference: syntax, components, and per-role templates.
    Load this prompt at the start of any session where you want to generate reports."""
    return _PROMPT_FILE.read_text(encoding="utf-8")


@mcp.tool()
def render_minidoc(dsl: str) -> str:
    """Compile MiniDoc DSL to an HTML file. Returns the absolute path to the rendered file.
    Share this path with the user so they can open it in a browser."""
    html = _compile(dsl)
    fd, path = tempfile.mkstemp(suffix=".html", prefix="llm2page_")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(html)
    return path


@mcp.tool()
def render_and_open(dsl: str) -> str:
    """Compile MiniDoc DSL to HTML and open it in the default browser. Returns the file path."""
    path = render_minidoc(dsl)
    if sys.platform == "darwin":
        subprocess.Popen(["open", path])
    elif sys.platform.startswith("linux"):
        subprocess.Popen(["xdg-open", path])
    elif sys.platform == "win32":
        os.startfile(path)
    return path


if __name__ == "__main__":
    mcp.run()
