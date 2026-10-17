# career connection workbench

> 单兵猎头用的本地 CRM:**数据 + 算法**包。挂载在 task101-portal 9616 的 `/t/hire` 下使用。
>
> 简称 **cc-workbench**(本机目录仍叫 `recruiter-screener`,仓地址 `github.com/notfresh/cc-workbench`)。

**本仓库只提供**:
- `schema.sql` — SQLite 单一来源(jds / candidates / imports)
- `service/db.py` — SQLite 连接管理 + schema 加载
- `service/matching.py` — 字面匹配算法(MVP 阶段 4 实装,接口位已留)
- `service/semantic_search.py` — 语义搜索占位(MVP 阶段 5 启用)
- `AGENTS.md` / `docs/PLAN.md` — 铁律 + 方案文档

**不提供**:Web 入口。所有路由渲染在
[`task101-portal/src/proxied-hire.py`](/root/projects/task101-portal/src/proxied-hire.py) 里——它**独立**的 Flask app,通过 WSGI 挂到 9616。

## 快速访问

浏览器: **http://47.80.28.245:9616/t/hire**

无需单独启动服务——9616 已经在跑(task101-portal),`/t/hire/*` 自动路由到 proxied-hire。

## 拆卸性验证(2026-10-17)

整个目录 + `proxied-hire.py` 复制到任意位置,只改 `_HIRE_ROOT` 一行路径,
就能用 `python3 -c "import proxied_hire"` 跑——零 portal.py 依赖、零 task101-portal 依赖。

## 借鉴自

- `github-issue-service` 的 SQLite 成品 + 增量指针心智
- `task101-portal/portal.py` 的 `issues_browse` 列表/过滤/抽屉模板思路
- **不抄**:爬虫 / 双 repo 目录 / 全量增量 / cron

## 阶段进度

- ✅ 阶段 0 立项 + 阶段 1 脚手架(库能跑能筛)
- ✅ 阶段 2 JD 录入表单 + 候选人录入表单
- ✅ 阶段 3 候选人库 CRUD 完整化
- ✅ 阶段 4 双向匹配 RULES 实装(compute_match_score)
- ⏳ 阶段 5 语义搜索(bge-small-zh + milvus-lite)

详细方案:见 [`docs/PLAN.md`](docs/PLAN.md)。版本:见 git tag `v1.0`。
