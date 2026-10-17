#!/usr/bin/env python3
"""serve.py — recruiter-screener 入口,9617 端口,装配各 Blueprint

启动:cd /root/projects/recruiter-screener && python serve.py
浏览器:http://localhost:9617
"""
import sys
import pathlib

# 让 service/ blueprints/ 能用包导入
_ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_ROOT))

from flask import Flask
from service.db import init_db
from blueprints.jd import bp as jd_bp
from blueprints.candidate import bp as candidate_bp
from blueprints.match import bp as match_bp
from blueprints.search import bp as search_bp
from blueprints.import_ import bp as import_bp

app = Flask("recruiter_screener")
app.register_blueprint(jd_bp)
app.register_blueprint(candidate_bp)
app.register_blueprint(match_bp)
app.register_blueprint(search_bp)
app.register_blueprint(import_bp)


@app.route("/")
def index():
    links = [
        ("📋 JD 库",          "/t/jd"),
        ("👤 候选人库",       "/t/candidate"),
        ("🎯 双向匹配",       "/t/match"),
        ("📥 手动录入",       "/t/import"),
        ("🔍 语义搜索(预留)", "/t/search"),
    ]
    items = "".join(f'<li><a href="{h}">{t}</a></li>' for t, h in links)
    return f"""
<h1>recruiter-screener</h1>
<p>单兵猎头 CRM · MVP 阶段 1 脚手架</p>
<ul>{items}</ul>
<p>服务端口:9617 · 数据:<code>./data/screener.db</code></p>
"""


if __name__ == "__main__":
    init_db()  # 启动时建表
    from werkzeug.serving import run_simple
    run_simple("0.0.0.0", 9617, app, use_reloader=False, use_debugger=False, threaded=True)
