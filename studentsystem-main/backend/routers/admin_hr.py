from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from database import get_db
from dependencies import require_admin
from models import (
    AchievementStatus,
    BizAchievement,
    CompetitionCatalog,
    HrCareerEvent,
    HrPerformanceRecord,
    HrProfileChangeRequest,
    HrTeacherAttachment,
    HrTeacherProfile,
    HrTitleApplication,
    HrTitleRule,
    RewardBatch,
    RewardRecognition,
    RewardRule,
    SysStudent,
    SysUser,
)
from routers.hr import (
    apply_profile_change,
    attachment_to_dict,
    build_title_gap,
    change_request_to_dict,
    performance_to_dict,
    profile_to_dict,
    title_rule_to_dict,
    load_reward_rules,
)
from services.hr_reward_service import calculate_structured_reward
from services.hr_fill_settings import fill_settings_to_dict, update_fill_setting
from services.reward_policy_labels import (
    POLICY_BASIS,
    reward_content_text as build_reward_content_text,
    request_subcategory,
    reward_label_parts,
)
from services.reward_policy_seed import DEFAULT_COMPETITIONS, DEFAULT_REWARD_RULES, POLICY_VERSION
from utils import error_response, success_response


router = APIRouter(prefix="/api/v1/admin/hr", tags=["Admin HR"])
reward_router = APIRouter(prefix="/api/v1/admin/reward", tags=["Admin Reward"])


@router.get("/teachers")
async def list_teachers(
    department: Optional[str] = Query(None),
    employment_type: Optional[str] = Query(None),
    title: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: SysUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    seed_profiles(db)
    query = db.query(HrTeacherProfile)
    if department:
        query = query.filter(HrTeacherProfile.department.like(f"%{department}%"))
    if employment_type:
        query = query.filter(HrTeacherProfile.employment_type == employment_type)
    if title:
        query = query.filter(HrTeacherProfile.current_title == title)
    total = query.count()
    rows = query.order_by(HrTeacherProfile.id.asc()).offset((page - 1) * page_size).limit(page_size).all()
    return success_response(data={"list": [profile_to_dict(row) for row in rows], "total": total})


@router.get("/teachers/{profile_id}")
async def get_teacher_detail(
    profile_id: int = Path(...),
    admin: SysUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    profile = db.query(HrTeacherProfile).filter(HrTeacherProfile.id == profile_id).first()
    if not profile:
        return error_response(msg="教师档案不存在", code=404)
    attachments = db.query(HrTeacherAttachment).filter(HrTeacherAttachment.profile_id == profile_id).all()
    performances = db.query(HrPerformanceRecord).filter(HrPerformanceRecord.profile_id == profile_id).all()
    events = db.query(HrCareerEvent).filter(HrCareerEvent.profile_id == profile_id).order_by(HrCareerEvent.event_date.desc()).all()
    approved_count = (
        db.query(BizAchievement)
        .filter(
            BizAchievement.student_id == profile.student_id,
            BizAchievement.status == AchievementStatus.APPROVED,
            BizAchievement.is_deleted == False,
        )
        .count()
    )
    return success_response(
        data={
            "profile": profile_to_dict(profile),
            "attachments": [attachment_to_dict(row) for row in attachments],
            "performances": [performance_to_dict(row) for row in performances],
            "career_events": [career_event_to_dict(row) for row in events],
            "title_gap": build_title_gap(db, profile, approved_count),
        }
    )


@router.get("/change-requests")
async def list_change_requests(
    status: Optional[str] = Query(None),
    admin: SysUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(HrProfileChangeRequest)
    if status:
        query = query.filter(HrProfileChangeRequest.status == status)
    rows = query.order_by(HrProfileChangeRequest.created_at.desc()).all()
    data = []
    for row in rows:
        item = change_request_to_dict(row)
        profile = db.query(HrTeacherProfile).filter(HrTeacherProfile.id == row.profile_id).first()
        if profile:
            item.update(
                {
                    "teacher_name": profile.name,
                    "employee_no": profile.employee_no,
                    "department": profile.department,
                }
            )
        data.append(item)
    return success_response(data=data)


@router.get("/fill-settings")
async def get_fill_settings(admin: SysUser = Depends(require_admin), db: Session = Depends(get_db)):
    return success_response(data=fill_settings_to_dict(db))


@router.patch("/fill-settings")
async def patch_fill_settings(
    payload: Dict[str, Any],
    admin: SysUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    feature = payload.get("feature")
    is_open = payload.get("is_open")
    if not isinstance(is_open, bool):
        return error_response(msg="is_open 必须为布尔值", code=400)
    try:
        data = update_fill_setting(db, feature, is_open, updated_by=admin.id)
    except ValueError as exc:
        return error_response(msg=str(exc), code=400)
    action = "开放" if is_open else "关闭"
    return success_response(data=data, msg=f"{action}填写已更新")


@router.get("/performance")
async def list_performance(
    profile_id: Optional[int] = Query(None),
    year: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: SysUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(HrPerformanceRecord, HrTeacherProfile).join(
        HrTeacherProfile,
        HrPerformanceRecord.profile_id == HrTeacherProfile.id,
    )
    if profile_id:
        query = query.filter(HrPerformanceRecord.profile_id == profile_id)
    if year:
        query = query.filter(HrPerformanceRecord.year == year)
    if status:
        query = query.filter(HrPerformanceRecord.status == status)
    total = query.count()
    rows = (
        query.order_by(HrPerformanceRecord.year.desc(), HrPerformanceRecord.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    data = []
    for record, profile in rows:
        item = performance_to_dict(record)
        item.update(
            {
                "profile_id": record.profile_id,
                "teacher_name": profile.name,
                "employee_no": profile.employee_no,
                "department": profile.department,
            }
        )
        data.append(item)
    return success_response(data={"list": data, "total": total})


@router.patch("/change-requests/{request_id}/audit")
async def audit_change_request(
    payload: Dict[str, Any],
    request_id: int = Path(...),
    admin: SysUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    row = db.query(HrProfileChangeRequest).filter(HrProfileChangeRequest.id == request_id).first()
    if not row:
        return error_response(msg="修改申请不存在", code=404)
    action = payload.get("action")
    if action not in {"approve", "reject"}:
        return error_response(msg="action 必须为 approve 或 reject", code=400)
    profile = db.query(HrTeacherProfile).filter(HrTeacherProfile.id == row.profile_id).first()
    if action == "approve" and profile:
        apply_profile_change(profile, row.after_data or {})
        row.status = "approved"
    else:
        row.status = "rejected"
    row.audit_comment = payload.get("comment")
    row.audited_at = datetime.utcnow()
    db.commit()
    return success_response(data=change_request_to_dict(row), msg="审核完成")


@router.post("/performance")
async def create_performance(
    payload: Dict[str, Any],
    admin: SysUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        profile_id = int(payload.get("profile_id") or 0)
    except (TypeError, ValueError):
        return error_response(msg="请选择有效教师档案", code=400)
    if profile_id <= 0:
        return error_response(msg="请选择有效教师档案", code=400)
    profile = db.query(HrTeacherProfile).filter(HrTeacherProfile.id == profile_id).first()
    if not profile:
        return error_response(msg="教师档案不存在，请先选择有效档案", code=404)

    final_score = float(payload.get("final_score") or 0)
    if not final_score:
        final_score = (
            float(payload.get("teaching_score") or 0)
            + float(payload.get("evaluation_score") or 0)
            + float(payload.get("reward_bonus") or 0)
            + float(payload.get("admin_adjustment") or 0)
        )
    row = HrPerformanceRecord(
        profile_id=profile_id,
        year=int(payload.get("year")),
        period_type=payload.get("period_type") or "annual",
        teaching_score=float(payload.get("teaching_score") or 0),
        evaluation_score=float(payload.get("evaluation_score") or 0),
        reward_bonus=float(payload.get("reward_bonus") or 0),
        admin_adjustment=float(payload.get("admin_adjustment") or 0),
        final_score=final_score,
        grade=payload.get("grade"),
        status=payload.get("status") or "published",
        note=payload.get("note"),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return success_response(data=performance_to_dict(row), msg="绩效记录已保存")


@router.patch("/performance/{record_id}")
async def update_performance(
    payload: Dict[str, Any],
    record_id: int = Path(...),
    admin: SysUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    row = db.query(HrPerformanceRecord).filter(HrPerformanceRecord.id == record_id).first()
    if not row:
        return error_response(msg="绩效记录不存在", code=404)
    for key in ["teaching_score", "evaluation_score", "reward_bonus", "admin_adjustment", "final_score"]:
        if key in payload:
            setattr(row, key, float(payload[key] or 0))
    for key in ["grade", "status", "note", "period_type"]:
        if key in payload:
            setattr(row, key, payload[key])
    db.commit()
    return success_response(data=performance_to_dict(row), msg="绩效记录已更新")


@router.post("/title-rules")
async def create_title_rule(
    payload: Dict[str, Any],
    admin: SysUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    row = HrTitleRule(
        target_title=payload.get("target_title"),
        employment_type=payload.get("employment_type") or "all",
        min_approved_achievements=int(payload.get("min_approved_achievements") or 0),
        required_performance_grade=payload.get("required_performance_grade"),
        min_years_in_current_title=int(payload.get("min_years_in_current_title") or 0),
        required_attachment_types=payload.get("required_attachment_types") or [],
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return success_response(data=title_rule_to_dict(row), msg="职称规则已保存")


@router.get("/title-rules")
async def list_title_rules(admin: SysUser = Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.query(HrTitleRule).filter(HrTitleRule.is_active == True).order_by(HrTitleRule.id.desc()).all()
    return success_response(data=[title_rule_to_dict(row) for row in rows])


@router.get("/title-applications")
async def list_title_applications(admin: SysUser = Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.query(HrTitleApplication).order_by(HrTitleApplication.created_at.desc()).all()
    return success_response(data=[title_application_to_dict(row) for row in rows])


@reward_router.get("/recognitions")
async def list_reward_recognitions(
    status: Optional[str] = Query(None),
    admin: SysUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(RewardRecognition)
    if status:
        query = query.filter(RewardRecognition.status == status)
    rows = query.order_by(RewardRecognition.created_at.desc()).all()
    return success_response(data=[recognition_to_dict(row, db) for row in rows])


@reward_router.get("/assistant-summary")
async def get_reward_assistant_summary(admin: SysUser = Depends(require_admin), db: Session = Depends(get_db)):
    rows = (
        db.query(RewardRecognition, HrTeacherProfile)
        .join(HrTeacherProfile, RewardRecognition.profile_id == HrTeacherProfile.id)
        .filter(RewardRecognition.status == "approved")
        .order_by(HrTeacherProfile.id.asc(), RewardRecognition.audited_at.desc(), RewardRecognition.created_at.desc())
        .all()
    )
    grouped: Dict[int, Dict[str, Any]] = {}
    for recognition, profile in rows:
        item = grouped.setdefault(
            profile.id,
            {
                "profile_id": profile.id,
                "teacher_name": profile.name,
                "employee_no": profile.employee_no,
                "department": profile.department,
                "approved_count": 0,
                "total_amount": 0,
                "awards": [],
            },
        )
        amount = int(recognition.final_amount or 0)
        item["approved_count"] += 1
        item["total_amount"] += amount
        item["awards"].append(reward_assistant_award_to_dict(recognition))

    teachers = [item for item in grouped.values() if item["approved_count"] >= 2]
    teachers.sort(key=lambda item: (-item["total_amount"], item["teacher_name"] or ""))
    return success_response(
        data={
            "teacher_count": len(teachers),
            "recognition_count": sum(item["approved_count"] for item in teachers),
            "total_amount": sum(item["total_amount"] for item in teachers),
            "teachers": teachers,
        }
    )


@reward_router.get("/rules")
async def list_reward_rules(admin: SysUser = Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.query(RewardRule).filter(RewardRule.is_active == True).order_by(RewardRule.id.desc()).all()
    return success_response(data=[reward_rule_to_dict(row) for row in rows])


@reward_router.post("/rules")
async def create_reward_rule(
    payload: Dict[str, Any],
    admin: SysUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    row = RewardRule(
        policy_version=payload.get("policy_version") or "2024",
        category=payload.get("category"),
        subcategory=payload.get("subcategory"),
        level=payload.get("level"),
        rank=payload.get("rank"),
        amount=int(payload.get("amount") or 0),
        manual_required=bool(payload.get("manual_required") or False),
        staged=bool(payload.get("staged") or False),
        annual_cap=payload.get("annual_cap"),
        allow_duplicate=bool(payload.get("allow_duplicate") or False),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return success_response(data=reward_rule_to_dict(row), msg="奖励规则已保存")


@reward_router.get("/competitions")
async def list_competitions(admin: SysUser = Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.query(CompetitionCatalog).filter(CompetitionCatalog.is_active == True).order_by(CompetitionCatalog.id.desc()).all()
    return success_response(data=[competition_to_dict(row) for row in rows])


@reward_router.post("/competitions")
async def create_competition(
    payload: Dict[str, Any],
    admin: SysUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    row = CompetitionCatalog(
        name=payload.get("name"),
        competition_type=payload.get("competition_type") or "student",
        max_level=payload.get("max_level"),
        organizer=payload.get("organizer"),
        policy_version=payload.get("policy_version") or "2024",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return success_response(data=competition_to_dict(row), msg="赛事级别已保存")


@reward_router.post("/policy-2024/init")
async def init_2024_reward_policy(admin: SysUser = Depends(require_admin), db: Session = Depends(get_db)):
    rule_count = 0
    competition_count = 0
    for item in DEFAULT_REWARD_RULES:
        exists = (
            db.query(RewardRule)
            .filter(
                RewardRule.policy_version == POLICY_VERSION,
                RewardRule.category == item.get("category"),
                RewardRule.subcategory == item.get("subcategory"),
                RewardRule.level == item.get("level"),
                RewardRule.rank == item.get("rank"),
            )
            .first()
        )
        if exists:
            continue
        db.add(
            RewardRule(
                policy_version=POLICY_VERSION,
                category=item.get("category"),
                subcategory=item.get("subcategory"),
                level=item.get("level"),
                rank=item.get("rank"),
                amount=int(item.get("amount") or 0),
                manual_required=bool(item.get("manual_required") or False),
                staged=bool(item.get("staged") or False),
                annual_cap=item.get("annual_cap"),
                allow_duplicate=bool(item.get("allow_duplicate") or False),
            )
        )
        rule_count += 1

    for item in DEFAULT_COMPETITIONS:
        exists = db.query(CompetitionCatalog).filter(CompetitionCatalog.name == item["name"]).first()
        if exists:
            continue
        db.add(
            CompetitionCatalog(
                name=item["name"],
                competition_type=item.get("competition_type") or "student",
                max_level=item.get("max_level"),
                organizer=item.get("organizer"),
                policy_version=POLICY_VERSION,
            )
        )
        competition_count += 1

    db.commit()
    return success_response(
        data={
            "policy_version": POLICY_VERSION,
            "inserted_rules": rule_count,
            "inserted_competitions": competition_count,
            "total_seed_rules": len(DEFAULT_REWARD_RULES),
            "total_seed_competitions": len(DEFAULT_COMPETITIONS),
        },
        msg="2024版教学奖励政策已初始化",
    )


@reward_router.post("/recognitions")
async def create_reward_recognition(
    payload: Dict[str, Any],
    admin: SysUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    calculation = calculate_structured_reward(payload, load_reward_rules(db))
    calculation["request_data"] = dict(payload)
    row = RewardRecognition(
        achievement_id=payload.get("achievement_id"),
        profile_id=payload.get("profile_id"),
        category=payload.get("category"),
        level=calculation.get("recognized_level"),
        rank=calculation.get("recognized_rank"),
        base_amount=calculation.get("base_amount") or 0,
        final_amount=calculation.get("final_amount") or 0,
        policy_basis=calculation.get("policy_basis"),
        calculation_detail=calculation,
        status="pending",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return success_response(data=recognition_to_dict(row), msg="奖励认定已创建")


@reward_router.patch("/recognitions/{recognition_id}/audit")
async def audit_reward_recognition(
    payload: Dict[str, Any],
    recognition_id: int = Path(...),
    admin: SysUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    row = db.query(RewardRecognition).filter(RewardRecognition.id == recognition_id).first()
    if not row:
        return error_response(msg="奖励认定不存在", code=404)
    action = payload.get("action")
    if action not in {"approve", "reject"}:
        return error_response(msg="action 必须为 approve 或 reject", code=400)
    row.status = "approved" if action == "approve" else "rejected"
    if "final_amount" in payload:
        row.final_amount = int(payload.get("final_amount") or 0)
    row.audit_comment = payload.get("comment")
    row.audited_at = datetime.utcnow()
    sync_linked_achievement_status(db, row)
    db.commit()
    return success_response(data=recognition_to_dict(row, db), msg="奖励认定审核完成")


@reward_router.post("/batches")
async def create_reward_batch(
    payload: Dict[str, Any],
    admin: SysUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    year = int(payload.get("year"))
    batch = RewardBatch(year=year, name=payload.get("name") or f"{year} 年教学奖励批次")
    db.add(batch)
    db.flush()
    ids = payload.get("recognition_ids") or []
    if ids:
        rows = db.query(RewardRecognition).filter(RewardRecognition.id.in_(ids)).all()
    else:
        rows = db.query(RewardRecognition).filter(RewardRecognition.status == "approved", RewardRecognition.batch_id == None).all()
    total = 0
    for row in rows:
        row.batch_id = batch.id
        total += row.final_amount or 0
    batch.total_amount = total
    db.commit()
    db.refresh(batch)
    return success_response(data=batch_to_dict(batch), msg="奖励批次已创建")


@reward_router.get("/batches")
async def list_reward_batches(admin: SysUser = Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.query(RewardBatch).order_by(RewardBatch.created_at.desc()).all()
    return success_response(data=[batch_to_dict(row) for row in rows])


def seed_profiles(db: Session) -> None:
    students = db.query(SysStudent).all()
    existing = {row.student_id for row in db.query(HrTeacherProfile).all()}
    changed = False
    for student in students:
        if student.id not in existing:
            db.add(
                HrTeacherProfile(
                    student_id=student.id,
                    employee_no=student.student_number,
                    name=student.name,
                    department=student.major,
                )
            )
            changed = True
    if changed:
        db.commit()


def career_event_to_dict(row: HrCareerEvent) -> Dict[str, Any]:
    return {
        "id": row.id,
        "event_type": row.event_type,
        "event_date": row.event_date.isoformat() if row.event_date else None,
        "from_value": row.from_value,
        "to_value": row.to_value,
        "document_url": row.document_url,
        "note": row.note,
    }


def title_application_to_dict(row: HrTitleApplication) -> Dict[str, Any]:
    return {
        "id": row.id,
        "profile_id": row.profile_id,
        "target_title": row.target_title,
        "status": row.status,
        "gap_result": row.gap_result,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


def sync_linked_achievement_status(db: Session, row: RewardRecognition) -> None:
    if not row.achievement_id:
        return
    achievement = db.query(BizAchievement).filter(BizAchievement.id == row.achievement_id).first()
    if not achievement:
        return
    if row.status == "approved":
        achievement.status = AchievementStatus.APPROVED
        student = db.query(SysStudent).filter(SysStudent.id == achievement.student_id).first()
        if student:
            student.persona_cache = None
    elif row.status == "rejected":
        achievement.status = AchievementStatus.REJECTED
    achievement.audit_comment = row.audit_comment


def recognition_to_dict(row: RewardRecognition, db: Optional[Session] = None) -> Dict[str, Any]:
    detail = row.calculation_detail or {}
    request_data = detail.get("request_data") or {}
    subcategory = request_subcategory(request_data, row.category)
    label_parts = reward_label_parts(row.category, row.level, row.rank, subcategory)
    profile = db.query(HrTeacherProfile).filter(HrTeacherProfile.id == row.profile_id).first() if db and row.profile_id else None
    achievement = db.query(BizAchievement).filter(BizAchievement.id == row.achievement_id).first() if db and row.achievement_id else None
    return {
        "id": row.id,
        "achievement_id": row.achievement_id,
        "profile_id": row.profile_id,
        "teacher_name": profile.name if profile else None,
        "employee_no": profile.employee_no if profile else None,
        "department": profile.department if profile else None,
        "achievement_title": achievement.title if achievement else request_data.get("achievement_title"),
        "achievement_type": achievement.type if achievement else request_data.get("achievement_domain"),
        "evidence_url": achievement.evidence_url if achievement else request_data.get("evidence_url"),
        "declared_award": request_data.get("award"),
        "declared_bonus": request_data.get("declared_bonus"),
        "category": row.category,
        "category_text": label_parts["category_text"],
        "subcategory_text": label_parts["subcategory_text"],
        "level": row.level,
        "level_text": label_parts["level_text"],
        "rank": row.rank,
        "rank_text": label_parts["rank_text"],
        "base_amount": row.base_amount,
        "final_amount": row.final_amount,
        "content": reward_content_text(row),
        "policy_basis": row.policy_basis or POLICY_BASIS,
        "calculation_detail": row.calculation_detail,
        "status": row.status,
        "audit_comment": row.audit_comment,
        "batch_id": row.batch_id,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


def reward_assistant_award_to_dict(row: RewardRecognition) -> Dict[str, Any]:
    detail = row.calculation_detail or {}
    request_data = detail.get("request_data") or {}
    subcategory = request_subcategory(request_data, row.category)
    label_parts = reward_label_parts(row.category, row.level, row.rank, subcategory)
    return {
        "id": row.id,
        "category": row.category,
        "category_text": label_parts["category_text"],
        "subcategory_text": label_parts["subcategory_text"],
        "level": row.level,
        "level_text": label_parts["level_text"],
        "rank": row.rank,
        "rank_text": label_parts["rank_text"],
        "final_amount": row.final_amount or 0,
        "content": reward_content_text(row),
        "policy_basis": row.policy_basis or POLICY_BASIS,
        "audited_at": row.audited_at.isoformat() if row.audited_at else None,
    }


def reward_content_text(row: RewardRecognition) -> str:
    detail = row.calculation_detail or {}
    request_data = detail.get("request_data") or {}
    subcategory = request_subcategory(request_data, row.category)
    return build_reward_content_text(row.category, row.level, row.rank, subcategory)


def batch_to_dict(row: RewardBatch) -> Dict[str, Any]:
    return {
        "id": row.id,
        "year": row.year,
        "name": row.name,
        "status": row.status,
        "total_amount": row.total_amount,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "approved_at": row.approved_at.isoformat() if row.approved_at else None,
    }


def reward_rule_to_dict(row: RewardRule) -> Dict[str, Any]:
    return {
        "id": row.id,
        "policy_version": row.policy_version,
        "category": row.category,
        "subcategory": row.subcategory,
        "level": row.level,
        "rank": row.rank,
        "amount": row.amount,
        "manual_required": row.manual_required,
        "staged": row.staged,
        "annual_cap": row.annual_cap,
        "allow_duplicate": row.allow_duplicate,
        "is_active": row.is_active,
    }


def competition_to_dict(row: CompetitionCatalog) -> Dict[str, Any]:
    return {
        "id": row.id,
        "name": row.name,
        "competition_type": row.competition_type,
        "max_level": row.max_level,
        "organizer": row.organizer,
        "policy_version": row.policy_version,
        "is_active": row.is_active,
    }
