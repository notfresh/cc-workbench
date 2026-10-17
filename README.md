# recruiter-screener

单兵猎头用的本地 CRM:JD 库 + 候选人库 + 双向字面匹配。语义搜索接口预留。

**MVP 状态**:方案文档定稿中(见 [`docs/PLAN.md`](docs/PLAN.md))。

## 一句话

> 把"猎头手头 Excel 表"升级成"可筛选、可双向匹配、后续可语义搜索"的小工具,本地 SQLite + 一个 Flask web,跑 9617 端口。

## 核心特性

- **JD 库管理** — 录入 / 编辑 / 删除 / 字段过滤(state / 学历 / 地点 / 经验 / 薪资 / 标签)
- **候选人库管理** — 同上,独立表
- **双向字面匹配** — 候选→JD 找匹配岗位,JD→候选 找匹配人选,字段级打分排序
- **语义搜索(预留)** — 接口位已留,MVP 完成后立刻可上(bge-small-zh + milvus-lite)

## 借鉴自

- [`/root/projects/github-repo-crawler/service/`](https://example) — SQLite 成品 + JSON 快照留底 + 增量指针心智
- [`/root/projects/task101-portal/src/portal.py`](https://example) — Flask 单文件 Blueprint 风格
- **不抄**:爬虫 / 多 repo 目录 / 全量增量机制 / 周报

## 快速开始(阶段 1 完成后才有)

```bash
cd /root/projects/recruiter-screener
python serve.py
# 浏览器开 http://localhost:9617
```

## 详细方案

见 [`docs/PLAN.md`](docs/PLAN.md) — 含架构图、字段映射、匹配算法、阶段拆解、借鉴/不借鉴对照表。

## 项目铁律

见 [`AGENTS.md`](AGENTS.md) — 编码约束 / 环境约定 / 测试约定。
