from .parser import parse, Node
from .renderer import render_nodes, PICO_CDN, CHARTJS_CDN, HIGHLIGHTJS_CSS, HIGHLIGHTJS_JS
from typing import List


def _flatten(nodes: List[Node]):
    for n in nodes:
        yield n
        yield from _flatten(n.children)


def compile_to_html(dsl: str) -> str:
    nodes = parse(dsl)

    doc_attrs = next((n.attrs for n in nodes if n.type == "doc_header"), {})
    title = doc_attrs.get("title", "llm2page")
    theme = doc_attrs.get("theme", "light")

    has_chart   = any(n.type == "chart"   for n in _flatten(nodes))
    has_diagram = any(n.type == "diagram" for n in _flatten(nodes))
    has_code    = any(n.type == "code"    for n in _flatten(nodes))

    body = render_nodes([n for n in nodes if n.type != "doc_header"])

    pico    = f'<link rel="stylesheet" href="{PICO_CDN}">'
    chartjs = f'<script src="{CHARTJS_CDN}"></script>' if has_chart else ""
    hljs    = (
        f'<link rel="stylesheet" href="{HIGHLIGHTJS_CSS}">'
        f'<script src="{HIGHLIGHTJS_JS}"></script>'
        f'<script>document.addEventListener("DOMContentLoaded",()=>hljs.highlightAll())</script>'
    ) if has_code else ""
    mermaid = (
        '<script type="module">'
        'import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";'
        'mermaid.initialize({startOnLoad:true,theme:"default"});'
        '</script>'
    ) if has_diagram else ""

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="{theme}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  {pico}
  {chartjs}
  {hljs}
  {mermaid}
  <style>
    body {{ max-width: 960px; margin: 0 auto; padding: 2rem 1.5rem; }}
    details > summary {{ list-style: none; }}
    details > summary::-webkit-details-marker {{ display: none; }}
    details > summary::after {{ display: none; }}
    details > summary::marker {{ display: none; }}
  </style>
</head>
<body>
  <main class="container">
    {body}
  </main>
</body>
</html>"""