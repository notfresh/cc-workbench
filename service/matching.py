"""字面匹配算法(阶段 4 实装)

设计原则(SEfirst):
- 单一来源:RULES 列表 = (name, weight, rule_fn) 单一驱动
- 不堆 if-else:compute_match_score 主循环只跑 RULES,加规则 = 加一项 + 加一个规则函数
- 行为抽到命名单元:每个规则独立函数,签名 (candidate: dict, jd: dict) -> (passed: bool, reason: str)
"""
from __future__ import annotations
import json
from typing import Callable, NamedTuple


class RuleResult(NamedTuple):
    name: str
    passed: bool
    reason: str
    weight: int


# 学历等级序(候选 > JD 要求 → 满足)
EDU_ORDER = {"博士": 5, "硕士": 4, "本科": 3, "大专": 2, "高中": 1, "不限": 0}


# ============================================================
# 5 个规则函数
# ============================================================
def _parse_tags(s) -> set[str]:
    """tags 字段是 JSON 数组字符串,容错解析。"""
    if not s:
        return set()
    try:
        return set(json.loads(s))
    except Exception:
        return set()


def _rule_education(c: dict, j: dict) -> tuple[bool, str]:
    c_edu = (c.get("education") or "不限").strip()
    j_edu = (j.get("education") or "不限").strip()
    c_rank = EDU_ORDER.get(c_edu, 0)
    j_rank = EDU_ORDER.get(j_edu, 0)
    if j_rank == 0:  # JD 不限
        return True, f"学历不卡(JD:不限,候选人:{c_edu or '未填'})"
    if c_rank >= j_rank:
        return True, f"学历{c_edu} ≥ JD要求{j_edu}"
    return False, f"学历{c_edu or '未填'} < JD要求{j_edu}"


def _rule_location(c: dict, j: dict) -> tuple[bool, str]:
    c_loc = (c.get("location") or "").strip()
    j_loc = (j.get("location") or "").strip()
    if not j_loc:
        return True, f"地点不卡(JD:不限,候选人:{c_loc or '未填'})"
    if c_loc == j_loc:
        return True, f"地点匹配:{j_loc}"
    return False, f"地点不符(候选人:{c_loc or '未填'} ≠ JD:{j_loc})"


def _rule_experience(c: dict, j: dict) -> tuple[bool, str]:
    c_yrs = c.get("experience_years") or 0
    j_yrs = j.get("experience_years") or 0
    if j_yrs == 0:
        return True, f"经验不卡(JD:不限,候选人:{c_yrs}年)"
    if c_yrs >= j_yrs:
        return True, f"经验{c_yrs}年 ≥ JD要求{j_yrs}年"
    return False, f"经验{c_yrs}年 < JD要求{j_yrs}年"


def _rule_salary(c: dict, j: dict) -> tuple[bool, str]:
    """候选人期望薪资 ⊆ JD 给出区间(候选人 min≥JD min 且 max≤JD max)"""
    c_min = c.get("expected_salary_min") or 0
    c_max = c.get("expected_salary_max") or 0
    j_min = j.get("salary_min") or 0
    j_max = j.get("salary_max") or 0
    if c_min == 0 and c_max == 0:
        return True, "期望薪资未填(无信号)"
    if j_min == 0 and j_max == 0:
        return True, "JD 未填薪资(无对照)"
    c_hi = c_max if c_max > 0 else c_min  # 0 = 未填上限,容错
    if c_min >= j_min and c_hi <= j_max:
        return True, f"薪资区间匹配(候选人{c_min}-{c_hi}k ⊆ JD{j_min}-{j_max}k)"
    return False, f"薪资区间不符(候选人{c_min}-{c_hi}k vs JD{j_min}-{j_max}k)"


def _rule_skill_overlap(c: dict, j: dict) -> tuple[bool, str]:
    c_tags = _parse_tags(c.get("tags"))
    j_tags = _parse_tags(j.get("tags"))
    if not j_tags:
        return True, "JD 无技能标签(无法判定)"
    overlap = c_tags & j_tags
    if overlap:
        shown = ",".join(sorted(overlap)[:5])
        return True, f"技能匹配 {len(overlap)}/{len(j_tags)}:{shown}"
    need = ",".join(sorted(j_tags)[:5])
    return False, f"无技能匹配(JD 要 {need})"


# ============================================================
# 规则集 = (名字, 权重, 计算函数)  ← 加规则在这里加,不动主循环
# 总分 = 100 = 20+15+15+20+30
# ============================================================
RULES: list[tuple[str, int, Callable[[dict, dict], tuple[bool, str]]]] = [
    ("education",      20, _rule_education),
    ("location",       15, _rule_location),
    ("experience",     15, _rule_experience),
    ("salary",         20, _rule_salary),
    ("skill_overlap",  30, _rule_skill_overlap),
]
assert sum(w for _, w, _ in RULES) == 100, f"RULES 权重之和必须 = 100,当前={sum(w for _, w, _ in RULES)}"


def compute_match_score(candidate: dict, jd: dict) -> tuple[int, list[RuleResult]]:
    """返回 (总分, 分项结果)。总分 = sum(weight if passed else 0)。"""
    results: list[RuleResult] = []
    for name, weight, fn in RULES:
        passed, reason = fn(candidate, jd)
        results.append(RuleResult(name, passed, reason, weight))
    return sum(r.weight for r in results if r.passed), results
