# career connection workbench (cc-workbench) · MVP 方案文档

> 状态:v1.0 已发布(2026-10-17)· 阶段 0-4 完成,阶段 5 语义搜索待启
>
> 本机目录 `recruiter-screener/`,GitHub 仓 `notfresh/cc-workbench`,项目显示名 career connection workbench。

---

## 0. 一句话定位

**单兵猎头用的本地 CRM**:JD 库 + 候选人库 + 双向字面匹配,语义搜索接口预留。

---

## 1. 整体架构(借鉴非复制)

```
┌────────────────────────────────────────────────────────┐
│  浏览器:9617 端口                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  /t/jd       │  │ /t/candidate │  │ /t/match     │ │
│  │  JD 库浏览   │  │ 候选人库浏览 │  │ 双向匹配     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────┐
│  serve.py — 装配各 Blueprint,跑 9617                   │
│  ├── blueprints/jd.py       JD CRUD + 过滤             │
│  ├── blueprints/candidate.py 候选人 CRUD + 过滤       │
│  ├── blueprints/match.py    双向匹配接口              │
│  ├── blueprints/import.py   手动录入(粘贴/上传)       │
│  └── service/                                                │
│      ├── db.py                SQLite 连接池             │
│      ├── schema.py            从 schema.sql 读表结构    │
│      ├── matching.py          字面匹配算法              │
│      └── semantic_search.py  语义搜索(空壳,占位)     │
└────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────┐
│  SQLite(screener.db)                                    │
│  ├── jds           JD 库                                │
│  ├── candidates    候选人库                             │
│  └── matches       匹配结果缓存(可选,先不做持久化)   │
└────────────────────────────────────────────────────────┘
                          ↓
            [语义搜索启用后,接 milvus-lite]
                  .vector/embeddings.db
```

**关键决策**:
- **不抄** github-issue-service 的"分 repo 目录"(`owner--repo/`)——单兵猎头就一份库,简单
- **借鉴** `task101-portal/src/portal.py` 的"一个 Blueprint 一类资源"风格,但不强制塞进同一个文件
- **不抄** sync.py 的"抓取+索引"两阶段——这里的两阶段是"录入+匹配",解耦方式保留

---

## 2. 数据模型(schema)

### 2.1 `jds` 表(JD 库)

| 字段 | 类型 | 说明 | 借鉴 issue 字段 |
|---|---|---|---|
| `id` | INTEGER PK | 自增 | 新增 |
| `title` | TEXT NOT NULL | 岗位名称 | `title` |
| `company` | TEXT | 公司名 | 新增 |
| `salary_min` | INTEGER | 薪资下限(k) | 新增 |
| `salary_max` | INTEGER | 薪资上限(k) | 新增 |
| `location` | TEXT | 工作地点(城市) | 新增 |
| `experience_years` | INTEGER | 经验要求(年) | 新增 |
| `education` | TEXT | 学历要求(高中/大专/本科/硕士/博士) | 新增 |
| `tags` | TEXT(JSON 数组) | 技能标签 ["Python", "Django"] | `labels`(改名为 tags,语义更准) |
| `body` | TEXT | JD 全文描述 | `body` |
| `state` | TEXT | 在招/已下架/已投递 | `state` |
| `source` | TEXT | 录入来源(手动/猎聘/朋友推荐) | 新增 |
| `notes` | TEXT | 猎头自己的备注 | 新增 |
| `created_at` | TEXT | 录入时刻(ISO8601) | `created_at` |
| `updated_at` | TEXT | 最后修改时刻 | `updated_at` |
| `embedding` | BLOB | **预留**——语义搜索启用后存向量 | 新增(占位) |

**状态值**:`active`(在招) / `closed`(已下架) / `submitted`(已投递) / `rejected`(被拒)

### 2.2 `candidates` 表(候选人库)

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | INTEGER PK | 自增 |
| `name` | TEXT NOT NULL | 姓名 |
| `phone` | TEXT | 联系方式 |
| `email` | TEXT | 邮箱 |
| `current_company` | TEXT | 当前公司 |
| `current_title` | TEXT | 当前职位 |
| `experience_years` | INTEGER | 工作年限 |
| `education` | TEXT | 最高学历 |
| `location` | TEXT | 所在城市 |
| `expected_salary_min` | INTEGER | 期望薪资下限 |
| `expected_salary_max` | INTEGER | 期望薪资上限 |
| `tags` | TEXT(JSON 数组) | 技能标签 |
| `resume` | TEXT | 简历全文/履历 |
| `state` | TEXT | 沟通中/已推荐/已入职/暂不考虑 |
| `notes` | TEXT | 猎头备注 |
| `created_at` | TEXT | 录入时刻 |
| `updated_at` | TEXT | 最后修改 |
| `embedding` | BLOB | **预留**——向量 |

**状态值**:`contacting`(沟通中) / `recommended`(已推荐) / `hired`(已入职) / `paused`(暂不考虑)

### 2.3 字段映射(对照 github-issue-service)

| 借鉴 | 改动 | 原因 |
|---|---|---|
| `number` | 改为自增 `id` | 单库不需要 repo 级编号 |
| `is_pr` | 删除 | JD/候选人不混存,各一张表 |
| `labels` | 改名 `tags` | 语义更准,业务叫法 |
| `comments` | 删除 | 猎头不评论 JD |
| `html_url` | 删除 | 没有外部链接 |
| 增量抓取机制 | 改为手动录入,但**保留 JSON 快照习惯** | 录入回溯/审计 |
| `crawl.py` | 改为 `import.py`(手动录入) | 业务无爬虫 |
| `query.py` | 复用思路但简化为"字段过滤 + 全文搜" | 单库不需要交互菜单 |
| `search.py`(语义) | **接口预留** | 立刻会接 |
| `weekly.py` 周报 | **不做** | 猎头不需要周报 |

---

## 3. 匹配算法(字面级别,MVP)

### 3.1 双向匹配语义

**A. 候选→JD**(`POST /t/match/candidate/<id> -> ranked JDs`)
输入:候选人 `cand`,输出:Top N JD 列表(分数降序)
逻辑:对每个 JD,跑 `compute_match_score(cand, jd)`,返回 score+reasons

**B. JD→候选**(`POST /t/match/jd/<id> -> ranked candidates`)
输入:JD `jd`,输出:Top N 候选人
逻辑:对每个候选人,跑 `compute_match_score(cand, jd)`,同上(对称)

**C. 字段级匹配规则**(MVP 第一版,白名单可调)

| 维度 | 规则 | 权重 | 实现 |
|---|---|---|---|
| 学历 | 候选人学历 ≥ JD 要求 | 20 | 学历等级序:博士5/硕士4/本科3/大专2/高中1 |
| 地点 | 候选人期望城市 == JD 城市(或一线城市"灵活") | 15 | 字符串 == 比较 |
| 经验 | 候选人年限 ≥ JD 最低年限 | 15 | 数字比较 |
| 薪资 | 候选人期望 ⊆ JD 区间(候选人 min≥JD min 且 max≤JD max) | 20 | 区间重叠判断 |
| 技能标签 | JD.tags ∩ cand.tags / JD.tags 长度 | 30 | 集合 Jaccard |

总分 100。每条规则返回 `(passed: bool, reason: str, weight: int)`,最终 score = sum(weight if passed else 0)。

**算法配置**:
```python
# service/matching.py
RULES = [
    ("education", 20, _rule_education),
    ("location", 15, _rule_location),
    ("experience", 15, _rule_experience),
    ("salary", 20, _rule_salary),
    ("skill_overlap", 30, _rule_skill_overlap),
]
```
加规则 = 加一项,不动主循环。**SEfirst 铁律:行为抽到命名单元**。

### 3.2 接口设计

```
GET  /t/match                    匹配首页(选方向)
POST /t/match/candidate/<id>    候选→JD(返 top 20 + 详情)
POST /t/match/jd/<id>           JD→候选(返 top 20 + 详情)
GET  /t/match/preview/<cand_id>/<jd_id>  单对匹配详情(给分项 + 原因)
```

**MVP 阶段不做**:
- 匹配结果持久化(每次实时算,MVP 候选/JD 数量不大,SQL JOIN 性能足够)
- 批量匹配(一次多个候选 vs 多个 JD)
- 匹配历史(谁什么时候给谁推荐过)

---

## 4. 语义搜索接口预留(MVP 占位)

### 4.1 文件:`service/semantic_search.py`

```python
def embed_text(text: str) -> bytes:
    """文本 → 512 维向量(blob)"""
    # TODO: 接 bge-small-zh
    # from sentence_transformers import SentenceTransformer
    # model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
    # return model.encode(text).tobytes()
    raise NotImplementedError("TODO: 接 bge-small-zh + milvus-lite")

def index_item(item_id: int, item_type: str, text: str):
    """JD/候选人入库后,触发 embedding + 写入 milvus-lite"""
    # TODO: 接 .vector/embeddings.db (milvus-lite)
    # 1. embed_text(text) → vector
    # 2. milvus.upsert(pk=item_id, vector=vec, meta={"type": item_type})
    raise NotImplementedError("TODO: 同步 .vector/embeddings.db")

def search(query: str, item_type: str = "all", top: int = 5):
    """自然语言 → Top N 命中(item_id + 相似度%)"""
    # TODO:
    # 1. embed_text(query)
    # 2. milvus.search(vector, top_k=top*5, filter=f"type=='{item_type}'")
    # 3. 按 number 聚合 + 排序(参考 issue service 的 title 加权模式)
    raise NotImplementedError("TODO: 接 milvus 检索 + 聚合")

def rebuild_index():
    """全量重建(参考 issue service 的 --full 模式:不 drop,逐条先删后插)"""
    # TODO: 遍历 jds + candidates,逐条 index_item()
    raise NotImplementedError("TODO: 接 bge-small-zh 全量批处理")
```

### 4.2 蓝图:`blueprints/search.py`

```python
@bp.route("/t/search")
def search_page():
    q = request.args.get("q", "").strip()
    if not q:
        return render_search_form()
    try:
        results = semantic_search.search(q, top=10)
    except NotImplementedError:
        return render_search_form(notice="⚠️ 语义搜索尚未启用(预留接口),先用字面搜索 /t/jd?q=...")
    return render_results(results)
```

**未启用时**:用户访问 `/t/search` 看到提示页"功能预留中",不报错。

### 4.3 启用时机(随时可上,文档约定)

启用步骤(走 `service/` 那套踩过的路):
1. `python3 -m venv venv` → `source venv/bin/activate`
2. `pip install -r requirements.txt`
3. 在 `service/semantic_search.py` 里把 4 个 TODO 补完
4. `python rebuild_index.py`(全量跑一次,1k 条级别预计 2-3 分钟)
5. `.vector/embeddings.db` 自动建出,进 `.gitignore`

**负载铁律(抄过来的)**:`torch.set_num_threads(2)` + `ENCODE_BATCH=32` + `time.sleep(0.3)` + `nice -n 10 python`。详见 `github-repo-crawler/service/SKILL.md` "⚠️ 负载控制是铁律"。

---

## 5. 文件骨架

```
recruiter-screener/
├── AGENTS.md              # 项目铁律(已写)
├── README.md              # 入门
├── docs/
│   └── PLAN.md            # 本文档
├── schema.sql             # SQLite 表结构(单一来源)
├── serve.py               # 入口:装配 Blueprint,跑 9617
├── requirements.txt       # flask + 语义搜索预留
├── .gitignore
├── blueprints/
│   ├── __init__.py
│   ├── jd.py              # /t/jd/*  JD 库
│   ├── candidate.py       # /t/candidate/* 候选人库
│   ├── match.py           # /t/match/* 双向匹配
│   ├── import_.py         # /t/import/* 手动录入
│   └── search.py          # /t/search/* 语义搜索(占位)
├── service/
│   ├── __init__.py
│   ├── db.py              # SQLite 连接管理
│   ├── schema.py          # 从 schema.sql 读建表语句
│   ├── matching.py        # 字面匹配算法 + RULES 配置
│   └── semantic_search.py # 占位,4 个 NotImplementedError
├── data/                  # git 忽略
│   ├── screener.db
│   └── imports/
├── .vector/               # git 忽略,语义搜索启用后才有
│   └── embeddings.db
├── venv/                  # git 忽略
└── tests/                 # 手动 curl 测,不进 git
    └── curl_examples.md
```

---

## 6. MVP 阶段拆解

### 阶段 0(已完成)✅
- 仓库建好
- AGENTS.md / README / PLAN / requirements / .gitignore
- 方案文档

### 阶段 1:脚手架 + 单表能跑(1 个 JD 库)
- `schema.sql` + `service/db.py` + `serve.py` 最小 Flask
- `blueprints/jd.py` 只做:列表 + 详情
- 不接候选人库、不接匹配
- 验收:9617 能开,看到空库 + 能手动插一条 JD(curl 或表单)

### 阶段 2:JD 库完整 CRUD + 字段过滤
- 录入表单(粘贴 JSON / 填字段)
- 编辑 / 删除 / 状态切换
- 过滤:state/学历/地点/经验/标签
- 验收:猎头能完整管理 JD 库

### 阶段 3:候选人库(镜像阶段 2)
- 同 JD 库结构,字段不同
- 验收:候选人库能用

### 阶段 4:双向匹配
- `service/matching.py` + RULES 配置
- `/t/match/candidate/<id>` + `/t/match/jd/<id>`
- 单对详情页(分项得分 + 原因)
- 验收:跑 5 条 JD × 5 个候选,匹配结果合理

### 阶段 5:语义搜索(可选,MVP 完成后立刻上)
- 补 4 个 TODO
- 全量重建索引
- 验收:`/t/search "3年 Python 经验 北京"` 返回相关条目

---

## 7. 借鉴 vs 不借鉴(速查表)

| github-issue-service | recruiter-screener | 处理 |
|---|---|---|
| Scrapy 爬虫 | **不要** | 手动录入 |
| `crawl.py` 增量 | 改为 `import.py` 手动 | 业务不同 |
| `query.py` 交互菜单 | 简化为字段过滤 | 单库不需要 |
| `search.py` 语义 | **接口预留** | 立刻会接 |
| `weekly.py` 周报 | **不要** | 猎头不需要 |
| 双连字符 `owner--repo/` 目录 | **不要** | 单库一份 |
| `last_crawl.txt` | `last_import.txt` | 录入指针 |
| `data/crawls/*.json` WAL | `data/imports/*.json` WAL | 录入回溯 |
| `data/issues.db` | `data/screener.db` | SQLite 成品 |
| `.vector/issues_vectors.db` | `.vector/embeddings.db` | milvus-lite 同样 |
| `task101-portal` 9616 挂载 | 自己 9617 起服务 | 端口错开 |
| `portal.py` 页面风格 | **借鉴** | UI 风格统一 |
| 学历/经验/薪资多字段过滤 | **借鉴** | 同样是字段过滤 |

---

## 8. 待确认(开工前)

- [ ] **端口 9617** 行不行?(避开 9616 task101-portal)
- [ ] **学历等级序** 默认 博士5/硕士4/本科3/大专2/高中1,要不要细分(海外学历/专升本)?
- [ ] **匹配规则权重** 5 项加起来 100,合不合理?(用户拍)
- [ ] **JSON 快照习惯** 要不要保留?猎头场景下录入回溯意义多大?
- [ ] **候选人隐私** ——本地库,数据安全责任在用户,我们不做加密(只 README 提示)
- [ ] **导入历史** ——要不要支持"猎聘导出 JSON 一键导入"?MVP 不做,只手动填
