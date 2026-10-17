-- recruiter-screener · SQLite schema (单一来源,代码读这里建表)
-- 启动时 service/schema.py 会 CREATE TABLE IF NOT EXISTS 执行本文件全部语句

-- ============================================================
-- 1. JD 库
-- ============================================================
CREATE TABLE IF NOT EXISTS jds (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    title             TEXT    NOT NULL,
    company           TEXT,
    salary_min        INTEGER,                   -- k,薪资下限
    salary_max        INTEGER,                   -- k,薪资上限
    location          TEXT,                      -- 工作城市
    experience_years  INTEGER,                   -- 经验要求(年),0 = 不限
    education         TEXT,                      -- 高中/大专/本科/硕士/博士
    tags              TEXT    DEFAULT '[]',      -- JSON 数组,例 ["Python","Django"]
    body              TEXT,                      -- JD 全文描述
    state             TEXT    DEFAULT 'active',  -- active/closed/submitted/rejected
    source            TEXT,                      -- 录入来源:manual/猎聘/朋友推荐
    notes             TEXT,                      -- 猎头备注
    created_at        TEXT    NOT NULL,          -- ISO8601 UTC
    updated_at        TEXT    NOT NULL,
    embedding         BLOB                       -- 预留:语义搜索启用后存 512 维 float32
);

CREATE INDEX IF NOT EXISTS idx_jds_state      ON jds(state);
CREATE INDEX IF NOT EXISTS idx_jds_location   ON jds(location);
CREATE INDEX IF NOT EXISTS idx_jds_education  ON jds(education);
CREATE INDEX IF NOT EXISTS idx_jds_updated    ON jds(updated_at DESC);


-- ============================================================
-- 2. 候选人库
-- ============================================================
CREATE TABLE IF NOT EXISTS candidates (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    name                  TEXT    NOT NULL,
    phone                 TEXT,
    email                 TEXT,
    current_company       TEXT,
    current_title         TEXT,
    experience_years      INTEGER,
    education             TEXT,                  -- 最高学历
    location              TEXT,
    expected_salary_min   INTEGER,               -- k
    expected_salary_max   INTEGER,
    tags                  TEXT    DEFAULT '[]',  -- JSON 数组
    resume                TEXT,                  -- 简历全文
    state                 TEXT    DEFAULT 'contacting',  -- contacting/recommended/hired/paused
    notes                 TEXT,
    created_at            TEXT    NOT NULL,
    updated_at            TEXT    NOT NULL,
    embedding             BLOB                   -- 预留
);

CREATE INDEX IF NOT EXISTS idx_candidates_state     ON candidates(state);
CREATE INDEX IF NOT EXISTS idx_candidates_location  ON candidates(location);
CREATE INDEX IF NOT EXISTS idx_candidates_education ON candidates(education);
CREATE INDEX IF NOT EXISTS idx_candidates_updated   ON candidates(updated_at DESC);


-- ============================================================
-- 3. 录入历史(可选,MVP 阶段先建表,不用)
-- ============================================================
CREATE TABLE IF NOT EXISTS imports (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    kind         TEXT    NOT NULL,    -- 'jd' | 'candidate'
    payload      TEXT    NOT NULL,    -- 原始 JSON
    imported_at  TEXT    NOT NULL,
    source       TEXT                 -- manual / paste / file
);
