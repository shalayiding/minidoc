import re
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Node:
    type: str
    attrs: Dict[str, str] = field(default_factory=dict)
    children: List["Node"] = field(default_factory=list)
    content: str = ""
    data_lines: List[str] = field(default_factory=list)


def parse_attrs(s: str) -> Dict[str, str]:
    attrs = {}
    for m in re.finditer(r'(\w+)="([^"]*?)"|(\w+)=([^\s\]]+)', s):
        if m.group(1):
            attrs[m.group(1)] = m.group(2)
        else:
            attrs[m.group(3)] = m.group(4)
    return attrs


BLOCK_TAGS = {"section", "columns", "col", "list"}


def parse(text: str) -> List[Node]:
    lines = text.splitlines()
    nodes: List[Node] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # @doc header
        if stripped.startswith("@doc"):
            nodes.append(Node(type="doc_header", attrs=parse_attrs(stripped[4:])))
            i += 1
            continue

        # Headings
        for level, prefix in ((1, "# "), (2, "## "), (3, "### ")):
            if stripped.startswith(prefix):
                nodes.append(Node(type="heading", attrs={"level": str(level)}, content=stripped[len(prefix):]))
                i += 1
                break
        else:
            # Blockquote
            if stripped.startswith("> "):
                nodes.append(Node(type="quote", content=stripped[2:]))
                i += 1
                continue

            # Block tags with closing counterpart: [section], [columns], [col], [list]
            block_m = re.match(r"^\[(\w+)([^\]]*)\]$", stripped)
            if block_m and block_m.group(1) in BLOCK_TAGS:
                tag = block_m.group(1)
                attrs = parse_attrs(block_m.group(2))
                close = f"[/{tag}]"
                i += 1
                inner, depth = [], 1
                while i < len(lines):
                    l = lines[i].strip()
                    if l == close:
                        depth -= 1
                        if depth == 0:
                            i += 1
                            break
                    elif re.match(rf"^\[{tag}[\s\]]", l):
                        depth += 1
                    inner.append(lines[i])
                    i += 1
                nodes.append(Node(type=tag, attrs=attrs, children=parse("\n".join(inner))))
                continue

            # Inline or multi-line component [tag ...]
            comp_m = re.match(r"^\[(\w+)(.*)", stripped)
            if comp_m:
                tag = comp_m.group(1)
                rest = comp_m.group(2)

                if rest.endswith("]"):
                    nodes.append(Node(type=tag, attrs=parse_attrs(rest[:-1])))
                    i += 1
                    continue

                # Multi-line: collect data lines until bare ]
                data: List[str] = []
                i += 1
                while i < len(lines):
                    l = lines[i].strip()
                    if l == "]":
                        i += 1
                        break
                    data.append(l)
                    i += 1
                nodes.append(Node(type=tag, attrs=parse_attrs(rest), data_lines=data))
                continue

            # Plain paragraph
            nodes.append(Node(type="paragraph", content=stripped))
            i += 1
            continue

        # loop already incremented i for heading match
        continue

    return nodes
