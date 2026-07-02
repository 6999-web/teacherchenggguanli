from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy import Float
from datetime import datetime
import enum
from database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    STUDENT = "student"
    ADMIN = "admin"


class AchievementStatus(str, enum.Enum):
    """Achievement status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class MessageRole(str, enum.Enum):
    """Chat message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"


class SysUser(Base):
    """System user table - login accounts"""
    __tablename__ = "sys_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    avatar_url = Column(String(500))
    is_first_login = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("SysStudent", back_populates="user", uselist=False)


class SysTeacher(Base):
    """Teacher basic data table"""
    __tablename__ = "sys_teachers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    title = Column(String(50))  # 职称
    department = Column(String(100))  # 院系
    
    # Relationships
    achievements = relationship("BizAchievement", back_populates="teacher")


class SysStudent(Base):
    """Student profile table"""
    __tablename__ = "sys_students"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("sys_users.id"), unique=True, nullable=False)
    student_number = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(50), nullable=False)
    major = Column(String(100))  # 专业
    persona_cache = Column(JSON)  # AI生成的画像数据
    
    # Relationships
    user = relationship("SysUser", back_populates="student")
    achievements = relationship("BizAchievement", back_populates="student")
    chat_sessions = relationship("AiChatSession", back_populates="student")


class BizAchievement(Base):
    """Achievement table"""
    __tablename__ = "biz_achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("sys_students.id"), nullable=False, index=True)
    teacher_id = Column(Integer, ForeignKey("sys_teachers.id"), nullable=True, index=True)
    title = Column(String(200), nullable=False)
    type = Column(String(50), nullable=False)  # 字典值
    content_json = Column(JSON)  # OCR识别后的结构化详情
    evidence_url = Column(String(500))  # 证书图片地址
    status = Column(Enum(AchievementStatus), default=AchievementStatus.PENDING, index=True)
    audit_comment = Column(Text)  # 审核意见
    is_deleted = Column(Boolean, default=False, index=True)  # 软删除标记
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    student = relationship("SysStudent", back_populates="achievements")
    teacher = relationship("SysTeacher", back_populates="achievements")


class AiChatSession(Base):
    """AI chat session table"""
    __tablename__ = "ai_chat_sessions"
    
    id = Column(String(36), primary_key=True)  # UUID
    student_id = Column(Integer, ForeignKey("sys_students.id"), nullable=False, index=True)
    title = Column(String(200))  # 会话摘要
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("SysStudent", back_populates="chat_sessions")
    messages = relationship("AiChatMessage", back_populates="session", order_by="AiChatMessage.created_at")


class AiChatMessage(Base):
    """AI chat message table"""
    __tablename__ = "ai_chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey("ai_chat_sessions.id"), nullable=False, index=True)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    session = relationship("AiChatSession", back_populates="messages")


class HrTeacherProfile(Base):
    """Teacher HR profile table."""
    __tablename__ = "hr_teacher_profiles"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("sys_students.id"), unique=True, nullable=False, index=True)
    employee_no = Column(String(50), index=True)
    name = Column(String(50), nullable=False)
    department = Column(String(100))
    education = Column(String(100))
    degree = Column(String(100))
    position = Column(String(100))
    current_title = Column(String(100))
    title_start_date = Column(DateTime)
    employment_type = Column(String(30), default="在编", index=True)
    hire_date = Column(DateTime)
    contract_start = Column(DateTime)
    contract_end = Column(DateTime)
    phone = Column(String(50))
    email = Column(String(255))
    office_location = Column(String(255))
    bio = Column(Text)
    status = Column(String(30), default="active", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class HrProfileChangeRequest(Base):
    """Pending profile changes submitted by teachers."""
    __tablename__ = "hr_profile_change_requests"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("hr_teacher_profiles.id"), nullable=False, index=True)
    before_data = Column(JSON)
    after_data = Column(JSON, nullable=False)
    status = Column(String(30), default="pending", index=True)
    audit_comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    audited_at = Column(DateTime)


class HrTeacherAttachment(Base):
    """Teacher HR archive attachment."""
    __tablename__ = "hr_teacher_attachments"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("hr_teacher_profiles.id"), nullable=False, index=True)
    attachment_type = Column(String(100), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    file_url = Column(String(500), nullable=False)
    original_filename = Column(String(255))
    status = Column(String(30), default="active", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class HrCareerEvent(Base):
    """Career events such as title, position, department, and contract changes."""
    __tablename__ = "hr_career_events"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("hr_teacher_profiles.id"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    event_date = Column(DateTime, nullable=False)
    from_value = Column(String(255))
    to_value = Column(String(255), nullable=False)
    document_url = Column(String(500))
    note = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class HrPerformanceRecord(Base):
    """Annual or appointment-period performance record."""
    __tablename__ = "hr_performance_records"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("hr_teacher_profiles.id"), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    period_type = Column(String(30), default="annual", index=True)
    teaching_score = Column(Float, default=0)
    evaluation_score = Column(Float, default=0)
    reward_bonus = Column(Float, default=0)
    admin_adjustment = Column(Float, default=0)
    final_score = Column(Float, default=0)
    grade = Column(String(30))
    status = Column(String(30), default="draft", index=True)
    note = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class HrTitleRule(Base):
    """Configurable title evaluation rule."""
    __tablename__ = "hr_title_rules"

    id = Column(Integer, primary_key=True, index=True)
    target_title = Column(String(100), nullable=False, index=True)
    employment_type = Column(String(30), default="all", index=True)
    min_approved_achievements = Column(Integer, default=0)
    required_performance_grade = Column(String(30))
    min_years_in_current_title = Column(Integer, default=0)
    required_attachment_types = Column(JSON)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class HrTitleApplication(Base):
    """Teacher title application progress."""
    __tablename__ = "hr_title_applications"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("hr_teacher_profiles.id"), nullable=False, index=True)
    target_title = Column(String(100), nullable=False, index=True)
    status = Column(String(30), default="draft", index=True)
    gap_result = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class HrFillSetting(Base):
    """Controls whether teacher-facing HR pages are open for filling."""
    __tablename__ = "hr_fill_settings"

    id = Column(Integer, primary_key=True, index=True)
    feature_key = Column(String(50), unique=True, nullable=False, index=True)
    is_open = Column(Boolean, default=False, nullable=False)
    updated_by = Column(Integer, ForeignKey("sys_users.id"), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RewardRule(Base):
    """Configurable teaching reward rule."""
    __tablename__ = "reward_rules"

    id = Column(Integer, primary_key=True, index=True)
    policy_version = Column(String(50), default="2024")
    category = Column(String(100), nullable=False, index=True)
    subcategory = Column(String(100))
    level = Column(String(50), index=True)
    rank = Column(String(50), index=True)
    amount = Column(Integer, nullable=False)
    manual_required = Column(Boolean, default=False)
    staged = Column(Boolean, default=False)
    annual_cap = Column(Integer)
    allow_duplicate = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True, index=True)


class CompetitionCatalog(Base):
    """Recognized teaching/student competition catalog."""
    __tablename__ = "competition_catalog"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    competition_type = Column(String(50), default="student")
    max_level = Column(String(50), nullable=False)
    organizer = Column(String(500))
    policy_version = Column(String(50), default="2024")
    is_active = Column(Boolean, default=True, index=True)


class RewardBatch(Base):
    """Annual reward payout batch."""
    __tablename__ = "reward_batches"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    status = Column(String(30), default="draft", index=True)
    total_amount = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime)


class RewardRecognition(Base):
    """Formal reward recognition record separated from achievement audit."""
    __tablename__ = "reward_recognitions"

    id = Column(Integer, primary_key=True, index=True)
    achievement_id = Column(Integer, ForeignKey("biz_achievements.id"), nullable=True, index=True)
    profile_id = Column(Integer, ForeignKey("hr_teacher_profiles.id"), nullable=True, index=True)
    category = Column(String(100), nullable=False, index=True)
    level = Column(String(50))
    rank = Column(String(50))
    base_amount = Column(Integer, default=0)
    final_amount = Column(Integer, default=0)
    policy_basis = Column(Text)
    calculation_detail = Column(JSON)
    status = Column(String(30), default="pending", index=True)
    audit_comment = Column(Text)
    batch_id = Column(Integer, ForeignKey("reward_batches.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    audited_at = Column(DateTime)


class RewardDistribution(Base):
    """Team reward distribution record."""
    __tablename__ = "reward_distributions"

    id = Column(Integer, primary_key=True, index=True)
    recognition_id = Column(Integer, ForeignKey("reward_recognitions.id"), nullable=False, index=True)
    member_name = Column(String(100), nullable=False)
    member_role = Column(String(100))
    ratio = Column(Float, default=0)
    amount = Column(Integer, default=0)
    confirmed = Column(Boolean, default=False)
