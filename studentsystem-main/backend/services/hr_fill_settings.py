from typing import Dict, Optional

from sqlalchemy.orm import Session

from models import HrFillSetting


FEATURE_LABELS = {
    "performance": "历年绩效",
    "title_check": "职称自查",
}


def fill_settings_to_dict(db: Session) -> Dict[str, bool]:
    settings = _ensure_settings(db)
    return {
        f"{feature}_open": settings[feature].is_open
        for feature in FEATURE_LABELS
    }


def update_fill_setting(
    db: Session,
    feature: str,
    is_open: bool,
    updated_by: Optional[int] = None,
) -> Dict[str, bool]:
    if feature not in FEATURE_LABELS:
        raise ValueError("feature 必须为 performance 或 title_check")
    settings = _ensure_settings(db)
    row = settings[feature]
    row.is_open = is_open
    row.updated_by = None
    db.commit()
    return fill_settings_to_dict(db)


def is_fill_open(db: Session, feature: str) -> bool:
    if feature not in FEATURE_LABELS:
        return False
    row = db.query(HrFillSetting).filter(HrFillSetting.feature_key == feature).first()
    return bool(row and row.is_open)


def closed_fill_message(feature: str) -> str:
    label = FEATURE_LABELS.get(feature, "当前页面")
    return f"{label}当前无法填写，请等待管理员开放填写。"


def _ensure_settings(db: Session) -> Dict[str, HrFillSetting]:
    existing = {
        row.feature_key: row
        for row in db.query(HrFillSetting)
        .filter(HrFillSetting.feature_key.in_(list(FEATURE_LABELS)))
        .all()
    }
    created = False
    for feature in FEATURE_LABELS:
        if feature not in existing:
            row = HrFillSetting(feature_key=feature, is_open=False)
            db.add(row)
            existing[feature] = row
            created = True
    if created:
        db.commit()
        for row in existing.values():
            db.refresh(row)
    return existing
