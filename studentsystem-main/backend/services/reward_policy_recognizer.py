"""Rule-based recognizer for 2024 teaching reward policy."""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

from services.reward_policy_labels import POLICY_BASIS, reward_content_text
from services.reward_policy_seed import DEFAULT_REWARD_RULES


CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "teaching_achievement": ["教学成果奖", "教学成果"],
    "major_construction": ["特色专业", "一流专业", "现代产业学院", "专业建设"],
    "course_construction": ["精品课程", "一流课程", "示范课程", "课程建设"],
    "textbook_construction": ["教材出版", "优秀教材奖", "优秀教材", "教材奖"],
    "practice_teaching": ["示范性实训基地", "校外实践教学基地", "重点实验室", "实训基地"],
    "teaching_competition": ["教学竞赛", "教学创新竞赛", "青年教师教学竞赛"],
    "teacher_team": ["优秀教学团队", "教学团队", "教学名师", "教学新秀"],
    "teaching_reform": ["教学改革", "教改", "职业教育教学改革", "本科教学改革"],
    "teaching_quality": ["教学质量奖", "教学质量"],
    "lecture_competition": ["讲课比赛奖", "讲课比赛"],
    "sanquan_education": ["三全育人", "综合改革示范校", "综合改革示范院系"],
    "teaching_management": ["虚拟教研室", "示范中心", "基层教学组织", "教学管理工作先进单位", "教研室工作先进单位"],
}

LEVEL_KEYWORDS: Dict[str, List[str]] = {
    "national": ["国家级", "全国", "国家"],
    "provincial": ["省（部）级", "省部级", "省级", "自治区", "区级"],
    "municipal": ["市（厅）级", "市厅级", "市级", "厅级"],
    "school": ["校级", "学校"],
}

RANK_KEYWORDS: Dict[str, List[str]] = {
    "grand_prize": ["特等奖"],
    "first_prize": ["一等奖", "一等"],
    "second_prize": ["二等奖", "二等"],
    "third_prize": ["三等奖", "三等"],
    "key": ["重点项目", "重点"],
    "major": ["重大项目", "重大"],
    "general": ["一般项目", "一般"],
    "A": ["A类", "Ａ类"],
    "B": ["B类", "Ｂ类"],
}

SUBCATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "教学成果奖": ["教学成果奖", "教学成果"],
    "特色专业/一流专业/现代产业学院": ["特色专业", "一流专业", "现代产业学院"],
    "精品/一流/示范课程": ["精品课程", "一流课程", "示范课程"],
    "教材出版20万字以上": ["20万字以上", "二十万字以上"],
    "教材出版20万字以下": ["20万字以下", "二十万字以下"],
    "优秀教材奖": ["优秀教材奖", "优秀教材"],
    "示范性实训基地/校外实践教学基地": ["示范性实训基地", "校外实践教学基地", "实训基地"],
    "重点实验室": ["重点实验室"],
    "group": ["团体奖励", "团体", "团队"],
    "individual": ["单项奖励", "单项", "个人"],
    "优秀教学团队": ["优秀教学团队", "教学团队"],
    "教学名师": ["教学名师"],
    "教学新秀": ["教学新秀"],
    "重点/重大项目": ["重点项目", "重大项目", "重点", "重大"],
    "一般项目": ["一般项目"],
    "本科教改重点项目": ["本科教改重点", "本科教学改革重点"],
    "本科教改一般A类/职教重点": ["A类", "职教重点", "职业教育教学改革研究重点"],
    "本科教改一般B类/职教一般": ["B类", "职教一般", "职业教育教学改革研究一般"],
    "教学质量奖": ["教学质量奖", "教学质量"],
    "讲课比赛奖": ["讲课比赛奖", "讲课比赛"],
    "三全育人综合改革示范校": ["三全育人综合改革示范校", "示范校"],
    "三全育人综合改革示范院系": ["三全育人综合改革示范院系", "示范院系"],
    "虚拟教研室/示范中心": ["虚拟教研室", "示范中心"],
    "基层教学组织": ["基层教学组织"],
    "教学管理工作先进单位": ["教学管理工作先进单位"],
    "教研室工作先进单位": ["教研室工作先进单位"],
}


def recognize_teaching_reward(title: str, attachment_names: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    text = _normalize_text(" ".join([title or "", *(attachment_names or [])]))
    scored = sorted(
        (_score_rule(rule, text) for rule in DEFAULT_REWARD_RULES),
        key=lambda item: (item[0], item[1]),
        reverse=True,
    )
    score, _specificity, best = scored[0]

    if score < 10:
        return {
            "matched": False,
            "category": None,
            "subcategory": None,
            "level": None,
            "rank": None,
            "amount": 0,
            "award_type": "",
            "rule_key": "",
            "confidence": 0,
            "policy_basis": POLICY_BASIS,
            "manual_required": True,
            "manual_reasons": ["未从名称或附件文件名中识别到明确的教学奖励类型"],
        }

    category = best.get("category")
    subcategory = best.get("subcategory")
    level = best.get("level")
    rank = best.get("rank")
    amount = int(best.get("amount") or 0)

    return {
        "matched": True,
        "category": category,
        "subcategory": subcategory,
        "level": level,
        "rank": rank,
        "amount": amount,
        "award_type": reward_content_text(category, level, rank, subcategory),
        "rule_key": _rule_key(best),
        "confidence": min(100, score * 8),
        "policy_basis": POLICY_BASIS,
        "manual_required": False,
        "manual_reasons": [],
    }


def _score_rule(rule: Dict[str, Any], text: str) -> Tuple[int, int, Dict[str, Any]]:
    category = str(rule.get("category") or "")
    subcategory = rule.get("subcategory")
    level = rule.get("level")
    rank = rule.get("rank")
    score = 0

    score += _keyword_score(text, CATEGORY_KEYWORDS.get(category, []), 10)
    score += _keyword_score(text, SUBCATEGORY_KEYWORDS.get(str(subcategory), []), 6)

    if level:
        score += _keyword_score(text, LEVEL_KEYWORDS.get(str(level), []), 5)
    if rank:
        score += _keyword_score(text, RANK_KEYWORDS.get(str(rank), []), 5)

    specificity = int(bool(subcategory)) + int(bool(level)) + int(bool(rank))
    return score, specificity, rule


def _keyword_score(text: str, keywords: Iterable[str], value: int) -> int:
    for keyword in keywords:
        if _normalize_text(keyword) in text:
            return value
    return 0


def _normalize_text(value: str) -> str:
    return re.sub(r"[\s_\-—（）()《》、，,。.;；:：/\\]+", "", value or "").lower()


def _rule_key(rule: Dict[str, Any]) -> str:
    subcategory = rule.get("subcategory")
    if rule.get("category") in {"teaching_achievement", "teaching_quality", "lecture_competition"}:
        subcategory = None
    return "--".join(
        str(part)
        for part in [rule.get("category"), subcategory, rule.get("level"), rule.get("rank")]
        if part
    )
