# AGENTS.md — recruiter-screener 项目铁律

> 单兵猎头用的 JD 库 + 候选人库 + 双向字面匹配工具。MVP 第一期,语义搜索接口预留。

## 项目定位
- **不是** github-issue-service 的 1:1 复制(数据源/增量/向量库都不同)
- **借鉴**:`/root/projects/github-repo-crawler/service/` 的 "SQLite 成品 + 增量指针" 心智、`/root/projects/task101-portal/src/portal.py` 的 web UI 风格
- **不做**:爬虫、多用户、权限、协作、评论(猎头场景不需要)

## 环境约定
- **本项目目录内**用独立 venv:`/root/projects/recruiter-screener/venv/`
  - 跟 `task101-portal` 一样不强行 venv(只用 flask,系统有)——但语义搜索启用时**必须**自己建 venv
  - 启用语义搜索后,cron/CLI 启动走 `source venv/bin/activate && python`(不能裸 python3,踩坑见 github-repo-crawler SKILL.md)
- **数据目录**:`./data/`(git 忽略)
  - `data/screener.db` — SQLite 成品库(JD + candidate + match)
  - `data/imports/` — 手动录入/导入的原始 JSON 快照(留底,跟 issue 服务的 WAL 一样)
  - `.vector/` — milvus-lite 向量库(语义搜索启用后才创建)
- **端口**:`9617`(避开 9616 task101-portal),启动方式 `python serve.py`

## 编码铁律
- **单一来源**:字段定义在 `schema.sql` 一处,代码读 SQL 建表,不要 Python 端复刻一份
- **行为抽到命名单元**:匹配算法 `compute_match_score(cand, jd) -> (score, reasons)`,别写在路由函数里
- **不堆 if-else**:匹配规则用配置驱动(`rules.json` 或 schema 里的规则表),加规则 = 加配置,不动算法
- **接口预留**:语义搜索函数位 `service/semantic_search.py` 先建空壳 `def search(query, repo=None, top=5): raise NotImplementedError("TODO: 接 bge-small-zh + milvus")` + schema 里预留 `embedding` 字段占位
- **不进数据进 git**:`.gitignore` 已配,任何人 commit data/ 立刻喊停

## 测试约定
- 用户偏好"起 server + 我 curl 测",不装 APK
- 客户端/UI 完成后,**起 9617 服务**给用户手动测,端口/测试命令/数据列表直接列清楚
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
- ✅ `last_crawl.txt` → 这里改成 `last_import.txt`(记录最后一次手动录入时刻,语义搜索启用后给增量索引用)
