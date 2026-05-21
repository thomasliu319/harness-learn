# AGENTS.md

## 项目概述

AI 知识库助手，自动从 GitHub Trending 和 Hacker News 采集 AI/LLM/Agent 领域的前沿技术动态，经 AI 分析提炼后以结构化 JSON 格式持久化存储，并通过 Telegram、飞书等多个渠道自动分发，帮助团队高效追踪 AI 领域最新进展。

## 技术栈

| 组件 | 选型 |
|------|------|
| 运行时 | Python 3.12 |
| AI 编排 | OpenCode + 国产大模型 |
| 工作流引擎 | LangGraph |
| 多渠道分发 | OpenClaw |

## 编码规范

- **PEP 8**：严格遵循 Python 编码风格指南
- **命名**：变量、函数、方法统一使用 `snake_case`；类名使用 `PascalCase`
- **Docstring**：所有公共函数/类必须使用 [Google 风格 docstring](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)，包含 `Args`、`Returns`、`Raises` 等段落
- **日志**：禁止使用裸 `print()`，统一使用 `logging` 模块，格式为 `logging.getLogger(__name__)`
- **类型注解**：所有公共函数必须包含完整的类型注解
- **行宽**：120 字符上限

## 项目结构

```
ai-knowledge-base-v2/
├── AGENTS.md                  # 本文件
├── .opencode/
│   ├── agents/                # Agent 定义与配置
│   └── skills/                # OpenCode Skill 定义
├── knowledge/
│   ├── raw/                   # 原始采集数据（采集 Agent 产出）
│   └── articles/              # 经分析整理后的结构化 JSON 条目
└── README.md
```

## 知识条目 JSON 格式

每条知识条目按如下 schema 存储，以 `{id}.json` 命名：

```json
{
  "id": "2026-05-21-github-trending-deepseek-r2",
  "title": "DeepSeek-R2 登顶 GitHub Trending",
  "source": "github_trending",
  "source_url": "https://github.com/deepseek-ai/DeepSeek-R2",
  "summary": "DeepSeek 发布第二代推理模型 R2，在 MATH 和 HumanEval 基准上超越 GPT-5，开源权重并支持本地部署。",
  "tags": ["LLM", "reasoning", "open-source", "benchmark"],
  "status": "published",
  "fetched_at": "2026-05-21T10:30:00Z",
  "analyzed_at": "2026-05-21T11:00:00Z",
  "published_at": "2026-05-21T12:00:00Z",
  "distributions": [
    {
      "channel": "telegram",
      "sent_at": "2026-05-21T12:05:00Z",
      "message_id": "12345"
    },
    {
      "channel": "feishu",
      "sent_at": "2026-05-21T12:06:00Z",
      "message_id": "om_abc123"
    }
  ]
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 唯一标识，格式 `{日期}-{来源}-{主题slug}` |
| `title` | string | 是 | 文章标题，≤ 120 字符 |
| `source` | enum | 是 | 来源：`github_trending` / `hacker_news` |
| `source_url` | string | 是 | 原文链接 |
| `summary` | string | 是 | 中文摘要，200-500 字符 |
| `tags` | string[] | 是 | 标签，至少 2 个 |
| `status` | enum | 是 | `draft` → `analyzed` → `published` |
| `fetched_at` | ISO 8601 | 是 | 原始采集时间 |
| `analyzed_at` | ISO 8601 | 否 | AI 分析完成时间 |
| `published_at` | ISO 8601 | 否 | 首次分发时间 |
| `distributions` | object[] | 否 | 各渠道分发记录 |

### 状态流转

```
draft ──(AI 分析完成)──▶ analyzed ──(人工/自动审核)──▶ published
```

## Agent 角色概览

| 角色 | 负责人 | 触发方式 | 职责 |
|------|--------|----------|------|
| **采集 Agent** | `agents/crawler.py` | 定时 / 手动 | 从 GitHub Trending 和 Hacker News 抓取 AI 相关条目，去重后存入 `knowledge/raw/` |
| **分析 Agent** | `agents/analyzer.py` | 采集完成后自动触发 | 读取 `knowledge/raw/` 中的原始数据，调用大模型进行摘要、标签归类、去噪，输出结构化 JSON 至 `knowledge/articles/` |
| **整理 Agent** | `agents/organizer.py` | 分析完成后触发 | 审核待发布条目，通过 OpenClaw 将 `status=published` 的条目分发至 Telegram 和飞书，更新分发记录 |

## 红线（绝对禁止）

1. **禁止输出 API Key / Token**：任何代码、日志、JSON 中不得包含 API Key、Token、Secret 等凭证，统一通过环境变量或 `.env` 注入
2. **禁止裸 print()**：所有输出必须通过 `logging` 模块，级别至少为 `INFO`
3. **禁止跳过状态流转**：条目必须严格按 `draft → analyzed → published` 流转，不得跨状态
4. **禁止重复分发**：已分发的条目（`distributions` 中已有对应渠道记录）不得再次发送
5. **禁止编辑已发布的条目**：`status=published` 的条目及其分发记录视为不可变，如需修正应创建新条目并关联原条目
6. **禁止硬编码配置**：渠道 Webhook、API 端点等配置统一走环境变量，不得硬编码在代码中
