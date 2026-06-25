from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Iterable, List, Optional


LEVEL_ALIASES = {
    "national": "national",
    "国家级": "national",
    "provincial": "provincial",
    "省部级": "provincial",
    "省（部）级": "provincial",
    "municipal": "municipal",
    "市厅级": "municipal",
    "市（厅）级": "municipal",
    "school": "school",
    "校级": "school",
}

RANK_ALIASES = {
    "grand_prize": "grand_prize",
    "特等奖": "grand_prize",
    "first_prize": "first_prize",
    "一等奖": "first_prize",
    "second_prize": "second_prize",
    "二等奖": "second_prize",
    "third_prize": "third_prize",
    "三等奖": "third_prize",
}

TEACHING_ACHIEVEMENT = {
    ("national", "grand_prize"): 120000,
    ("national", "first_prize"): 100000,
    ("national", "second_prize"): 80000,
    ("provincial", "grand_prize"): 60000,
    ("provincial", "first_prize"): 50000,
    ("provincial", "second_prize"): 30000,
    ("municipal", "grand_prize"): 8000,
    ("municipal", "first_prize"): 6000,
    ("municipal", "second_prize"): 4000,
    ("school", "grand_prize"): 3000,
    ("school", "first_prize"): 2000,
    ("school", "second_prize"): 1000,
}

TEACHING_COMPETITION = {
    "group": {
        ("national", "grand_prize"): 30000,
        ("national", "first_prize"): 20000,
        ("national", "second_prize"): 15000,
        ("national", "third_prize"): 10000,
        ("provincial", "grand_prize"): 10000,
        ("provincial", "first_prize"): 8000,
        ("provincial", "second_prize"): 6000,
        ("provincial", "third_prize"): 5000,
        ("municipal", "first_prize"): 5000,
        ("municipal", "second_prize"): 3000,
        ("municipal", "third_prize"): 2000,
    },
    "individual": {
        ("national", "grand_prize"): 20000,
        ("national", "first_prize"): 15000,
        ("national", "second_prize"): 12000,
        ("national", "third_prize"): 8000,
        ("provincial", "grand_prize"): 8000,
        ("provincial", "first_prize"): 6000,
        ("provincial", "second_prize"): 4000,
        ("provincial", "third_prize"): 3000,
        ("municipal", "first_prize"): 3000,
        ("municipal", "second_prize"): 2000,
        ("municipal", "third_prize"): 1000,
    },
}

REFORM_PROJECT = {
    ("national", "major"): 30000,
    ("national", "key"): 30000,
    ("national", "general"): 15000,
    ("provincial", "key"): 10000,
    ("provincial", "A"): 6000,
    ("provincial", "vocational_key"): 6000,
    ("provincial", "B"): 3000,
    ("provincial", "vocational_general"): 3000,
}

SIMPLE_CATEGORY_AMOUNTS = {
    "major_construction": {"national": 60000, "provincial": 40000, "school": 10000},
    "course_construction": {"national": 50000, "provincial": 30000},
    "teaching_quality": {"first_prize": 3000, "second_prize": 2000, "third_prize": 1000},
    "lecture_competition": {"first_prize": 3000, "second_prize": 2000, "third_prize": 1000},
}

PERFORMANCE_GRADE_ORDER = {"不合格": 0, "合格": 1, "良好": 2, "优秀": 3}


def calculate_structured_reward(
    data: Dict[str, Any],
    rules: Optional[Iterable[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    category = str(data.get("category") or "")
    level = _normal_level(data.get("level"))
    rank = _normal_rank(data.get("rank") or data.get("award_rank"))
    adjustments: List[Dict[str, Any]] = []
    manual_reasons: List[str] = []
    base_amount: Optional[int] = None
    final_amount: Optional[int] = None
    policy_basis = "广西警察学院教学工作奖励办法（2024年修订）"

    if str(data.get("first署名单位") or data.get("first_unit") or "").strip() not in {"", "广西警察学院"}:
        manual_reasons.append("成果第一署名单位不是广西警察学院，需要人工复核是否可奖励")

    configured_rule = _match_configured_rule(
        category,
        level,
        rank,
        rules or [],
        subcategory=_rule_subcategory(data),
    )
    if configured_rule:
        base_amount = int(configured_rule.get("amount") or 0)
        final_amount = base_amount
        if configured_rule.get("manual_required"):
            manual_reasons.append("该奖励规则配置为需要人工认定")
        if configured_rule.get("staged") and data.get("project_stage") in {"established", "completed"}:
            final_amount = int(base_amount * 0.5)
            adjustments.append({"type": "stage", "value": 0.5, "reason": "configured staged rule pays 50%"})
        annual_cap = configured_rule.get("annual_cap")
        if annual_cap:
            prior_total = int(data.get("teacher_year_guided_total") or 0)
            remaining = max(0, int(annual_cap) - prior_total)
            if final_amount > remaining:
                final_amount = remaining
                adjustments.append({"type": "cap", "value": int(annual_cap), "reason": "configured annual cap"})
    elif category == "teaching_achievement":
        base_amount = TEACHING_ACHIEVEMENT.get((level, rank))
    elif category == "teaching_competition":
        scope = "group" if data.get("competition_scope") == "group" else "individual"
        base_amount = TEACHING_COMPETITION[scope].get((level, rank))
        final_amount = base_amount
        if data.get("participation_type") == "guided_student" and base_amount is not None:
            final_amount = int(base_amount * 0.5)
            adjustments.append({"type": "ratio", "value": 0.5, "reason": "guided student competition"})
            prior_total = int(data.get("teacher_year_guided_total") or 0)
            remaining = max(0, 20000 - prior_total)
            if final_amount > remaining:
                final_amount = remaining
                adjustments.append({"type": "cap", "value": 20000, "reason": "guided student annual cap"})
    elif category == "teaching_reform":
        project_type = str(data.get("project_type") or "").strip()
        project_type = {"重点": "key", "重大": "major", "一般": "general", "A类": "A", "B类": "B"}.get(project_type, project_type)
        base_amount = REFORM_PROJECT.get((level, project_type))
        final_amount = base_amount
        stage = data.get("project_stage")
        if stage in {"established", "completed"} and base_amount is not None:
            final_amount = int(base_amount * 0.5)
            adjustments.append({"type": "stage", "value": 0.5, "reason": f"{stage} stage pays 50%"})
    elif category == "textbook_construction":
        word_count = int(data.get("word_count") or 0)
        if word_count:
            base_amount = 8000 if word_count >= 200000 else 6000
        elif level and rank:
            textbook_awards = {
                ("national", "first_prize"): 50000,
                ("national", "second_prize"): 30000,
                ("national", "third_prize"): 20000,
                ("provincial", "first_prize"): 15000,
                ("provincial", "second_prize"): 10000,
                ("provincial", "third_prize"): 5000,
            }
            base_amount = textbook_awards.get((level, rank))
    elif category in SIMPLE_CATEGORY_AMOUNTS:
        key = rank if category in {"teaching_quality", "lecture_competition"} else level
        base_amount = SIMPLE_CATEGORY_AMOUNTS[category].get(key)
    elif category in {"ideological_political", "external_competition"}:
        manual_reasons.append("该类别需教务处或专家人工认定奖励标准")

    if final_amount is None:
        final_amount = base_amount

    matched = base_amount is not None
    return {
        "matched": matched,
        "category": category,
        "recognized_level": level,
        "recognized_rank": rank,
        "base_amount": base_amount,
        "final_amount": final_amount if matched else 0,
        "currency": "CNY",
        "policy_basis": policy_basis,
        "adjustments": adjustments,
        "manual_required": bool(manual_reasons) or not matched,
        "manual_reasons": manual_reasons if manual_reasons else ([] if matched else ["未匹配到结构化奖励规则"]),
    }


def summarize_title_gap(
    profile: Dict[str, Any],
    approved_achievements: int,
    performance_records: Iterable[Dict[str, Any]],
    target_rule: Dict[str, Any],
    attachment_types: Iterable[str],
    today: Optional[date] = None,
) -> Dict[str, Any]:
    today = today or date.today()
    missing: List[str] = []
    satisfied: List[str] = []

    required_achievements = int(target_rule.get("min_approved_achievements") or 0)
    if approved_achievements >= required_achievements:
        satisfied.append(f"已认定成果 {approved_achievements} 项")
    else:
        missing.append(f"已认定成果不足，还需 {required_achievements - approved_achievements} 项")

    required_grade = target_rule.get("required_performance_grade")
    if required_grade:
        best_grade = _best_performance_grade(performance_records)
        if PERFORMANCE_GRADE_ORDER.get(best_grade, -1) >= PERFORMANCE_GRADE_ORDER.get(required_grade, 99):
            satisfied.append(f"绩效等级达到 {required_grade}")
        else:
            missing.append(f"缺少 {required_grade} 及以上绩效记录")

    min_years = int(target_rule.get("min_years_in_current_title") or 0)
    title_start = _as_date(profile.get("title_start_date"))
    if min_years and title_start:
        years = (today - title_start).days / 365.25
        if years >= min_years:
            satisfied.append(f"任现职 {years:.1f} 年")
        else:
            missing.append(f"任现职年限不足，还需 {max(0, min_years - years):.1f} 年")
    elif min_years:
        missing.append("缺少当前职称起始时间")

    existing_types = set(attachment_types)
    for attachment_type in target_rule.get("required_attachment_types") or []:
        if attachment_type in existing_types:
            satisfied.append(f"已上传 {attachment_type}")
        else:
            missing.append(f"缺少附件：{attachment_type}")

    return {
        "target_title": target_rule.get("target_title"),
        "eligible": not missing,
        "missing_items": missing,
        "satisfied_items": satisfied,
    }


def _normal_level(value: Any) -> Optional[str]:
    if not value:
        return None
    text = str(value).strip()
    return LEVEL_ALIASES.get(text, text)


def _normal_rank(value: Any) -> Optional[str]:
    if not value:
        return None
    text = str(value).strip()
    return RANK_ALIASES.get(text, text)


def _match_configured_rule(
    category: str,
    level: Optional[str],
    rank: Optional[str],
    rules: Iterable[Dict[str, Any]],
    subcategory: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    for rule in rules:
        if rule.get("category") != category:
            continue
        rule_subcategory = rule.get("subcategory")
        if subcategory and rule_subcategory not in {None, "", subcategory}:
            continue
        if rule.get("level") not in {None, "", level}:
            continue
        if rule.get("rank") not in {None, "", rank}:
            continue
        return rule
    return None


def _rule_subcategory(data: Dict[str, Any]) -> Optional[str]:
    category = str(data.get("category") or "")
    if category == "teaching_competition":
        return "group" if data.get("competition_scope") == "group" else "individual"
    if category == "teaching_reform":
        return str(data.get("project_type") or "").strip() or None
    return str(data.get("subcategory") or "").strip() or None


def _best_performance_grade(records: Iterable[Dict[str, Any]]) -> Optional[str]:
    best = None
    best_score = -1
    for record in records:
        grade = record.get("grade")
        score = PERFORMANCE_GRADE_ORDER.get(str(grade), -1)
        if score > best_score:
            best = grade
            best_score = score
    return best


def _as_date(value: Any) -> Optional[date]:
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str) and value:
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None
    return None
