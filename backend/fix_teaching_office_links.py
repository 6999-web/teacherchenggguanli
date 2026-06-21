from app.db.base import SessionLocal
from app.models.teaching_office import TeachingOffice
from app.models.user import User


def main() -> None:
    db = SessionLocal()
    try:
        offices = db.query(TeachingOffice).order_by(TeachingOffice.name.asc()).all()
        office_by_name = {office.name: office for office in offices}

        print(f"Found {len(offices)} teaching offices:")
        for office in offices:
            print(f"  {office.name}: {office.id}")

        users = (
            db.query(User)
            .filter(User.role == "teaching_office")
            .order_by(User.username.asc())
            .all()
        )
        print(f"\nFound {len(users)} teaching office users:")

        for user in users:
            office = office_by_name.get(user.username)
            if office is None:
                print(f"  Warning: no teaching office matched username {user.username}")
                continue

            old_id = user.teaching_office_id
            user.teaching_office_id = office.id
            print(f"  {user.username}: {old_id} -> {office.id}")

        db.commit()
        print("\nTeaching office links updated successfully.")
    except Exception as exc:
        print(f"Failed to fix teaching office links: {exc}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
