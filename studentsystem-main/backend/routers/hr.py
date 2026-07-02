from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from database import get_db
from dependencies import require_student
from models import (
    AchievementStatus,
    BizAchievement,
    HrCareerEvent,
    HrPerformanceRecord,
    HrProfileChangeRequest,
    HrTeacherAttachment,
    HrTeacherProfile,
    HrTitleRule,
    RewardRecognition,
    RewardRule,
    SysStudent,
)
from services.hr_fill_settings import closed_fill_message, fill_settings_to_dict, is_fill_open
from services.hr_reward_service import calculate_structured_reward, summarize_title_gap
from services.reward_policy_labels import (
    POLICY_BASIS,
    request_subcategory,
    reward_content_text,
    reward_label_parts,
)
from services.teaching_reward_rules import calculate_teaching_reward
from utils import error_response, success_response


router = APIRouter(prefix="/api/v1/hr", tags=["HR"])


@router.get("/profile")
async def get_profile(student: SysStudent = Depends(require_student), db: Session = Depends(get_db)):
    profile = ensure_profile(db, student)
    return success_response(data=profile_to_dict(profile))


@router.get("/dashboard")
async def get_dashboard(student: SysStudent = Depends(require_student), db: Session = Depends(get_db)):
    profile = ensure_profile(db, student)
    approved = (
        db.query(BizAchievement)
        .filter(
            BizAchievement.student_id == student.id,
            BizAchievement.status == AchievementStatus.APPROVED,
            BizAchievement.is_deleted == False,
        )
        .all()
    )
    reward_total = 0
    for achievement in approved:
        reward = calculate_teaching_reward(achievement)
        if reward.get("matched") and isinstance(reward.get("amount"), int):
            reward_total += reward["amount"]
    reward_recognitions = (
        db.query(RewardRecognition)
        .filter(RewardRecognition.profile_id == profile.id)
        .order_by(RewardRecognition.created_at.desc())
        .all()
    )
    recognized_reward_total = sum(row.final_amount or 0 for row in reward_recognitions)
    approved_reward_total = sum(
        row.final_amount or 0 for row in reward_recognitions if row.status == "approved"
    )

    latest_performance = (
        db.query(HrPerformanceRecord)
        .filter(HrPerformanceRecord.profile_id == profile.id)
        .order_by(HrPerformanceRecord.year.desc())
        .first()
    )
    title_gap = build_title_gap(db, profile, len(approved))
    return success_response(
        data={
            "profile": profile_to_dict(profile),
            "achievement_summary": {
                "approved_count": len(approved),
                "estimated_reward_total": reward_total,
            },
            "reward_recognition_summary": {
                "count": len(reward_recognitions),
                "total_amount": recognized_reward_total,
                "approved_total_amount": approved_reward_total,
                "pending_count": len([row for row in reward_recognitions if row.status == "pending"]),
            },
            "reward_recognitions": [reward_recognition_to_dict(row) for row in reward_recognitions[:5]],
            "current_performance": performance_to_dict(latest_performance) if latest_performance else None,
            "title_gap": title_gap,
        }
    )


@router.post("/profile/change-request")
async def create_change_request(
    payload: Dict[str, Any],
    student: SysStudent = Depends(require_student),
    db: Session = Depends(get_db),
):
    profile = ensure_profile(db, student)
    req = HrProfileChangeRequest(
        profile_id=profile.id,
        before_data=profile_to_dict(profile),
        after_data=payload,
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return success_response(data=change_request_to_dict(req), msg="资料修改申请已提交")


@router.get("/attachments")
async def list_attachments(student: SysStudent = Depends(require_student), db: Session = Depends(get_db)):
    profile = ensure_profile(db, student)
    rows = (
        db.query(HrTeacherAttachment)
        .filter(HrTeacherAttachment.profile_id == profile.id, HrTeacherAttachment.status == "active")
        .order_by(HrTeacherAttachment.created_at.desc())
        .all()
    )
    return success_response(data=[attachment_to_dict(row) for row in rows])


@router.post("/attachments")
async def upload_attachment(
    attachment_type: str = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...),
    student: SysStudent = Depends(require_student),
    db: Session = Depends(get_db),
):
    from services.file_manager import file_manager

    profile = ensure_profile(db, student)
    saved = await file_manager.save_certificate_permanent(file, student.id)
    row = HrTeacherAttachment(
        profile_id=profile.id,
        attachment_type=attachment_type,
        title=title,
        file_url=saved["file_url"],
        original_filename=saved["original_filename"],
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return success_response(data=attachment_to_dict(row), msg="附件已归档")


@router.get("/fill-settings")
async def get_fill_settings(student: SysStudent = Depends(require_student), db: Session = Depends(get_db)):
    return success_response(data=fill_settings_to_dict(db))


@router.get("/performance")
async def list_performance(student: SysStudent = Depends(require_student), db: Session = Depends(get_db)):
    if not is_fill_open(db, "performance"):
        return error_response(msg=closed_fill_message("performance"), code=403)
    profile = ensure_profile(db, student)
    rows = (
        db.query(HrPerformanceRecord)
        .filter(HrPerformanceRecord.profile_id == profile.id)
        .order_by(HrPerformanceRecord.year.desc())
        .all()
    )
    return success_response(data=[performance_to_dict(row) for row in rows])


@router.get("/title-gap")
async def get_title_gap(
    target_title: Optional[str] = None,
    student: SysStudent = Depends(require_student),
    db: Session = Depends(get_db),
):
    if not is_fill_open(db, "title_check"):
        return error_response(msg=closed_fill_message("title_check"), code=403)
    profile = ensure_profile(db, student)
    approved_count = (
        db.query(BizAchievement)
        .filter(
            BizAchievement.student_id == student.id,
            BizAchievement.status == AchievementStatus.APPROVED,
            BizAchievement.is_deleted == False,
        )
        .count()
    )
    return success_response(data=build_title_gap(db, profile, approved_count, target_title))


@router.get("/reward-recognitions")
async def list_reward_recognitions(
    student: SysStudent = Depends(require_student),
    db: Session = Depends(get_db),
):
    profile = ensure_profile(db, student)
    rows = (
        db.query(RewardRecognition)
        .filter(RewardRecognition.profile_id == profile.id)
        .order_by(RewardRecognition.created_at.desc())
        .all()
    )
    return success_response(data=[reward_recognition_to_dict(row) for row in rows])


@router.post("/reward-recognitions")
async def create_reward_recognition(
    payload: Dict[str, Any],
    student: SysStudent = Depends(require_student),
    db: Session = Depends(get_db),
):
    profile = ensure_profile(db, student)
    payload = {**payload, "profile_id": profile.id}
    calculation = calculate_structured_reward(payload, load_reward_rules(db))
    calculation["request_data"] = dict(payload)
    row = RewardRecognition(
        achievement_id=payload.get("achievement_id"),
        profile_id=profile.id,
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
    return success_response(data=reward_recognition_to_dict(row), msg="奖励认定申请已提交")


def ensure_profile(db: Session, student: SysStudent) -> HrTeacherProfile:
    profile = db.query(HrTeacherProfile).filter(HrTeacherProfile.student_id == student.id).first()
    if profile:
        return profile
    profile = HrTeacherProfile(
        student_id=student.id,
        employee_no=student.student_number,
        name=student.name,
        department=student.major,
        email=getattr(student.user, "email", None),
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def build_title_gap(
    db: Session,
    profile: HrTeacherProfile,
    approved_count: int,
    target_title: Optional[str] = None,
) -> Dict[str, Any]:
    query = db.query(HrTitleRule).filter(HrTitleRule.is_active == True)
    if target_title:
        query = query.filter(HrTitleRule.target_title == target_title)
    rule = query.order_by(HrTitleRule.id.asc()).first()
    if not rule:
        return {
            "target_title": target_title or "副教授",
            "eligible": False,
            "missing_items": ["管理员尚未配置职称评审规则"],
            "satisfied_items": [],
        }
    performances = [
        performance_to_dict(row)
        for row in db.query(HrPerformanceRecord)
        .filter(HrPerformanceRecord.profile_id == profile.id)
        .all()
    ]
    attachments = [
        row.attachment_type
        for row in db.query(HrTeacherAttachment)
        .filter(HrTeacherAttachment.profile_id == profile.id, HrTeacherAttachment.status == "active")
        .all()
    ]
    return summarize_title_gap(
        profile_to_dict(profile),
        approved_count,
        performances,
        title_rule_to_dict(rule),
        attachments,
    )


def profile_to_dict(profile: HrTeacherProfile) -> Dict[str, Any]:
    return {
        "id": profile.id,
        "student_id": profile.student_id,
        "employee_no": profile.employee_no,
        "name": profile.name,
        "department": profile.department,
        "education": profile.education,
        "degree": profile.degree,
        "position": profile.position,
        "current_title": profile.current_title,
        "title_start_date": profile.title_start_date.isoformat() if profile.title_start_date else None,
        "employment_type": profile.employment_type,
        "hire_date": profile.hire_date.isoformat() if profile.hire_date else None,
        "contract_start": profile.contract_start.isoformat() if profile.contract_start else None,
        "contract_end": profile.contract_end.isoformat() if profile.contract_end else None,
        "phone": profile.phone,
        "email": profile.email,
        "office_location": profile.office_location,
        "bio": profile.bio,
        "status": profile.status,
    }


def apply_profile_change(profile: HrTeacherProfile, data: Dict[str, Any]) -> None:
    allowed = {
        "education",
        "degree",
        "position",
        "current_title",
        "employment_type",
        "phone",
        "email",
        "office_location",
        "bio",
        "department",
    }
    for key, value in data.items():
        if key in allowed:
            setattr(profile, key, value)


def attachment_to_dict(row: HrTeacherAttachment) -> Dict[str, Any]:
    return {
        "id": row.id,
        "attachment_type": row.attachment_type,
        "title": row.title,
        "file_url": row.file_url,
        "original_filename": row.original_filename,
        "status": row.status,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


def performance_to_dict(row: HrPerformanceRecord) -> Dict[str, Any]:
    return {
        "id": row.id,
        "year": row.year,
        "period_type": row.period_type,
        "teaching_score": row.teaching_score,
        "evaluation_score": row.evaluation_score,
        "reward_bonus": row.reward_bonus,
        "admin_adjustment": row.admin_adjustment,
        "final_score": row.final_score,
        "grade": row.grade,
        "status": row.status,
        "note": row.note,
    }


def title_rule_to_dict(row: HrTitleRule) -> Dict[str, Any]:
    return {
        "id": row.id,
        "target_title": row.target_title,
        "employment_type": row.employment_type,
        "min_approved_achievements": row.min_approved_achievements,
        "required_performance_grade": row.required_performance_grade,
        "min_years_in_current_title": row.min_years_in_current_title,
        "required_attachment_types": row.required_attachment_types or [],
    }


def change_request_to_dict(row: HrProfileChangeRequest) -> Dict[str, Any]:
    return {
        "id": row.id,
        "profile_id": row.profile_id,
        "before_data": row.before_data,
        "after_data": row.after_data,
        "status": row.status,
        "audit_comment": row.audit_comment,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "audited_at": row.audited_at.isoformat() if row.audited_at else None,
    }


def reward_recognition_to_dict(row: RewardRecognition) -> Dict[str, Any]:
    detail = row.calculation_detail or {}
    request_data = detail.get("request_data") or {}
    subcategory = request_subcategory(request_data, row.category)
    label_parts = reward_label_parts(row.category, row.level, row.rank, subcategory)
    return {
        "id": row.id,
        "achievement_id": row.achievement_id,
        "profile_id": row.profile_id,
        "category": row.category,
        "category_text": label_parts["category_text"],
        "subcategory_text": label_parts["subcategory_text"],
        "level": row.level,
        "level_text": label_parts["level_text"],
        "rank": row.rank,
        "rank_text": label_parts["rank_text"],
        "base_amount": row.base_amount,
        "final_amount": row.final_amount,
        "content": reward_content_text(row.category, row.level, row.rank, subcategory),
        "policy_basis": row.policy_basis or POLICY_BASIS,
        "calculation_detail": row.calculation_detail,
        "status": row.status,
        "audit_comment": row.audit_comment,
        "batch_id": row.batch_id,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


def load_reward_rules(db: Session):
    return [
        {
            "category": row.category,
            "subcategory": row.subcategory,
            "level": row.level,
            "rank": row.rank,
            "amount": row.amount,
            "manual_required": row.manual_required,
            "staged": row.staged,
            "annual_cap": row.annual_cap,
        }
        for row in db.query(RewardRule).filter(RewardRule.is_active == True).order_by(RewardRule.id.desc()).all()
    ]
