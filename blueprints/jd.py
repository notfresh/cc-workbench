"""JD 库 Blueprint — 阶段 1 起逐步实装"""
from __future__ import annotations
import json
import datetime
from flask import Blueprint, render_template_string, request, abort
from service.db import get_conn

bp = Blueprint("jd", __name__)

# 阶段 1:列表 + 详情。阶段 2 加录入/编辑/删除/字段过滤
LIST_PAGE = """
<h1>📋 JD 库(占位)</h1>
<p>阶段 1 阶段,只有列表 + 详情。阶段 2 加 CRUD + 字段过滤。</p>
<p>共 {{ total }} 条 JD</p>
<table border=1 cellpadding=6>
<tr><th>#</th><th>岗位</th><th>公司</th><th>地点</th><th>学历</th><th>经验</th><th>薪资</th><th>状态</th></tr>
{% for r in rows %}
<tr>
  <td>{{ r.id }}</td>
  <td><a href="/t/jd/{{ r.id }}">{{ r.title }}</a></td>
  <td>{{ r.company or '' }}</td>
  <td>{{ r.location or '' }}</td>
  <td>{{ r.education or '' }}</td>
  <td>{{ r.experience_years or '' }}年</td>
  <td>{{ r.salary_min or '' }}-{{ r.salary_max or '' }}k</td>
  <td>{{ r.state }}</td>
</tr>
{% endfor %}
</table>
<p><a href="/">← 回首页</a></p>
"""


@bp.route("/t/jd")
def jd_list():
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) AS c FROM jds").fetchone()["c"]
        rows = conn.execute(
            "SELECT id, title, company, location, education, experience_years,"
            " salary_min, salary_max, state FROM jds ORDER BY updated_at DESC"
        ).fetchall()
    return render_template_string(LIST_PAGE, total=total, rows=rows)


@bp.route("/t/jd/<int:jid>")
def jd_detail(jid: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM jds WHERE id = ?", (jid,)).fetchone()
    if not row:
        abort(404)
    tags = json.loads(row["tags"] or "[]")
    return render_template_string(
        "<h1>{{ r.title }}</h1>"
        "<p>#{{ r.id }} · {{ r.company or '?' }} · {{ r.location or '?' }}</p>"
        "<p>学历:{{ r.education or '不限' }} · 经验:{{ r.experience_years or '不限' }}年</p>"
        "<p>薪资:{{ r.salary_min or '?' }}-{{ r.salary_max or '?' }}k</p>"
        "<p>状态:{{ r.state }}</p>"
        "<p>标签:{{ tags|join(' / ') }}</p>"
        "<hr><pre>{{ r.body or '(空)' }}</pre>"
        "<p><a href='/t/jd'>← 回列表</a></p>",
        r=row, tags=tags,
    )
