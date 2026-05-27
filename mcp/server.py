import os
import tempfile
import subprocess
import sys
from fastmcp import FastMCP
from llm2page import compile_to_html

mcp = FastMCP("llm2page")


@mcp.tool()
def render_minidoc(dsl: str) -> str:
    """Compile MiniDoc DSL to an HTML file. Returns the absolute path to the rendered file.
    Share this path with the user so they can open it in a browser."""
    html = compile_to_html(dsl)
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
