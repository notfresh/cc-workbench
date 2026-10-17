# AGENTS.md — recruiter-screener 项目铁律

> 单兵猎头用的 JD 库 + 候选人库 + 双向字面匹配工具。MVP 第一期,语义搜索接口预留。

## ⚠️ 已知风险(2026-10-17 立)

| 风险 | 当前状态 | 触发条件 | 缓解 |
|---|---|---|---|
| **删除 = 硬删** | 阶段 2 写 | 用户点"删除 JD/候选人" → `DELETE FROM jds` 不可恢复 | MVP 暂不引入软删;猎头误删可重录。回收站留待阶段 6+ |
| **状态切换走 GET** | 阶段 2 写 | `/t/hire/jd/<id>/state/active` 用 GET 实现,免模板 | 单兵本地,无 CSRF 风险。多用户时**必须改 POST** |
| **表单字段全展开** | 阶段 2 写 | 录入/编辑页一次性展示所有字段(无折叠/JS) | 字段数稳定 ≤ 15,全展开够用 |
| **跨仓 import** | 阶段 1 写 | `proxied-hire.py` `sys.path.insert(0, "/root/projects/recruiter-screener")` 硬编 | 复制走时改这一行即可(已验证拆卸性) |
| **无并发锁** | 整体 | SQLite WAL 模式未启用,多写者并发会锁库 | 单兵单人用,单进程 9616,无并发。语义搜索启用后加 `PRAGMA journal_mode=WAL` |
| **候选人隐私 = 明文** | 整体 | 候选人手机/邮箱/简历全明文存 SQLite,无加密 | 本地库责任在用户;README 提示别放云上。多用户/合规需加密 |
| **大文本无长度校验** | 阶段 2 待补 | JD `body` / 候选人 `resume` 字段无 maxlength,塞 100MB 也能进 | MVP 暂不挡(猎头场景),阶段 3+ 加前端 maxlength + 后端截断 |
| **录入时间用本地时区** | 阶段 1 写 | `datetime.now().isoformat()` 写 created_at/updated_at,无 UTC 标记 | 单机本地用,无歧义。跨时区需 `datetime.now(timezone.utc).isoformat()` |
| **SQL 拼接用 f-string** | 阶段 1 写 | `WHERE title LIKE ?` 走参数化,但 `state='active'` 这种合法值仍用 f-string | 当前只有 4 个固定 state 枚举,值已在 schema 注释中标,**不要加 user-supplied 字符串进 f-string** |
| **同源多任务读写** | 阶段 1 写 | 9616 跑着,用户又开 IDE 直接 sqlite3 改库 → 写锁冲突 | 用户自拍:要么 IDE 只读,要么先关 9616 |

## 项目定位
- **不是** github-issue-service 的 1:1 复制(数据源/增量/向量库都不同)
- **借鉴**:`/root/projects/github-repo-crawler/service/` 的 "SQLite 成品 + 增量指针" 心智、`/root/projects/task101-portal/src/portal.py` 的 web UI 风格
- **不做**:爬虫、多用户、权限、协作、评论(猎头场景不需要)

## 环境约定
- **不独立起服务**——所有路由在 `task101-portal/src/proxied-hire.py` 里,通过 9616 访问
  - 浏览器入口:`http://47.80.28.245:9616/t/hire`
  - 启动 task101-portal:`cd /root/projects/task101-portal && python serve-tasks.py`
- **本项目目录内**用独立 venv:`/root/projects/recruiter-screener/venv/`
  - 跟 `task101-portal` 一样不强行 venv(只用 flask,系统有)——但语义搜索启用时**必须**自己建 venv
  - 启用语义搜索后,cron/CLI 启动走 `source venv/bin/activate && python`(不能裸 python3,踩坑见 github-repo-crawler SKILL.md)
- **数据目录**:`./data/`(git 忽略)
  - `data/screener.db` — SQLite 成品库(JD + candidate + match)
  - `data/imports/` — 手动录入/导入的原始 JSON 快照(留底,跟 issue 服务的 WAL 一样)——MVP 暂不实装
  - `.vector/` — milvus-lite 向量库(语义搜索启用后才创建)

## 编码铁律
- **单一来源**:字段定义在 `schema.sql` 一处,代码读 SQL 建表,不要 Python 端复刻一份
- **行为抽到命名单元**:匹配算法 `compute_match_score(cand, jd) -> (score, reasons)` / 表单 `parse_jd_form()` / 模板 `render_jd_form()` 别写在路由函数里
- **不堆 if-else**:匹配规则用配置驱动(`RULES` 列表),加规则 = 加配置,不动算法;表单字段列表用 dict 驱动,加字段 = 改 schema + 加一项
- **接口预留**:语义搜索函数位 `service/semantic_search.py` 先建空壳 `def search(query, repo=None, top=5): raise NotImplementedError("TODO: 接 bge-small-zh + milvus")` + schema 里预留 `embedding` 字段占位
- **不进数据进 git**:`.gitignore` 已配,任何人 commit data/ 立刻喊停

## 测试约定
- 用户偏好"起 server + 我 curl 测",不装 APK
- 客户端/UI 完成后,**起 9616 服务**给用户手动测,端口/测试命令/数据列表直接列清楚
- 数据库 schema 改动 → 提供 `python migrate.py` 一行迁移脚本(小项目不需要 alembic)

## 不抄的东西
- ❌ 不抄 issue 服务的 cron(无爬虫,数据都是手动)
- ❌ 不抄 issue 服务的 "全量/增量" 抓取(WAL 快照留作"录入底",不当作"抓取成果")
- ❌ 不抄 milvus upsert 的"先删后插"那套复杂逻辑(第一期无向量)
- ❌ 不抄 scrapy / Twisted 那一坨(MVP 根本不需要爬虫)
- ❌ 不抄多 repo 目录(`owner--repo` 双连字符那套是给多仓库用的,这里就一个猎头一份库)

## 借鉴的东西
- ✅ portal.py 风格:`flask` + `render_template_string` + 一页里塞搜索框+表+抽屉
- ✅ SQLite + JSON 快照双留底(SQLite 是成品,JSON 是录入回溯)
- ✅ 字段级过滤(state/type/keyword)→ SQL WHERE 拼装
- ✅ `last_crawl.txt` → 这里改成 `last_import.txt`(记录最后一次手动录入时刻,语义搜索启用后给增量索引用)——MVP 暂不实装
