import html as _html
import re
import json
import uuid
from typing import List
from .parser import Node

PICO_CDN = "https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css"
CHARTJS_CDN = "https://cdn.jsdelivr.net/npm/chart.js"
HIGHLIGHTJS_CSS = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css"
HIGHLIGHTJS_JS  = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"

COLOR_MAP = {
    "green":  "#22c55e",
    "red":    "#ef4444",
    "yellow": "#f59e0b",
    "blue":   "#3b82f6",
    "purple": "#8b5cf6",
    "gray":   "#6b7280",
}

CHART_PALETTE = ["#6366f1", "#22c55e", "#f59e0b", "#ef4444", "#3b82f6", "#8b5cf6", "#ec4899"]

ALERT_STYLES = {
    "warning": ("#f59e0b", "#fffbeb", "⚠️"),
    "info":    ("#3b82f6", "#eff6ff", "ℹ️"),
    "error":   ("#ef4444", "#fef2f2", "❌"),
    "success": ("#22c55e", "#f0fdf4", "✅"),
}


def inline_md(text: str) -> str:
    """Inline markdown: `code`, **bold**, *italic*, [link](url)."""
    # code spans first — content inside is treated as literal
    text = re.sub(
        r'`([^`]+)`',
        r'<code style="background:#f3f4f6;padding:0.15em 0.4em;'
        r'border-radius:3px;font-size:0.88em;color:#e83e8c">\1</code>',
        text,
    )
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    return text


def render_nodes(nodes: List[Node]) -> str:
    return "\n".join(render_node(n) for n in nodes)


def render_node(node: Node) -> str:
    fn = _RENDERERS.get(node.type)
    if fn:
        return fn(node)
    return f"<!-- unknown: {node.type} -->"


def _heading(n: Node) -> str:
    lvl = n.attrs.get("level", "2")
    return f"<h{lvl}>{inline_md(n.content)}</h{lvl}>"


def _paragraph(n: Node) -> str:
    return f"<p>{inline_md(n.content)}</p>"


def _quote(n: Node) -> str:
    return f"<blockquote><p>{inline_md(n.content)}</p></blockquote>"


def _metric(n: Node) -> str:
    label = n.attrs.get("label", "")
    value = n.attrs.get("value", "")
    trend = n.attrs.get("trend", "")
    color = COLOR_MAP.get(n.attrs.get("color", "blue"), n.attrs.get("color", "#3b82f6"))

    trend_html = ""
    if trend:
        arrow = "▲" if trend.startswith("+") else "▼"
        tc = "#22c55e" if trend.startswith("+") else "#ef4444"
        trend_html = f'<div style="color:{tc};font-size:0.8em;margin-top:0.2rem">{arrow} {trend}</div>'

    return (
        f'<article style="border-left:4px solid {color};padding:1rem 1.25rem;margin:0.5rem 0;border-radius:6px">'
        f'<div style="font-size:0.8em;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em">{label}</div>'
        f'<div style="font-size:2rem;font-weight:700;color:{color};line-height:1.2">{value}</div>'
        f'{trend_html}'
        f'</article>'
    )


def _table(n: Node) -> str:
    cols = [c.strip() for c in n.attrs.get("cols", "").split(",")]
    header = "".join(f"<th>{c}</th>" for c in cols)
    rows = ""
    for line in n.data_lines:
        line = line.strip()
        if not line:
            continue
        cells = "".join(f"<td>{inline_md(c.strip())}</td>" for c in line.split("|"))
        rows += f"<tr>{cells}</tr>"
    return f"<figure><table><thead><tr>{header}</tr></thead><tbody>{rows}</tbody></table></figure>"


def _chart(n: Node) -> str:
    chart_id = f"chart_{uuid.uuid4().hex[:8]}"
    chart_type = n.attrs.get("type", "bar")
    title = n.attrs.get("title", "")

    data: dict = {}
    # Data from attrs (inline single-line form)
    for k, v in n.attrs.items():
        if k in ("type", "title"):
            continue
        try:
            data[k] = float(v)
        except ValueError:
            pass
    # Data from multi-line form
    for line in n.data_lines:
        for m in re.finditer(r"(\w+)=([0-9.]+)", line):
            data[m.group(1)] = float(m.group(2))

    labels = json.dumps(list(data.keys()))
    values = json.dumps(list(data.values()))
    colors = json.dumps(CHART_PALETTE[: len(data)])

    if chart_type in ("pie", "doughnut"):
        datasets = f'[{{data:{values},backgroundColor:{colors}}}]'
        legend = "true"
    else:
        c = CHART_PALETTE[0]
        datasets = (
            f'[{{label:{json.dumps(title)},data:{values},'
            f'backgroundColor:"{c}",borderColor:"{c}",tension:0.4}}]'
        )
        legend = "false"

    return (
        f'<div style="max-width:600px;margin:1.5rem auto">'
        f'<canvas id="{chart_id}"></canvas>'
        f'<script>new Chart(document.getElementById({json.dumps(chart_id)}),{{'
        f'type:{json.dumps(chart_type)},'
        f'data:{{labels:{labels},datasets:{datasets}}},'
        f'options:{{responsive:true,plugins:{{legend:{{display:{legend}}},'
        f'title:{{display:true,text:{json.dumps(title)}}}}}}}}})'
        f'</script></div>'
    )


def _section(n: Node) -> str:
    title = n.attrs.get("title", "")
    card = n.attrs.get("style", "") == "card"
    shadow = "box-shadow:0 1px 6px rgba(0,0,0,0.08);" if card else ""
    title_html = f"<h3>{title}</h3>" if title else ""
    inner = render_nodes(n.children)
    return (
        f'<section style="background:var(--pico-card-background-color,#fff);'
        f'border-radius:8px;padding:1.5rem;margin:1rem 0;{shadow}">'
        f"{title_html}{inner}</section>"
    )


def _columns(n: Node) -> str:
    inner = render_nodes(n.children)
    return f'<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1rem">{inner}</div>'


def _col(n: Node) -> str:
    return f"<div>{render_nodes(n.children)}</div>"


def _badge(n: Node) -> str:
    text = n.attrs.get("text", "")
    color = COLOR_MAP.get(n.attrs.get("color", "blue"), n.attrs.get("color", "#3b82f6"))
    return (
        f'<span style="background:{color}1a;color:{color};border:1px solid {color}40;'
        f'border-radius:999px;padding:0.2em 0.75em;font-size:0.82em;font-weight:600">{text}</span>'
    )


def _alert(n: Node) -> str:
    color, bg, icon = ALERT_STYLES.get(n.attrs.get("type", "info"), ALERT_STYLES["info"])
    text = inline_md(n.attrs.get("text", ""))
    return (
        f'<div style="background:{bg};border-left:4px solid {color};'
        f'padding:0.75rem 1rem;border-radius:4px;margin:0.75rem 0">{icon} {text}</div>'
    )


def _list(n: Node) -> str:
    style = n.attrs.get("style", "bullet")
    tag = "ol" if style == "numbered" else "ul"
    pl = 'style="padding-left:0"' if style == "check" else ""
    items = []
    for c in n.children:
        if c.type == "paragraph":
            text = re.sub(r"^[-*]\s*", "", c.content)
            prefix = "✅ " if style == "check" else ""
            li_style = 'style="list-style:none;margin:0.3rem 0"' if style == "check" else ""
            items.append(f"<li {li_style}>{prefix}{inline_md(text)}</li>")
    return f"<{tag} {pl}>{''.join(items)}</{tag}>"


def _progress(n: Node) -> str:
    label = n.attrs.get("label", "")
    value = int(float(n.attrs.get("value", "0")))
    target = n.attrs.get("target", "")
    color = COLOR_MAP.get(n.attrs.get("color", "blue"), n.attrs.get("color", "#3b82f6"))
    target_html = f'<span style="font-size:0.8em;color:#6b7280;margin-left:0.5rem">/ {target}</span>' if target else ""
    return (
        f'<div style="margin:0.75rem 0">'
        f'<div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:0.35rem">'
        f'<span style="font-size:0.9em">{label}</span>'
        f'<span style="font-weight:700;color:{color}">{value}%{target_html}</span>'
        f'</div>'
        f'<div style="background:#e5e7eb;border-radius:999px;height:8px;overflow:hidden">'
        f'<div style="width:{min(value,100)}%;background:{color};border-radius:999px;height:8px"></div>'
        f'</div></div>'
    )


def _kpi(n: Node) -> str:
    label = n.attrs.get("label", "")
    value = n.attrs.get("value", "")
    target = n.attrs.get("target", "")
    trend = n.attrs.get("trend", "")
    color = COLOR_MAP.get(n.attrs.get("color", "blue"), n.attrs.get("color", "#3b82f6"))

    trend_html = ""
    if trend:
        arrow = "▲" if trend.startswith("+") else "▼"
        tc = "#22c55e" if trend.startswith("+") else "#ef4444"
        trend_html = f'<span style="color:{tc};font-size:0.85em;margin-left:0.5rem">{arrow} {trend}</span>'

    target_html = (
        f'<div style="font-size:0.8em;color:#6b7280;margin-top:0.25rem">'
        f'Target: <strong>{target}</strong></div>'
    ) if target else ""

    return (
        f'<article style="border-left:4px solid {color};padding:1rem 1.25rem;margin:0.5rem 0;border-radius:6px">'
        f'<div style="font-size:0.8em;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em">{label}</div>'
        f'<div style="font-size:2rem;font-weight:700;color:{color};line-height:1.2">{value}{trend_html}</div>'
        f'{target_html}'
        f'</article>'
    )


def _divider(n: Node) -> str:
    return '<hr style="margin:1.5rem 0;opacity:0.3">'


def _callout(n: Node) -> str:
    icon = n.attrs.get("icon", "💡")
    title = n.attrs.get("title", "")
    text = n.attrs.get("text", "")
    color = COLOR_MAP.get(n.attrs.get("color", "blue"), n.attrs.get("color", "#3b82f6"))
    title_html = f'<div style="font-weight:600;color:{color};margin-bottom:0.2rem">{title}</div>' if title else ""
    return (
        f'<div style="background:{color}0d;border:1px solid {color}30;border-radius:8px;'
        f'padding:1rem 1.25rem;margin:0.75rem 0;display:flex;gap:0.75rem;align-items:flex-start">'
        f'<span style="font-size:1.3rem;line-height:1.4">{icon}</span>'
        f'<div>{title_html}<div style="font-size:0.95em">{inline_md(text)}</div></div>'
        f'</div>'
    )


def _timeline(n: Node) -> str:
    color = COLOR_MAP.get(n.attrs.get("color", "blue"), n.attrs.get("color", "#3b82f6"))
    items = []
    for c in n.children:
        if c.type == "paragraph":
            text = re.sub(r"^[-*]\s*", "", c.content)
            # Split "label: description" if colon present
            if ":" in text:
                label, _, desc = text.partition(":")
                item_html = f'<strong style="color:{color}">{inline_md(label.strip())}</strong> — {inline_md(desc.strip())}'
            else:
                item_html = inline_md(text)
            items.append(
                f'<div style="position:relative;margin-bottom:1.25rem;padding-left:0.25rem">'
                f'<div style="position:absolute;left:-1.4rem;top:0.35rem;width:10px;height:10px;'
                f'background:{color};border-radius:50%;box-shadow:0 0 0 3px {color}30"></div>'
                f'<div style="font-size:0.95em">{item_html}</div>'
                f'</div>'
            )
    return (
        f'<div style="margin:1rem 0;padding-left:1.5rem;'
        f'border-left:2px solid {color}40">{"".join(items)}</div>'
    )


def _tabs(n: Node) -> str:
    group_id = f"tabs_{uuid.uuid4().hex[:8]}"
    buttons, panels = [], []
    tab_nodes = [c for c in n.children if c.type == "tab"]

    for idx, tab in enumerate(tab_nodes):
        title = tab.attrs.get("title", f"Tab {idx+1}")
        active_btn = (
            f'background:var(--pico-primary,#6366f1);color:#fff;'
            f'border-bottom:2px solid var(--pico-primary,#6366f1);'
        ) if idx == 0 else "background:transparent;color:#374151;border-bottom:2px solid transparent;"
        buttons.append(
            f'<button data-group="{group_id}" onclick="minidocTab(\'{group_id}\',{idx})" '
            f'style="border:none;cursor:pointer;padding:0.6rem 1.25rem;font-size:0.9em;'
            f'font-weight:600;border-radius:6px 6px 0 0;{active_btn}">{title}</button>'
        )
        display = "block" if idx == 0 else "none"
        panels.append(
            f'<div id="{group_id}_{idx}" style="display:{display};padding:1rem 0">'
            f'{render_nodes(tab.children)}</div>'
        )

    js = (
        f'<script>'
        f'function minidocTab(g,idx){{'
        f'document.querySelectorAll("[data-group=\'"+g+"\']").forEach(function(b,i){{'
        f'b.style.background=i===idx?"var(--pico-primary,#6366f1)":"transparent";'
        f'b.style.color=i===idx?"#fff":"#374151";'
        f'b.style.borderBottom=i===idx?"2px solid var(--pico-primary,#6366f1)":"2px solid transparent";'
        f'}});'
        f'var p=document.getElementById(g+"_0");'
        f'if(p){{var par=p.parentNode;'
        f'par.querySelectorAll("[id^=\'"+g+"_\']").forEach(function(el,i){{el.style.display=i===idx?"block":"none";}});}}'
        f'}}'
        f'</script>'
    )

    return (
        f'<div style="margin:1rem 0">'
        f'<div style="display:flex;gap:0;border-bottom:2px solid #e5e7eb;margin-bottom:0">{"".join(buttons)}</div>'
        f'{"".join(panels)}'
        f'</div>'
        f'{js}'
    )


def _tab(n: Node) -> str:
    # Rendered by _tabs — standalone tab nodes are no-ops
    return render_nodes(n.children)


def _diagram(n: Node) -> str:
    content = "\n".join(n.data_lines)
    return (
        f'<div class="mermaid" style="margin:1.5rem 0;text-align:center;'
        f'background:var(--pico-card-background-color,#fafafa);'
        f'border-radius:8px;padding:1.5rem;overflow-x:auto">\n{content}\n</div>'
    )


def _code(n: Node) -> str:
    lang = n.attrs.get("lang", "")
    title = n.attrs.get("title", "")
    code = _html.escape("\n".join(n.data_lines))
    lang_class = f'class="language-{lang}"' if lang else ""
    title_html = (
        f'<div style="background:#161b22;border-bottom:1px solid #30363d;'
        f'padding:0.35rem 1rem;font-size:0.8em;color:#8b949e;font-family:monospace">'
        f'{_html.escape(title)}</div>'
    ) if title else ""
    return (
        f'<div style="border:1px solid #30363d;border-radius:8px;overflow:hidden;margin:1rem 0">'
        f'{title_html}'
        f'<pre style="margin:0;padding:0;overflow-x:auto;background:#0d1117">'
        f'<code {lang_class} style="border-radius:0;padding:1rem;display:block;background:#0d1117">{code}</code>'
        f'</pre>'
        f'</div>'
    )


def _image(n: Node) -> str:
    src = n.attrs.get("src", "")
    alt = _html.escape(n.attrs.get("alt", ""))
    caption = n.attrs.get("caption", "")
    width = n.attrs.get("width", "100%")
    align = n.attrs.get("align", "center")
    if width.isdigit():
        width = f"{width}px"
    margin = "margin:0 auto" if align == "center" else f"margin-{'right' if align == 'left' else 'left'}:auto"
    caption_html = (
        f'<figcaption style="text-align:center;font-size:0.85em;color:#6b7280;margin-top:0.4rem">'
        f'{inline_md(caption)}</figcaption>'
    ) if caption else ""
    return (
        f'<figure style="margin:1rem 0;text-align:{align}">'
        f'<img src="{src}" alt="{alt}" style="max-width:{width};height:auto;border-radius:6px;display:block;{margin}">'
        f'{caption_html}'
        f'</figure>'
    )


def _accordion(n: Node) -> str:
    title = n.attrs.get("title", "")
    open_attr = " open" if n.attrs.get("open", "").lower() in ("true", "1", "yes") else ""
    inner = render_nodes(n.children)
    return (
        f'<details{open_attr} style="border:1px solid #e5e7eb;border-radius:8px;'
        f'margin:0.5rem 0;overflow:hidden">'
        f'<summary style="padding:0.85rem 1.25rem;cursor:pointer;font-weight:600;'
        f'background:var(--pico-card-background-color,#fff);user-select:none;'
        f'display:flex;justify-content:space-between;align-items:center;list-style:none">'
        f'{inline_md(title)}'
        f'<span style="font-size:0.75em;color:#6b7280;transition:transform 0.2s">▼</span>'
        f'</summary>'
        f'<div style="padding:1rem 1.25rem;border-top:1px solid #e5e7eb">{inner}</div>'
        f'</details>'
    )


_RENDERERS = {
    "doc_header": lambda n: "",
    "heading":    _heading,
    "paragraph":  _paragraph,
    "quote":      _quote,
    "metric":     _metric,
    "kpi":        _kpi,
    "progress":   _progress,
    "table":      _table,
    "chart":      _chart,
    "section":    _section,
    "columns":    _columns,
    "col":        _col,
    "badge":      _badge,
    "alert":      _alert,
    "list":       _list,
    "divider":    _divider,
    "callout":    _callout,
    "timeline":   _timeline,
    "tabs":       _tabs,
    "tab":        _tab,
    "diagram":    _diagram,
    "code":       _code,
    "image":      _image,
    "accordion":  _accordion,
}