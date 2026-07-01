"""Repair missing student profiles for existing student-role users."""

from database import SessionLocal, init_db
from models import SysStudent, SysUser, UserRole


DEFAULT_NAMES = {
    "admin": "测试教师",
    "2021001": "张三",
    "2021002": "李四",
}


def repair_student_profiles() -> None:
    init_db()
    db = SessionLocal()
    try:
        changed = False
        users = db.query(SysUser).filter(SysUser.role == UserRole.STUDENT).order_by(SysUser.id).all()
        for user in users:
            if user.student:
                continue

            student_number = user.username
            if db.query(SysStudent).filter(SysStudent.student_number == student_number).first():
                student_number = f"U{user.id:04d}"

            db.add(
                SysStudent(
                    user_id=user.id,
                    student_number=student_number,
                    name=DEFAULT_NAMES.get(user.username, user.username),
                    major="教师人事管理体系",
                )
            )
            changed = True

        if changed:
            db.commit()
        print("student_profiles_repaired" if changed else "student_profiles_already_ok")
    finally:
        db.close()


if __name__ == "__main__":
    repair_student_profiles()
