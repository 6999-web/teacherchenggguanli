"""Reward rules for Guangxi Police College teaching work awards (2024 revision)."""

from __future__ import annotations

import re
from typing import Any, Dict, Optional


Rank = Optional[str]


TEACHING_ACHIEVEMENT_AMOUNTS = {
    ("国家级", "特等奖"): 120000,
    ("国家级", "一等奖"): 100000,
    ("国家级", "二等奖"): 80000,
    ("省部级", "特等奖"): 60000,
    ("省部级", "一等奖"): 50000,
    ("省部级", "二等奖"): 30000,
    ("市厅级", "特等奖"): 8000,
    ("市厅级", "一等奖"): 6000,
    ("市厅级", "二等奖"): 4000,
    ("校级", "特等奖"): 3000,
    ("校级", "一等奖"): 2000,
    ("校级", "二等奖"): 1000,
}

MAJOR_CONSTRUCTION_AMOUNTS = {
    "国家级": 60000,
    "省部级": 40000,
    "校级": 10000,
}

COURSE_CONSTRUCTION_AMOUNTS = {
    "国家级": 50000,
    "省部级": 30000,
}

TEXTBOOK_AWARD_AMOUNTS = {
    ("国家级", "一等奖"): 50000,
    ("国家级", "二等奖"): 30000,
    ("国家级", "三等奖"): 20000,
    ("省部级", "一等奖"): 15000,
    ("省部级", "二等奖"): 10000,
    ("省部级", "三等奖"): 5000,
}

PRACTICE_CONSTRUCTION_AMOUNTS = {
    ("国家级", "示范性实训基地"): 80000,
    ("国家级", "校外实践教学基地"): 80000,
    ("国家级", "重点实验室"): 80000,
    ("省部级", "重点实验室"): 30000,
    ("省部级", "示范性实训基地"): 20000,
    ("省部级", "校外实践教学基地"): 20000,
}

TEACHING_COMPETITION_AMOUNTS = {
    "group": {
        ("国家级", "特等奖"): 30000,
        ("国家级", "一等奖"): 20000,
        ("国家级", "二等奖"): 15000,
        ("国家级", "三等奖"): 10000,
        ("省部级", "特等奖"): 10000,
        ("省部级", "一等奖"): 8000,
        ("省部级", "二等奖"): 6000,
        ("省部级", "三等奖"): 5000,
        ("市厅级", "一等奖"): 5000,
        ("市厅级", "二等奖"): 3000,
        ("市厅级", "三等奖"): 2000,
    },
    "individual": {
        ("国家级", "特等奖"): 20000,
        ("国家级", "一等奖"): 15000,
        ("国家级", "二等奖"): 12000,
        ("国家级", "三等奖"): 8000,
        ("省部级", "特等奖"): 8000,
        ("省部级", "一等奖"): 6000,
        ("省部级", "二等奖"): 4000,
        ("省部级", "三等奖"): 3000,
        ("市厅级", "一等奖"): 3000,
        ("市厅级", "二等奖"): 2000,
        ("市厅级", "三等奖"): 1000,
    },
}

TEACHER_TEAM_AMOUNTS = {
    "国家级优秀教学团队": 60000,
    "省部级优秀教学团队": 30000,
    "校级优秀教学团队": 10000,
    "国家级教学名师": 50000,
    "省部级教学名师": 30000,
    "校级教学名师": 5000,
    "教学新秀": 2000,
}

REFORM_PROJECT_AMOUNTS = {
    ("国家级", "重点"): 30000,
    ("国家级", "重大"): 30000,
    ("国家级", "一般"): 15000,
    ("省部级", "重点"): 10000,
    ("省部级", "A类"): 6000,
    ("省部级", "职业教育重点"): 6000,
    ("省部级", "B类"): 3000,
    ("省部级", "职业教育一般"): 3000,
}

QUALITY_AND_LECTURE_AMOUNTS = {
    "一等奖": 3000,
    "二等奖": 2000,
    "三等奖": 1000,
}

SANQUAN_AMOUNTS = {
    "国家级三全育人综合改革示范校": 80000,
    "自治区级三全育人综合改革示范校": 40000,
    "国家级三全育人综合改革示范院系": 40000,
    "自治区级三全育人综合改革示范院系": 20000,
}

TEACHING_MANAGEMENT_AMOUNTS = {
    "国家级虚拟教研室": 50000,
    "国家级示范中心": 50000,
    "省部级虚拟教研室": 30000,
    "省部级示范中心": 30000,
    "自治区级普通本科高校基层教学组织": 20000,
    "学校教学管理工作先进单位": 15000,
    "学校教研室工作先进单位": 5000,
}

COMPETITION_LEVEL_RECOGNITION = {
    "全国高校教师教学创新大赛": "国家级",
    "全国高校青年教师教学竞赛": "国家级",
    "全国高校思想政治理论课教学展示活动": "省部级",
    "外研社教学之星大赛": "省部级",
    "全国高等院校英语教师教学基本功大赛": "省部级",
    "外教社杯全国高校外语教学大赛": "省部级",
    "广西高校教育教学数字化大赛": "市厅级",
    "全区高校学习习近平新时代中国特色社会主义思想示范课堂": "市厅级",
    "广西高校思政课教师教学基本功暨精彩一课": "市厅级",
    "广西高校思想政治工作优秀工作案例": "市厅级",
    "广西高校壮美广西系列思政课示范课堂": "市厅级",
    "全区高校就业创业课程精彩一课教学大赛": "市厅级",
    "广西壮族自治区大中专院校体育教师教学技能大赛": "市厅级",
    "中国国际大学生创新大赛": "国家级",
    "挑战杯全国大学生课外学术科技作品竞赛": "国家级",
    "挑战杯中国大学生创业计划大赛": "国家级",
    "中华职业教育创新创业大赛": "国家级",
    "ACM-ICPC国际大学生程序设计竞赛": "省部级",
    "全国大学生数学建模竞赛": "省部级",
    "全国大学生电子设计竞赛": "省部级",
    "全国大学生机械创新设计大赛": "省部级",
    "全国大学生智能汽车竞赛": "省部级",
    "全国大学生电子商务创新创意及创业挑战赛": "省部级",
    "中国大学生工程实践与创新能力大赛": "省部级",
    "外研社全国大学生英语系列赛": "省部级",
    "全国大学生创新创业训练计划年会展示": "省部级",
    "全国大学生机器人大赛": "省部级",
    "全国大学生市场调查与分析大赛": "省部级",
    "全国大学生先进成图技术与产品信息建模创新大赛": "省部级",
    "全国三维数字化创新设计大赛": "省部级",
    "西门子杯中国智能制造挑战赛": "省部级",
    "中国大学生服务外包创新创业大赛": "省部级",
    "中国大学生计算机设计大赛": "省部级",
    "中国高校计算机大赛": "省部级",
    "蓝桥杯全国软件和信息技术专业人才大赛": "省部级",
    "全国大学生光电设计竞赛": "省部级",
    "全国大学生集成电路创新创业大赛": "省部级",
    "全国大学生信息安全竞赛": "省部级",
    "中国大学生机械工程创新创意大赛": "省部级",
    "中国机器人大赛暨RoboCup机器人世界杯中国赛": "省部级",
    "中国软件杯大学生软件设计大赛": "省部级",
    "中美青年创客大赛": "省部级",
    "睿抗机器人开发者大赛": "省部级",
    "大唐杯全国大学生新一代信息通信技术大赛": "省部级",
    "华为ICT大赛": "省部级",
    "全国大学生嵌入式芯片与系统设计竞赛": "省部级",
    "全国高校商业精英挑战赛": "省部级",
    "学创杯全国大学生创业综合模拟大赛": "省部级",
    "中国高校智能机器人创意大赛": "省部级",
    "中国机器人及人工智能大赛": "省部级",
    "21世纪杯全国英语演讲比赛": "省部级",
    "iCAN大学生创新创业大赛": "省部级",
    "工行杯全国大学生金融科技创新大赛": "省部级",
    "中华经典诵写讲大赛": "省部级",
    "外教社杯全国高校学生跨文化能力大赛": "省部级",
    "百度之星程序设计大赛": "省部级",
    "全国大学生工业设计大赛": "省部级",
    "全国大学生计算机系统统能力大赛": "省部级",
    "全国大学生物联网设计竞赛": "省部级",
    "全国大学生信息安全与对抗技术竞赛": "省部级",
    "全国大学生统计建模大赛": "省部级",
    "全国大学生数字媒体科技作品及创意竞赛": "省部级",
    "全国企业竞争模拟大赛": "省部级",
    "全国高等院校数智化企业经营沙盘大赛": "省部级",
    "全球校园人工智能算法精英大赛": "省部级",
    "科云杯全国大学生财会职业能力大赛": "省部级",
    "世界技能大赛": "省部级",
    "世界技能大赛中国选拔赛": "省部级",
    "一带一路暨金砖国家技能发展与技术创新大赛": "省部级",
    "码蹄杯全国职业院校程序设计大赛": "省部级",
    "大学生讲思政课公开课展示活动": "省部级",
    "我心中的思政课全国高校大学生微电影展示活动": "省部级",
    "全国大学生职业规划大赛": "省部级",
    "全国大学生英语竞赛": "省部级",
    "全国大学生数学竞赛": "省部级",
    "世界职业院校技能大赛法律实务赛项": "省部级",
    "中华经典诵读系列比赛": "省部级",
    "华为鲲鹏昇腾系列竞赛": "省部级",
    "外教社词达人杯全国大学生英语词汇能力大赛": "省部级",
    "广西校园中华经典诵读比赛": "市厅级",
    "全国公安院校智慧侦查技能大赛": "市厅级",
    "黄河流域公安院校现场勘查比赛": "市厅级",
    "警务英语大赛": "市厅级",
    "大数据智能警务挑战赛": "市厅级",
    "公安院校师生智慧交通警务教学技能创新大赛": "市厅级",
    "广西八桂法声比赛": "市厅级",
    "全区高校思想政治理论课研究性学习与实践性教学优秀成果评选活动": "市厅级",
    "全国公安院校图像检验大赛": "市厅级",
    "陆由杯广西高校大学生社会工作实务技能大赛": "市厅级",
    "广西大学生应急救援技术大赛": "市厅级",
    "南宁市创业大赛": "市厅级",
}

REWARD_CATEGORY_LABELS = {
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
}

LEVEL_ALIASES = {
    "national": "国家级",
    "international": "国家级",
    "国家": "国家级",
    "国家级": "国家级",
    "省级": "省部级",
    "省部级": "省部级",
    "自治区级": "省部级",
    "省（部）级": "省部级",
    "市级": "市厅级",
    "市厅级": "市厅级",
    "市（厅）级": "市厅级",
    "校级": "校级",
    "学校": "校级",
    "university": "校级",
    "college": "院级",
    "院级": "院级",
}

RANK_ALIASES = {
    "grandprize": "特等奖",
    "grand_prize": "特等奖",
    "特等": "特等奖",
    "特等奖": "特等奖",
    "firstprize": "一等奖",
    "first_prize": "一等奖",
    "一等": "一等奖",
    "一等奖": "一等奖",
    "secondprize": "二等奖",
    "second_prize": "二等奖",
    "二等": "二等奖",
    "二等奖": "二等奖",
    "thirdprize": "三等奖",
    "third_prize": "三等奖",
    "三等": "三等奖",
    "三等奖": "三等奖",
}


def calculate_teaching_reward(achievement: Any) -> Dict[str, Any]:
    content = achievement.content_json if isinstance(achievement.content_json, dict) else {}
    text = _combined_text(achievement, content)
    category_hint = _normal_reward_category(
        content.get("teaching_reward_category")
        or content.get("reward_category")
        or content.get("category")
        or getattr(achievement, "type", "")
    )
    level = _normal_level(content.get("award_level") or content.get("level") or content.get("project_level"))
    rank = _normal_rank(content.get("award") or content.get("award_rank") or content.get("rank") or content.get("prize"))
    inferred_level = _infer_competition_level(text)
    if inferred_level:
        level = inferred_level

    result = _base_result()

    def matched(category: str, amount: Optional[int], basis: str, notes: str = "") -> Dict[str, Any]:
        data = _base_result()
        data.update({
            "matched": amount is not None,
            "reward_category": category,
            "amount": amount,
            "basis": basis,
            "recognized_level": level,
            "recognized_rank": rank,
            "notes": notes,
        })
        return data

    if category_hint == "teaching_achievement" or _has_any(text, ["教学成果"]):
        amount = TEACHING_ACHIEVEMENT_AMOUNTS.get((level, rank))
        return matched("教学成果类", amount, f"{level or '-'}教学成果{rank or ''}")

    if category_hint == "major_construction" or _has_any(text, ["特色专业", "一流专业", "优势专业", "示范专业", "现代产业学院"]):
        amount = MAJOR_CONSTRUCTION_AMOUNTS.get(level)
        return matched("专业建设类", amount, f"{level or '-'}特色（一流、优势、示范等）专业/现代产业学院")

    if category_hint == "course_construction" or _has_any(text, ["精品课程", "一流课程", "示范课程"]):
        amount = COURSE_CONSTRUCTION_AMOUNTS.get(level)
        return matched("课程建设类", amount, f"{level or '-'}精品（一流、示范等）课程")

    if category_hint == "textbook_construction" or _has_any(text, ["教材"]):
        amount = TEXTBOOK_AWARD_AMOUNTS.get((level, rank))
        if amount:
            return matched("教材建设类", amount, f"{level}优秀教材{rank}")
        word_count = _as_int(content.get("word_count") or content.get("words"))
        if word_count:
            amount = 8000 if word_count >= 200000 else 6000
            return matched("教材建设类", amount, "经学校立项正式出版教材", "20万字以上8000元，20万字以下6000元。")
        return matched("教材建设类", None, "教材出版或教材获奖", "需提供教材字数或教材获奖级别/等级。")

    if category_hint == "practice_teaching" or _has_any(text, ["实训基地", "校外实践教学基地", "重点实验室"]):
        item = _first_item(text, ["示范性实训基地", "校外实践教学基地", "重点实验室"])
        amount = PRACTICE_CONSTRUCTION_AMOUNTS.get((level, item))
        return matched("实践教学建设类", amount, f"{level or '-'}{item or '实践教学建设项目'}")

    if category_hint == "teaching_competition" or _has_any(text, ["教学竞赛", "教师教学创新竞赛", "青年教师教学竞赛", "指导学生", "大学生", "挑战杯", "蓝桥杯", "华为ICT"]):
        kind = "group" if _has_any(text, ["团体", "团队"]) else "individual"
        amount = TEACHING_COMPETITION_AMOUNTS[kind].get((level, rank))
        if _has_any(text, ["指导学生", "指导教师", "advisors"]):
            amount = int(amount / 2) if amount else None
            note = "教师组织指导学生参赛获奖按教师本人参赛获奖标准的二分之一执行；同一教师一年内指导学生比赛获奖奖励金额20000元封顶。"
        else:
            note = "同一项目多名指导教师只按项目奖励一次；团体奖励指多人参加不同单项比赛取得的团队奖励。"
        return matched("教学竞赛类", amount, f"{level or '-'}{rank or ''}{'团体' if kind == 'group' else '单项'}奖励", note)

    if category_hint == "teacher_team":
        for key, amount in TEACHER_TEAM_AMOUNTS.items():
            if _compact(key) in _compact(text):
                return matched(REWARD_CATEGORY_LABELS["teacher_team"], amount, key)
        return matched(REWARD_CATEGORY_LABELS["teacher_team"], None, "教师队伍建设奖励", "需提供符合办法的称号名称，如教学名师、优秀基层教学组织、教学团队等。")

    for key, amount in TEACHER_TEAM_AMOUNTS.items():
        if _compact(key) in _compact(text):
            return matched("教师队伍建设类", amount, key)

    if category_hint == "teaching_reform" or _has_any(text, ["教学改革", "教改", "教育科学规划"]):
        project_rank = _project_rank(text, content)
        amount = REFORM_PROJECT_AMOUNTS.get((level, project_rank))
        return matched("教学改革项目奖", amount, f"{level or '-'}教学改革{project_rank or ''}项目", "立项年度发放50%，结题年度发放50%。")

    if category_hint == "teaching_quality" or _has_any(text, ["教学质量奖", "教学质量综合测评"]):
        amount = QUALITY_AND_LECTURE_AMOUNTS.get(rank)
        return matched("教学质量奖", amount, f"教学质量奖{rank or ''}", "必修课按参评人数前30%评奖；选修课按参评人数前20%评奖。")

    if category_hint == "lecture_competition" or _has_any(text, ["讲课比赛", "青年教师教学竞赛", "教师教学创新竞赛"]):
        amount = QUALITY_AND_LECTURE_AMOUNTS.get(rank)
        return matched("讲课比赛奖", amount, f"讲课比赛{rank or ''}")

    if category_hint == "sanquan_education":
        for key, amount in SANQUAN_AMOUNTS.items():
            if _compact(key) in _compact(text):
                return matched(REWARD_CATEGORY_LABELS["sanquan_education"], amount, key)
        return matched(REWARD_CATEGORY_LABELS["sanquan_education"], None, "三全育人专项奖励", "需提供符合办法的育人称号或项目名称。")

    for key, amount in SANQUAN_AMOUNTS.items():
        if _compact(key) in _compact(text):
            return matched("三全育人专项奖", amount, key)

    if category_hint == "teaching_management":
        for key, amount in TEACHING_MANAGEMENT_AMOUNTS.items():
            if _compact(key) in _compact(text):
                return matched(REWARD_CATEGORY_LABELS["teaching_management"], amount, key)
        return matched(REWARD_CATEGORY_LABELS["teaching_management"], None, "教学管理奖励", "需提供符合办法的教学管理获奖名称。")

    for key, amount in TEACHING_MANAGEMENT_AMOUNTS.items():
        if _compact(key) in _compact(text):
            return matched("教学管理奖", amount, key)

    if category_hint == "ideological_political" or _has_any(text, ["思政课教学改革", "思政课教学竞赛", "示范课堂", "精彩一课", "理论宣讲", "教学案例"]):
        return matched("思政类教学工作专项奖", None, "思政类教学工作专项奖", "由马克思主义学院组织专家评审并报教务处审定，奖励标准按照学校相关奖励标准执行。")

    result.update({
        "basis": "未匹配到《广西警察学院教学工作奖励办法（2024年修订）》中的可自动计奖条目",
        "recognized_level": level,
        "recognized_rank": rank,
    })
    return result


def _base_result() -> Dict[str, Any]:
    return {
        "matched": False,
        "reward_category": None,
        "amount": None,
        "currency": "CNY",
        "basis": "",
        "recognized_level": None,
        "recognized_rank": None,
        "notes": "",
        "source": "广西警察学院教学工作奖励办法（2024年修订）",
    }


def _combined_text(achievement: Any, content: Dict[str, Any]) -> str:
    pieces = [getattr(achievement, "title", ""), getattr(achievement, "type", "")]
    for value in content.values():
        if isinstance(value, (list, tuple)):
            pieces.extend(str(item) for item in value)
        elif isinstance(value, dict):
            pieces.extend(str(item) for item in value.values())
        elif value is not None:
            pieces.append(str(value))
    return " ".join(pieces)


def _normal_reward_category(value: Any) -> Optional[str]:
    if not value:
        return None
    text = str(value).strip()
    aliases = {
        "teaching_achievement": "teaching_achievement",
        "major_construction": "major_construction",
        "course_construction": "course_construction",
        "textbook_construction": "textbook_construction",
        "practice_teaching": "practice_teaching",
        "teaching_competition": "teaching_competition",
        "competition": "teaching_competition",
        "teacher_team": "teacher_team",
        "teaching_reform": "teaching_reform",
        "teaching_quality": "teaching_quality",
        "lecture_competition": "lecture_competition",
        "sanquan_education": "sanquan_education",
        "teaching_management": "teaching_management",
        "ideological_political": "ideological_political",
    }
    if text in aliases:
        return aliases[text]
    for key, label in REWARD_CATEGORY_LABELS.items():
        if label in text:
            return key
    return None


def _normal_level(value: Any) -> Rank:
    if not value:
        return None
    text = str(value).strip()
    for key, normalized in LEVEL_ALIASES.items():
        if key.lower() in text.lower():
            return normalized
    return text if text in {"国家级", "省部级", "市厅级", "校级", "院级"} else None


def _normal_rank(value: Any) -> Rank:
    if not value:
        return None
    text = str(value).strip()
    for key, normalized in RANK_ALIASES.items():
        if key.lower() in text.lower():
            return normalized
    return text if text in {"特等奖", "一等奖", "二等奖", "三等奖"} else None


def _infer_competition_level(text: str) -> Rank:
    compact_text = _compact(text)
    for name, level in COMPETITION_LEVEL_RECOGNITION.items():
        if _compact(name) in compact_text:
            return level
    if "各省市公安院校" in text:
        return "市厅级"
    return None


def _project_rank(text: str, content: Dict[str, Any]) -> Rank:
    raw = str(content.get("project_rank") or content.get("project_type") or "")
    haystack = f"{raw} {text}"
    if "重大" in haystack:
        return "重大"
    if "重点" in haystack and "职业教育" in haystack:
        return "职业教育重点"
    if "重点" in haystack:
        return "重点"
    if "A类" in haystack or "A 类" in haystack:
        return "A类"
    if "B类" in haystack or "B 类" in haystack:
        return "B类"
    if "职业教育" in haystack and "一般" in haystack:
        return "职业教育一般"
    if "一般" in haystack:
        return "一般"
    return None


def _first_item(text: str, names: list[str]) -> Rank:
    for name in names:
        if name in text:
            return name
    return None


def _has_any(text: str, words: list[str]) -> bool:
    compact_text = _compact(text)
    return any(_compact(word) in compact_text for word in words)


def _compact(text: str) -> str:
    return re.sub(r"[\s（）()\"'“”‘’·&—\-、，,。:：]+", "", text or "").lower()


def _as_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        match = re.search(r"\d+", str(value))
        return int(match.group(0)) if match else None
