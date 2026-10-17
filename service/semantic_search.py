"""语义搜索 — MVP 阶段 5 启用

抄自 /root/projects/github-repo-crawler/service/ 的 index.py / search.py 心智,
但 MVP 阶段不实装,4 个 TODO 全部 raise NotImplementedError,蓝图侧捕获后给用户
"功能预留中"提示页,而不是 500 报错。
"""
from __future__ import annotations


def embed_text(text: str) -> bytes:
    """文本 → 512 维 float32 向量(blob)"""
    # TODO 阶段 5 启用:
    #   from sentence_transformers import SentenceTransformer
    #   model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
    #   return model.encode(text).tobytes()
    raise NotImplementedError("TODO: 接 bge-small-zh (阶段 5)")


def index_item(item_id: int, item_type: str, text: str) -> None:
    """JD/候选人入库后,触发 embedding + 写入 .vector/embeddings.db (milvus-lite)"""
    # TODO 阶段 5 启用:
    #   vec = embed_text(text)
    #   milvus.upsert(pk=item_id, vector=vec, meta={"type": item_type})
    raise NotImplementedError("TODO: 同步 .vector/embeddings.db (阶段 5)")


def search(query: str, item_type: str = "all", top: int = 5) -> list[dict]:
    """自然语言 → Top N 命中 [{item_id, type, score}]"""
    # TODO 阶段 5 启用:
    #   1. embed_text(query)
    #   2. milvus.search(vector, top_k=top*5, filter=...)
    #   3. 按 number 聚合 + 排序(参考 issue service 的 title 加权模式)
    raise NotImplementedError("TODO: 接 milvus 检索 (阶段 5)")


def rebuild_index() -> int:
    """全量重建 — 遍历 jds + candidates 逐条 index_item()。返回处理条数。"""
    # TODO 阶段 5 启用:
    #   ⚠️ 负载铁律(抄自 issue service):
    #     torch.set_num_threads(2) + ENCODE_BATCH=32 + time.sleep(0.3) + nice -n 10
    raise NotImplementedError("TODO: 全量重建索引 (阶段 5)")
