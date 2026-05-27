import importlib
import os
import subprocess
import sys
from pathlib import Path
from fastmcp import FastMCP

mcp = FastMCP("llm2page")

_REPO_ROOT = Path(__file__).parent.parent
_PROMPT_FILE = _REPO_ROOT / "SYSTEM_PROMPT.md"
_RESULT_DIR = _REPO_ROOT / "result"


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


def _write_result(html: str, name: str = "") -> str:
    _RESULT_DIR.mkdir(exist_ok=True)
    stem = name.removesuffix(".minidoc").removesuffix(".html") if name else "output"
    path = _RESULT_DIR / f"{stem}.html"
    path.write_text(html, encoding="utf-8")
    return str(path)


@mcp.prompt()
def minidoc_guide() -> str:
    """MiniDoc DSL reference: syntax, components, and per-role templates.
    Load this prompt at the start of any session where you want to generate reports."""
    return _PROMPT_FILE.read_text(encoding="utf-8")


@mcp.tool()
def render_minidoc(dsl: str, name: str = "") -> str:
    """Compile MiniDoc DSL to an HTML file saved in result/.
    Pass name (e.g. 'netflix_architecture') to set the output filename.
    Returns the absolute path to the rendered file."""
    return _write_result(_compile(dsl), name)


@mcp.tool()
def render_and_open(dsl: str, name: str = "") -> str:
    """Compile MiniDoc DSL to HTML, save in result/, and open in the default browser.
    Pass name (e.g. 'netflix_architecture') to set the output filename.
    Returns the file path."""
    path = render_minidoc(dsl, name)
    if sys.platform == "darwin":
        subprocess.Popen(["open", path])
    elif sys.platform.startswith("linux"):
        subprocess.Popen(["xdg-open", path])
    elif sys.platform == "win32":
        os.startfile(path)
    return path


if __name__ == "__main__":
    mcp.run()
