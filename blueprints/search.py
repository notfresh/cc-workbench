"""语义搜索 Blueprint — MVP 阶段 5 启用,阶段 1 放占位提示页"""
from flask import Blueprint, render_template_string, request

bp = Blueprint("search", __name__)

NOTICE_PAGE = """
<h1>🔍 语义搜索</h1>
<form method=get>
  <input name=q value="{{ q }}" placeholder="试试:3年 Python 经验 北京" style="width:400px;padding:6px">
  <button type=submit>搜索</button>
</form>
{% if notice %}
  <p style="color:#d97706">⚠️ {{ notice }}</p>
{% endif %}
<p><a href='/'>← 回首页</a></p>
"""


@bp.route("/t/search")
def search_page():
    q = request.args.get("q", "").strip()
    notice = None
    if q:
        # 阶段 5 之前,统一提示"功能预留"
        notice = ("语义搜索功能尚未启用(MVP 阶段 5 计划)。"
                  "现阶段请用字段过滤: <a href='/t/jd'>/t/jd</a> 或 <a href='/t/candidate'>/t/candidate</a>。")
    return render_template_string(NOTICE_PAGE, q=q, notice=notice)
