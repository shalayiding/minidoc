<div align="center">

# minidoc

**不要再用 Markdown 写文档了。写一次，呈现得更好。**

一个紧凑的 DSL，编译为精致的独立 HTML——内置图表、流程图、标签页、指标卡和代码高亮。写同样多的内容，得到的远不止于此。

[![PyPI](https://img.shields.io/pypi/v/minidoc-dsl?color=blue)](https://pypi.org/project/minidoc-dsl)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

[English](README.md) · [中文](README_zh.md)

**[→ 在线示例](https://shalayiding.github.io/minidoc/)**

</div>

---

## Markdown 文档的问题

Markdown 无处不在——README、Wiki、设计文档、故障复盘。写起来简单，但大规模阅读时体验很差。一旦文档里塞满了表格、代码块和系统图，它就变成了一堵没人想打开的符号墙。

minidoc 就是为了解决这个问题而生的。写一份紧凑的 DSL（或者让 LLM 来写），得到一份带有真实图表、可交互标签页、Mermaid 流程图和整洁视觉布局的独立 HTML 文件——那种人们真正会去打开的文档。

## 实测对比：URL 短链系统设计文档

我们用同一份系统设计文档分别写了 Markdown 和 minidoc DSL 两个版本，然后对比了结果。

| | Markdown | minidoc DSL |
|---|---|---|
| 写作输入量 | 3,908 tokens | 4,598 tokens（**工作量相当**） |
| 输出结果 | 纯文本 + 表格 | **可交互 HTML，渲染内容达 13,394 tokens** |
| 图表 | ❌ 不支持 | ✅ Chart.js — 柱状图、折线图、饼图 |
| 架构流程图 | ❌ 不支持 | ✅ Mermaid — 流程图、时序图、ER 图 |
| 标签页 / 折叠面板 | ❌ 不支持 | ✅ 内置 |
| KPI / 指标卡 | ❌ 不支持 | ✅ 内置 |
| 代码高亮 | 取决于渲染器 | ✅ highlight.js，github-dark 主题 |
| 可分享性 | 需要 Markdown 渲染器 | ✅ 任意浏览器直接打开，零依赖 |

写的内容差不多，minidoc 编译出的东西是 Markdown 永远做不到的。

> 数据来源：[`benchmark/url_shortener/`](benchmark/url_shortener/) — minidoc DSL vs Markdown，使用 `tiktoken`（cl100k_base）测量。

---

## 快速开始

```bash
pip install minidoc
```

新建 `report.minidoc`：

```
@doc title="Q3 季报" theme=light

# Q3 业务回顾

[columns]
[col][metric label="MRR" value="$48K" trend=+12% color=green][/col]
[col][metric label="流失率" value="2.1%" trend=-0.4% color=blue][/col]
[col][metric label="NPS" value="61" trend=+8 color=purple][/col]
[/columns]

[chart type=bar title="月度营收"
  一月=38 二月=41 三月=44 四月=46 五月=48
]

[table cols="事项,负责人,状态"
  移动端改版 | 设计团队 | ✅ 已完成
  API v2    | 后端团队 | 🔄 进行中
  SOC 2     | 安全团队 | 📋 计划中
]
```

编译：

```bash
minidoc report.minidoc -o report.html
```

用任意浏览器打开 `report.html`，编译后无需联网。

---

## 核心特性

- **极低 token 消耗** — 完整的 DSL 参考手册可以放进一条 system prompt
- **LLM 友好** — 受约束的语法让幻觉和格式错误大幅减少
- **零运行时依赖** — 编译结果完全独立，可作为邮件附件或静态文件直接分发
- **丰富的组件库** — 指标卡、KPI、图表、表格、流程图、代码块、时间线、标签页、折叠面板
- **MCP 服务器** — 与 Claude 及所有支持 MCP 协议的 Agent 原生集成
- **深色模式** — 通过 Pico CSS CSS 变量支持 `theme=dark`
- **Mermaid 图表** — 流程图、时序图、ER 图、甘特图，全部声明式
- **代码高亮** — highlight.js 支持 100+ 语言

---

## 使用方式

### 命令行

```bash
# 编译文件
minidoc report.minidoc -o output.html

# 从 stdin 读取
echo '@doc title="Hello" theme=light
# Hello World' | minidoc -o hello.html
```

### Python API

```python
from minidoc import compile_to_html

dsl = """
@doc title="我的报告" theme=light
# Hello
[metric label="用户数" value="1,240" color=blue]
"""

html = compile_to_html(dsl)
with open("report.html", "w") as f:
    f.write(html)
```

### MCP 服务器（供 Claude 和 LLM Agent 使用）

启动服务器：

```bash
uv run python mcp/server.py
```

在 `.mcp.json` 或 Claude Code 设置中添加：

```json
{
  "mcpServers": {
    "minidoc": {
      "type": "stdio",
      "command": "uvx",
      "args": ["minidoc-mcp"]
    }
  }
}
```

**可用工具：**

| 工具 | 说明 |
|------|------|
| `render_and_open(dsl, name?)` | 编译 DSL，保存到 `result/`，直接打开浏览器 |
| `render_minidoc(dsl, name?)` | 编译并保存，返回文件路径 |

**可用 Prompt：**

| Prompt | 说明 |
|--------|------|
| `minidoc_guide` | 将完整 DSL 参考手册加载到模型上下文 |

**在 Claude 中的推荐工作流：**
1. 调用 `minidoc_guide` prompt，让 Claude 加载 DSL 参考
2. 让 Claude 生成报告
3. Claude 调用 `render_and_open`，结果直接在浏览器中打开

---

## DSL 参考

### 文档头

```
@doc title="标题" theme=light
```

`theme`：`light`（默认）· `dark`

### 文本

```
# 一级标题  /  ## 二级标题  /  ### 三级标题
> 引用块
段落文本，支持 **加粗**、*斜体*、`代码`、[链接](url)
[divider]
```

### 指标组件

```
[metric label="ARR" value="$4.8M" trend=+18% color=green]
[kpi label="ARR" value="$4.8M" target="$5.0M" trend=+18% color=green]
[progress label="Q3 目标" value=72 color=green target="$2.2M"]
[badge text="进展顺利" color=green]
```

### 数据展示

```
[table cols="姓名,阶段,金额"
  Acme   | 谈判中 | $120k
  Globex | 提案中 | $85k
]

[chart type=bar title="营收"
  Jan=40 Feb=55 Mar=72
]
```

### 内容块

```
[alert type=info text="提示信息。"]
[callout icon=💡 title="洞察" text="详细说明。" color=blue]

[code lang=python title="app.py"
def hello():
    return "world"
]

[diagram
flowchart TD
    A[客户端] --> B[API] --> C[(数据库)]
]

[image src="https://..." alt="..." caption="图 1" width=800]
```

### 布局

```
[columns]
[col][metric label="MRR" value="$700K"][/col]
[col][metric label="NRR" value="118%"][/col]
[/columns]

[section title="标题" style=card]
内容
[/section]

[tabs]
[tab title="概览"] ... [/tab]
[tab title="详情"] ... [/tab]
[/tabs]

[accordion title="展开查看"] ... [/accordion]
```

### 列表与时间线

```
[list style=check]
- 完成了功能 A
- 修复了 Bug B
[/list]

[timeline color=blue]
- Q1：发布 MVP — 500 用户
- Q2：完成 A 轮融资 — $400 万
[/timeline]
```

**颜色：** `green` `red` `blue` `yellow` `purple` `gray`  
**提示类型：** `info` `warning` `error` `success`  
**图表类型：** `bar` `line` `pie` `doughnut`  
**代码语言：** `python` `javascript` `typescript` `sql` `bash` `json` `yaml` `go` `rust`  
**列表样式：** `bullet` `numbered` `check`

---

## 示例文档

| 示例 | Markdown 源文件 | minidoc DSL | 渲染 HTML |
|------|----------------|-------------|-----------|
| **URL 短链系统设计**<br>架构图 · 数据模型 · 可扩展性 · 设计决策 | [查看 .md](benchmark/url_shortener/url_shortener_system_design.md) | [查看 .minidoc](benchmark/url_shortener/url_shortener_system_design.minidoc) | [打开 HTML →](https://shalayiding.github.io/minidoc/url_shortener.html) |

---

## 前端技术栈

编译后的 HTML 文件所有依赖均来自 CDN，无需 bundler、构建步骤或 Node.js。

| 层 | 库 |
|----|-----|
| CSS | [Pico CSS v2](https://picocss.com) — 无类名，CSS 变量主题 |
| 图表 | [Chart.js](https://chartjs.org) |
| 流程图 | [Mermaid.js v11](https://mermaid.js.org) |
| 代码高亮 | [highlight.js](https://highlightjs.org) — github-dark 主题 |

---

## License

MIT