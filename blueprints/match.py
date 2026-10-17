"""双向匹配 Blueprint — 阶段 4 实装"""
from flask import Blueprint

bp = Blueprint("match", __name__)


@bp.route("/t/match")
def match_index():
    return "<h1>双向匹配(阶段 4 实装)</h1><p><a href='/'>← 回首页</a></p>"
