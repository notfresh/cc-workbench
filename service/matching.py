"""字面匹配算法(阶段 4 实装)

MVP 阶段留空壳,放规则配置常量和类型签名,避免阶段 1/2/3 还得回来改。
"""
from __future__ import annotations
import json
from typing import Callable, NamedTuple


class RuleResult(NamedTuple):
    name: str
    passed: bool
    reason: str
    weight: int


# 规则集 = (名字, 权重, 计算函数)  ← 加规则在这里加,不动主循环
RULES: list[tuple[str, int, Callable[[dict, dict], tuple[bool, str]]]] = [
    # ("education", 20, _rule_education),
    # ("location", 15, _rule_location),
    # ...
]


def compute_match_score(candidate: dict, jd: dict) -> tuple[int, list[RuleResult]]:
    """MVP 阶段 4 实装。返回 (总分, 分项结果)。总分 = sum(weight if passed else 0)。"""
    if not RULES:
        # MVP 阶段尚未实装,先返 0
        return 0, []
    results: list[RuleResult] = []
    for name, weight, fn in RULES:
        passed, reason = fn(candidate, jd)
        results.append(RuleResult(name, passed, reason, weight))
    return sum(r.weight for r in results if r.passed), results
