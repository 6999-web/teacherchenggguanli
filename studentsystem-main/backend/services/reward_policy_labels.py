"""Chinese labels for Guangxi Police College 2024 teaching reward policy."""

from typing import Any, Dict, Optional

POLICY_BASIS = "广西警察学院教学工作奖励办法（2024年修订）"

CATEGORY_TEXT = {
    "teaching_achievement": "教学成果类",
    "major_construction": "专业建设类",
    "course_construction": "课程建设类",
    "textbook_construction": "教材建设类",
    "practice_teaching": "实践教学建设类",
    "teaching_competition": "教学竞赛类",
    "teacher_team": "教师队伍建设类",
    "teaching_reform": "教学改革项目奖",
    "teaching_quality": "教学质量奖",
    "lecture_competition": "讲课比赛奖",
    "sanquan_education": "三全育人专项奖",
    "teaching_management": "教学管理奖",
    "ideological_political": "思政类教学工作专项奖",
    "research_achievement": "科研类成果",
}

LEVEL_TEXT = {
    "national": "国家级",
    "provincial": "省（部）级",
    "municipal": "市（厅）级",
    "school": "校级",
}

RANK_TEXT = {
    "grand_prize": "特等奖",
    "first_prize": "一等奖",
    "second_prize": "二等奖",
    "third_prize": "三等奖",
    "key": "重点项目",
    "major": "重大项目",
    "general": "一般项目",
    "A": "A类",
    "B": "B类",
    "vocational_key": "职业教育教学改革研究重点项目",
    "vocational_general": "职业教育教学改革研究一般项目",
}

SUBCATEGORY_TEXT = {
    "group": "团体奖励",
    "individual": "单项奖励",
    "教学成果奖": "教学成果奖",
    "特色专业/一流专业/现代产业学院": "特色专业（一流专业、现代产业学院）",
    "精品/一流/示范课程": "精品（一流、示范等）课程",
    "教材出版20万字以上": "教材出版20万字以上",
    "教材出版20万字以下": "教材出版20万字以下",
    "优秀教材奖": "优秀教材奖",
    "示范性实训基地/校外实践教学基地": "示范性实训基地（校外实践教学基地）",
    "重点实验室": "重点实验室",
    "优秀教学团队": "优秀教学团队",
    "教学名师": "教学名师",
    "教学新秀": "教学新秀",
    "重点/重大项目": "国家级重点（重大）教学改革立项项目",
    "一般项目": "国家级一般教学改革项目",
    "本科教改重点项目": "广西高等教育本科教学改革工程重点项目",
    "本科教改一般A类/职教重点": "广西高等教育本科教学改革工程一般项目A类、广西职业教育教学改革研究重点项目",
    "本科教改一般B类/职教一般": "广西高等教育本科教学改革工程一般项目B类、广西职业教育教学改革研究一般项目",
    "三全育人综合改革示范校": "三全育人综合改革示范校",
    "三全育人综合改革示范院系": "三全育人综合改革示范院系",
    "虚拟教研室/示范中心": "虚拟教研室、示范中心",
    "基层教学组织": "基层教学组织",
    "教学管理工作先进单位": "教学管理工作先进单位",
    "教研室工作先进单位": "教研室工作先进单位",
}


def label(mapping: Dict[str, str], value: Optional[str]) -> str:
    return mapping.get(value or "", value or "")


def reward_subcategory_text(value: Optional[str]) -> str:
    return label(SUBCATEGORY_TEXT, value)


def reward_label_parts(category: str, level: Optional[str], rank: Optional[str], subcategory: Optional[str]) -> Dict[str, str]:
    return {
        "category_text": label(CATEGORY_TEXT, category),
        "subcategory_text": reward_subcategory_text(subcategory),
        "level_text": label(LEVEL_TEXT, level),
        "rank_text": label(RANK_TEXT, rank),
    }


def reward_content_text(
    category: str,
    level: Optional[str] = None,
    rank: Optional[str] = None,
    subcategory: Optional[str] = None,
) -> str:
    parts = reward_label_parts(category, level, rank, subcategory)
    category_text = parts["category_text"]
    subcategory_text = parts["subcategory_text"]
    level_text = parts["level_text"]
    rank_text = parts["rank_text"]

    if category == "teaching_achievement":
        return "".join([level_text, "教学成果", rank_text])
    if category == "teaching_competition":
        return "".join([level_text, "教学竞赛类", subcategory_text, rank_text])
    if category in {"teaching_quality", "lecture_competition"}:
        return "".join([category_text, rank_text])
    if category == "teaching_reform":
        return "".join([level_text, subcategory_text or "教学改革项目", rank_text])
    if category == "textbook_construction" and subcategory_text == "优秀教材奖":
        return "".join([level_text, subcategory_text, rank_text])
    if category == "research_achievement":
        return "科研类成果"
    if subcategory_text:
        return "".join([level_text, subcategory_text, rank_text])
    return "".join([level_text, category_text, rank_text]) or category


def request_subcategory(data: Dict[str, Any], category: str) -> Optional[str]:
    if category == "teaching_competition":
        return data.get("competition_scope") or data.get("subcategory")
    if category == "teaching_reform":
        return data.get("project_type") or data.get("subcategory")
    return data.get("subcategory")
