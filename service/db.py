"""SQLite 连接管理 + schema 加载(单一来源:schema.sql)"""
import sqlite3
import pathlib
from contextlib import contextmanager

# 数据目录 = 项目根 / data
_ROOT = pathlib.Path(__file__).resolve().parent.parent
_DATA_DIR = _ROOT / "data"
_DATA_DIR.mkdir(exist_ok=True)
DB_PATH = _DATA_DIR / "screener.db"
SCHEMA_PATH = _ROOT / "schema.sql"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_conn():
    """with get_conn() as conn: ... 自动关闭,自动 commit(无异常)/rollback(异常)"""
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """启动时执行 schema.sql 全部 CREATE TABLE IF NOT EXISTS"""
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with get_conn() as conn:
        conn.executescript(sql)
