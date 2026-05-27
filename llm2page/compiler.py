from .parser import parse, Node
from .renderer import render_nodes, PICO_CDN, CHARTJS_CDN
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

    has_chart = any(n.type == "chart" for n in _flatten(nodes))

    body = render_nodes([n for n in nodes if n.type != "doc_header"])

    pico = f'<link rel="stylesheet" href="{PICO_CDN}">'
    chartjs = f'<script src="{CHARTJS_CDN}"></script>' if has_chart else ""

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="{theme}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  {pico}
  {chartjs}
  <style>
    body {{ max-width: 960px; margin: 0 auto; padding: 2rem 1.5rem; }}
  </style>
</head>
<body>
  <main class="container">
    {body}
  </main>
</body>
</html>"""