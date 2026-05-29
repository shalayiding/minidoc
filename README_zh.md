<div align="center">

# minidoc

**专为 LLM 设计的紧凑 DSL，生成可读、可分享的 HTML 文档。**

LLM 每天都在生成报告、看板和设计文档——但输出通常是没人想读的 Markdown，或者消耗大量 token 却难以稳定生成的原始 HTML。minidoc 给你的 LLM 提供了第三条路：一个受约束的 DSL，编译成带图表、流程图和交互布局的精致独立 HTML 文件。

[![PyPI](https://img.shields.io/pypi/v/minidoc-dsl?color=blue)](https://pypi.org/project/minidoc-dsl)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

[English](README.md) · [中文](README_zh.md)

| 示例 | 受众 | Markdown | minidoc DSL | 在线 HTML |
|------|------|----------|-------------|-----------|
| URL 短链系统设计 | 工程师 | [.md](benchmark/url_shortener/url_shortener_system_design.md) | [.minidoc](benchmark/url_shortener/url_shortener_system_design.minidoc) | [→ 打开](https://shalayiding.github.io/minidoc/url_shortener.html) |
| Q3 业务季报 | 管理层 | [.md](showcase/q3_business_report.md) | [.minidoc](showcase/q3_business_report.minidoc) | [→ 打开](https://shalayiding.github.io/minidoc/q3_business_report.html) |
| 故障复盘 | DevOps | [.md](showcase/incident_postmortem.md) | [.minidoc](showcase/incident_postmortem.minidoc) | [→ 打开](https://shalayiding.github.io/minidoc/incident_postmortem.html) |
| 销售漏斗看板 | 销售团队 | [.md](showcase/sales_pipeline.md) | [.minidoc](showcase/sales_pipeline.minidoc) | [→ 打开](https://shalayiding.github.io/minidoc/sales_pipeline.html) |
| ML 实验追踪 | 数据科学 | [.md](showcase/ml_experiment.md) | [.minidoc](showcase/ml_experiment.minidoc) | [→ 打开](https://shalayiding.github.io/minidoc/ml_experiment.html) |

</div>

---

## 为什么用 minidoc

让 LLM 生成报告，通常有三种选择：

**选项一 — 生成 Markdown。** LLM 写起来容易，但输出是一堵符号墙。没有图表，没有布局，读者要自己脑补。很难分享给非技术受众。

**选项二 — 生成原始 HTML。** 输出好看，但消耗的 token 是 Markdown 的 3 倍以上，而且 LLM 经常出错——标签未闭合、CSS 单位错误、JavaScript 出 bug。每次生成质量不稳定。

**选项三 — 生成 minidoc DSL。** Token 消耗和 Markdown 相当。编译器负责处理所有 HTML、CSS 和 JS。输出是精致的独立 HTML 文件，读者用任意浏览器打开，或者直接作为邮件附件转发。

## 实测数据：URL 短链系统设计文档

同一份系统设计文档，分别用三种方式生成，对比结果如下：

| | LLM → Markdown | LLM → 原始 HTML | LLM → minidoc DSL |
|---|---|---|---|
| Token 消耗 | 3,908 | ~13,000+ | **4,598** |
| LLM 稳定性 | 高 | 低 — CSS/JS 易出错 | 高 — 语法受约束 |
| 图表 / 流程图 | ❌ | ✅ 不稳定 | ✅ 声明式，一行搞定 |
| 标签页 / 折叠面板 | ❌ | ✅ 不稳定 | ✅ 内置 |
| KPI / 指标卡 | ❌ | ✅ 不稳定 | ✅ 内置 |
| 无工具直接分享 | ❌ 需要渲染器 | ✅ | ✅ |
| 编译输出大小 | 纯文本 | ~13,000 tokens | **13,394 tokens** |

minidoc 的生成成本和 Markdown 相当，但输出的 HTML 文档和原始 HTML 一样丰富——没有 token 浪费，也没有稳定性问题。

> 数据来源：[`benchmark/url_shortener/`](benchmark/url_shortener/) — 使用 `tiktoken`（cl100k_base）测量。

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