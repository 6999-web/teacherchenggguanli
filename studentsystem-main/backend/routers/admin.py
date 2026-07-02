from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Optional
from datetime import datetime
from database import get_db
from schemas import AchievementListResponse, AchievementResponse, AchievementAudit
from utils import success_response, error_response
from models import (
    BizAchievement, AchievementStatus, SysStudent,
    SysTeacher, SysUser, HrProfileChangeRequest, RewardRecognition, HrTeacherProfile
)
from dependencies import require_admin
from services.teaching_reward_rules import calculate_teaching_reward

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


@router.get("/dashboard/audit-summary")
async def get_audit_summary(
    admin: SysUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Aggregate all teacher-submitted audit workloads for the admin dashboard."""
    profile_change_module = _string_status_counts(
        db,
        HrProfileChangeRequest,
        "profile_changes",
        "教师档案变更审核",
        "/admin/hr/change-requests",
    )
    reward_module = _string_status_counts(
        db,
        RewardRecognition,
        "reward_recognitions",
        "教学奖励认定审核",
        "/admin/reward/recognitions",
    )
    modules = [profile_change_module, reward_module]
    return success_response(
        data={
            "total": {
                "submitted": sum(item["submitted"] for item in modules),
                "pending": sum(item["pending"] for item in modules),
                "approved": sum(item["approved"] for item in modules),
                "rejected": sum(item["rejected"] for item in modules),
            },
            "modules": modules,
        }
    )


@router.get("/dashboard/audit-details")
async def get_audit_details(
    status: str = Query("submitted"),
    admin: SysUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Return concrete audit records for dashboard detail buttons."""
    if status not in {"pending", "approved", "rejected", "submitted"}:
        return error_response(msg="status 必须是 pending、approved、rejected 或 submitted", code=400)

    rows = []
    profile_query = db.query(HrProfileChangeRequest)
    reward_query = db.query(RewardRecognition)
    if status != "submitted":
        profile_query = profile_query.filter(HrProfileChangeRequest.status == status)
        reward_query = reward_query.filter(RewardRecognition.status == status)

    for request in profile_query.order_by(HrProfileChangeRequest.created_at.desc()).all():
        profile = db.query(HrTeacherProfile).filter(HrTeacherProfile.id == request.profile_id).first()
        changed_fields = list((request.after_data or {}).keys())
        rows.append(
            {
                "module_key": "profile_changes",
                "module_title": "教师档案变更审核",
                "id": request.id,
                "status": request.status,
                "teacher_name": profile.name if profile else "",
                "employee_no": profile.employee_no if profile else "",
                "department": profile.department if profile else "",
                "title": "教师档案变更",
                "summary": "、".join(changed_fields) if changed_fields else "档案信息变更",
                "amount": None,
                "content": None,
                "audit_comment": request.audit_comment,
                "created_at": request.created_at.isoformat() if request.created_at else None,
                "audited_at": request.audited_at.isoformat() if request.audited_at else None,
                "route": "/admin/hr/change-requests",
                "detail": {
                    "profile_id": request.profile_id,
                    "before_data": request.before_data or {},
                    "after_data": request.after_data or {},
                },
            }
        )

    for recognition in reward_query.order_by(RewardRecognition.created_at.desc()).all():
        profile = db.query(HrTeacherProfile).filter(HrTeacherProfile.id == recognition.profile_id).first()
        achievement = (
            db.query(BizAchievement).filter(BizAchievement.id == recognition.achievement_id).first()
            if recognition.achievement_id
            else None
        )
        detail = recognition.calculation_detail or {}
        request_data = detail.get("request_data") or {}
        title = achievement.title if achievement else request_data.get("achievement_title") or request_data.get("award") or "教学奖励认定"
        rows.append(
            {
                "module_key": "reward_recognitions",
                "module_title": "教学奖励认定审核",
                "id": recognition.id,
                "status": recognition.status,
                "teacher_name": profile.name if profile else "",
                "employee_no": profile.employee_no if profile else "",
                "department": profile.department if profile else "",
                "title": title,
                "summary": request_data.get("award") or recognition.category,
                "amount": recognition.final_amount or 0,
                "content": {
                    "category": recognition.category,
                    "level": recognition.level,
                    "rank": recognition.rank,
                    "base_amount": recognition.base_amount or 0,
                    "final_amount": recognition.final_amount or 0,
                    "policy_basis": recognition.policy_basis,
                },
                "audit_comment": recognition.audit_comment,
                "created_at": recognition.created_at.isoformat() if recognition.created_at else None,
                "audited_at": recognition.audited_at.isoformat() if recognition.audited_at else None,
                "route": "/admin/reward/recognitions",
                "detail": {
                    "achievement_id": recognition.achievement_id,
                    "profile_id": recognition.profile_id,
                    "request_data": request_data,
                    "calculation_detail": detail,
                },
            }
        )

    rows.sort(key=lambda item: item.get("created_at") or "", reverse=True)
    return success_response(data={"status": status, "total": len(rows), "list": rows})


def _string_status_counts(db: Session, model, key: str, title: str, route: str):
    base = db.query(model)
    return {
        "key": key,
        "title": title,
        "pending": base.filter(model.status == "pending").count(),
        "approved": base.filter(model.status == "approved").count(),
        "rejected": base.filter(model.status == "rejected").count(),
        "submitted": base.count(),
        "route": route,
    }


@router.get("/achievements")
async def get_achievements_for_review(
    status: Optional[str] = Query(None),
    student_name: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    admin: SysUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get achievements for review
    - Admin can view all achievements
    - Filter by status and student name
    - Pagination support
    """
    # Build query with joins
    query = db.query(BizAchievement).join(
        SysStudent, BizAchievement.student_id == SysStudent.id
    ).join(
        SysTeacher, BizAchievement.teacher_id == SysTeacher.id
    )
    
    # Apply filters
    if status:
        try:
            status_enum = AchievementStatus(status)
            query = query.filter(BizAchievement.status == status_enum)
        except ValueError:
            return error_response(msg="Invalid status value", code=400)
    
    if student_name:
        query = query.filter(SysStudent.name.like(f"%{student_name}%"))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    achievements = query.order_by(BizAchievement.created_at.desc()).offset(offset).limit(page_size).all()
    
    # Format response
    achievement_list = []
    for ach in achievements:
        achievement_list.append({
            "id": ach.id,
            "title": ach.title,
            "type": ach.type,
            "student_name": ach.student.name,
            "student_number": ach.student.student_number,
            "student_major": ach.student.major,
            "student_class": getattr(ach.student, 'class_name', None),
            "teacher_name": ach.teacher.name,
            "evidence_url": ach.evidence_url,
            "status": ach.status.value,
            "audit_comment": ach.audit_comment,
            "create_time": ach.created_at.isoformat(),
            "content_json": ach.content_json,
            "reward": calculate_teaching_reward(ach),
        })
    
    return success_response(data={
        "list": achievement_list,
        "total": total
    })


@router.patch("/achievements/{achievement_id}/audit")
async def audit_achievement(
    achievement_id: int = Path(...),
    audit_req: AchievementAudit = None,
    admin: SysUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Audit achievement
    - Approve or reject achievement
    - Comment required for rejection
    - Invalidates student persona cache on approval
    """
    # Get achievement
    achievement = db.query(BizAchievement).filter(BizAchievement.id == achievement_id).first()
    
    if not achievement:
        return error_response(msg="Achievement not found", code=404)
    
    # Validate action
    if audit_req.action not in ["approve", "reject"]:
        return error_response(msg="Invalid action. Must be 'approve' or 'reject'", code=400)
    
    # Validate comment for rejection
    if audit_req.action == "reject" and not audit_req.comment:
        return error_response(msg="Comment is required for rejection", code=400)
    
    # Update achievement status
    if audit_req.action == "approve":
        achievement.status = AchievementStatus.APPROVED
        achievement.audit_comment = audit_req.comment or "Approved"
        
        # Invalidate persona cache for student
        student = db.query(SysStudent).filter(SysStudent.id == achievement.student_id).first()
        if student:
            student.persona_cache = None  # Mark for regeneration
    else:
        achievement.status = AchievementStatus.REJECTED
        achievement.audit_comment = audit_req.comment
    
    db.commit()
    
    # --- 团队成果审批同步 ---
    # 查找所有关联的团队成员成果，同步审核状态
    synced_count = 0
    
    # 情况1：当前成果是原始成果，查找通过 source_achievement_id 指向本成果的关联记录
    related_achievements = db.query(BizAchievement).filter(
        BizAchievement.id != achievement_id,
        BizAchievement.is_deleted == False
    ).all()
    
    for related in related_achievements:
        if related.content_json and isinstance(related.content_json, dict):
            source_id = related.content_json.get("source_achievement_id")
            if source_id and source_id == achievement_id:
                related.status = achievement.status
                related.audit_comment = achievement.audit_comment
                # 同步失效学生画像缓存
                if audit_req.action == "approve":
                    related_student = db.query(SysStudent).filter(
                        SysStudent.id == related.student_id
                    ).first()
                    if related_student:
                        related_student.persona_cache = None
                synced_count += 1
    
    # 情况2：当前成果是关联成果（有 source_achievement_id），同步原始成果及其他关联
    if achievement.content_json and isinstance(achievement.content_json, dict):
        source_id = achievement.content_json.get("source_achievement_id")
        if source_id:
            # 同步原始成果
            source_achievement = db.query(BizAchievement).filter(
                BizAchievement.id == source_id
            ).first()
            if source_achievement:
                source_achievement.status = achievement.status
                source_achievement.audit_comment = achievement.audit_comment
                if audit_req.action == "approve":
                    source_student = db.query(SysStudent).filter(
                        SysStudent.id == source_achievement.student_id
                    ).first()
                    if source_student:
                        source_student.persona_cache = None
                synced_count += 1
            
            # 同步同源的其他关联成果
            for related in related_achievements:
                if related.id == achievement_id:
                    continue
                if related.content_json and isinstance(related.content_json, dict):
                    rel_source = related.content_json.get("source_achievement_id")
                    if rel_source and rel_source == source_id:
                        related.status = achievement.status
                        related.audit_comment = achievement.audit_comment
                        if audit_req.action == "approve":
                            rel_student = db.query(SysStudent).filter(
                                SysStudent.id == related.student_id
                            ).first()
                            if rel_student:
                                rel_student.persona_cache = None
                        synced_count += 1
    
    if synced_count > 0:
        db.commit()
    
    return success_response(
        msg=f"Achievement {audit_req.action}d successfully" + 
            (f", synced {synced_count} related records" if synced_count > 0 else "")
    )
