"""候选人库 Blueprint — 阶段 3 实装,阶段 1 先放占位"""
from flask import Blueprint

bp = Blueprint("candidate", __name__)


@bp.route("/t/candidate")
def candidate_list():
    return "<h1>候选人库(阶段 3 实装)</h1><p><a href='/'>← 回首页</a></p>"
