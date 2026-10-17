"""schema 加载 — 当前只是 re-export,后续可能加 schema 校验/版本"""
from .db import init_db, get_conn, DB_PATH

__all__ = ["init_db", "get_conn", "DB_PATH"]
