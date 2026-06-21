import uuid

from sqlalchemy import text

from app.core.security import get_password_hash
from app.db.base import SessionLocal, engine
from app.models.teaching_office import TeachingOffice
from app.models.user import User

DEFAULT_PASSWORD = "password123"

TEACHING_OFFICE_ACCOUNTS = [
    {"username": "禁毒学教研室", "code": "TO001", "email": "office1@local.test"},
    {"username": "人工智能教研室", "code": "TO002", "email": "office2@local.test"},
    {"username": "公共体育教研室", "code": "TO003", "email": "office3@local.test"},
    {"username": "网络攻防教研室", "code": "TO004", "email": "office4@local.test"},
    {"username": "治安学教研室", "code": "TO005", "email": "office5@local.test"},
    {"username": "英语教研室", "code": "TO006", "email": "office6@local.test"},
]

MANAGEMENT_ACCOUNTS = [
    {
        "username": "考评小组张老师",
        "role": "evaluation_team",
        "email": "evaluation-team-zhang@local.test",
    },
    {
        "username": "考评小组李老师",
        "role": "evaluation_team",
        "email": "evaluation-team-li@local.test",
    },
    {
        "username": "考评办公室",
        "role": "evaluation_office",
        "email": "evaluation-office@local.test",
    },
    {
        "username": "教务处",
        "role": "president_office",
        "email": "academic-affairs-office@local.test",
    },
]


def main() -> None:
    db = SessionLocal()
    try:
        if engine.dialect.name == "mysql":
            db.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
            db.execute(text("TRUNCATE TABLE users;"))
            db.execute(text("TRUNCATE TABLE teaching_offices;"))
            db.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        else:
            db.execute(text("DELETE FROM users;"))
            db.execute(text("DELETE FROM teaching_offices;"))

        password_hash = get_password_hash(DEFAULT_PASSWORD)

        offices = []
        for spec in TEACHING_OFFICE_ACCOUNTS:
            office = TeachingOffice(
                id=uuid.uuid4(),
                name=spec["username"],
                code=spec["code"],
                department=spec["username"],
            )
            offices.append(office)
            db.add(office)

        db.commit()

        users = []
        for spec, office in zip(TEACHING_OFFICE_ACCOUNTS, offices):
            users.append(
                User(
                    username=spec["username"],
                    password_hash=password_hash,
                    role="teaching_office",
                    name=spec["username"],
                    teaching_office_id=office.id,
                    email=spec["email"],
                )
            )

        for spec in MANAGEMENT_ACCOUNTS:
            users.append(
                User(
                    username=spec["username"],
                    password_hash=password_hash,
                    role=spec["role"],
                    name=spec["username"],
                    email=spec["email"],
                )
            )

        for user in users:
            db.add(user)

        db.commit()
        print(f"Local accounts reset successfully. Default password: {DEFAULT_PASSWORD}")
        for user in users:
            print(f"{user.username} ({user.role})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
