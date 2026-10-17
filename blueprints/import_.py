"""手动录入 Blueprint — 阶段 2 实装"""
from flask import Blueprint

bp = Blueprint("import_", __name__)


@bp.route("/t/import")
def import_index():
    return "<h1>手动录入(阶段 2 实装)</h1><p><a href='/'>← 回首页</a></p>"
