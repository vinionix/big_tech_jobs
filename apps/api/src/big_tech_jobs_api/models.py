from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from big_tech_jobs_api.database import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )


class UserAccount(TimestampMixin, Base):
    __tablename__ = "user_accounts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(512))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    profile: Mapped[UserProfile | None] = relationship(back_populates="user", cascade="all, delete")
    sessions: Mapped[list[UserSession]] = relationship(cascade="all, delete-orphan")


class UserSession(Base):
    __tablename__ = "user_sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_accounts.id", ondelete="CASCADE"), index=True
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class UserProfile(TimestampMixin, Base):
    __tablename__ = "user_profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_accounts.id", ondelete="CASCADE"), unique=True, index=True
    )
    full_name: Mapped[str | None] = mapped_column(String(200))
    phone: Mapped[str | None] = mapped_column(String(40))
    current_location: Mapped[str | None] = mapped_column(String(200))
    professional_summary: Mapped[str | None] = mapped_column(Text)
    current_seniority: Mapped[str | None] = mapped_column(String(50))
    years_experience: Mapped[Decimal | None] = mapped_column(Numeric(4, 1))
    countries_of_interest: Mapped[list[str]] = mapped_column(JSON, default=list)
    acceptable_timezones: Mapped[list[str]] = mapped_column(JSON, default=list)
    desired_work_modes: Mapped[list[str]] = mapped_column(JSON, default=list)
    work_authorizations: Mapped[list[str]] = mapped_column(JSON, default=list)
    needs_sponsorship: Mapped[bool | None] = mapped_column(Boolean)
    willing_to_relocate: Mapped[bool | None] = mapped_column(Boolean)
    salary_min: Mapped[int | None] = mapped_column(Integer)
    salary_max: Mapped[int | None] = mapped_column(Integer)
    salary_currency: Mapped[str | None] = mapped_column(String(3))
    onboarding_step: Mapped[int] = mapped_column(Integer, default=1)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped[UserAccount] = relationship(back_populates="profile")


class WorkExperience(TimestampMixin, Base):
    __tablename__ = "work_experiences"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_accounts.id", ondelete="CASCADE"), index=True
    )
    company: Mapped[str] = mapped_column(String(200))
    title: Mapped[str] = mapped_column(String(200))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)
    responsibilities: Mapped[str | None] = mapped_column(Text)
    results: Mapped[str | None] = mapped_column(Text)


class Project(TimestampMixin, Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_accounts.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    role: Mapped[str | None] = mapped_column(String(160))
    results: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str | None] = mapped_column(String(2048))


class Education(TimestampMixin, Base):
    __tablename__ = "education"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_accounts.id", ondelete="CASCADE"), index=True
    )
    institution: Mapped[str] = mapped_column(String(200))
    degree: Mapped[str | None] = mapped_column(String(160))
    field_of_study: Mapped[str | None] = mapped_column(String(160))
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)


class Skill(TimestampMixin, Base):
    __tablename__ = "skills"
    __table_args__ = (UniqueConstraint("user_id", "normalized_name", name="uq_skill_user_name"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_accounts.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(100))
    normalized_name: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(30), default="technical")
    proficiency: Mapped[str | None] = mapped_column(String(30))
    years_experience: Mapped[Decimal | None] = mapped_column(Numeric(4, 1))


class Language(TimestampMixin, Base):
    __tablename__ = "languages"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_language_user_name"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_accounts.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(100))
    proficiency: Mapped[str] = mapped_column(String(50))


class Certification(TimestampMixin, Base):
    __tablename__ = "certifications"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_accounts.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(200))
    issuer: Mapped[str | None] = mapped_column(String(200))
    issue_date: Mapped[date | None] = mapped_column(Date)
    credential_url: Mapped[str | None] = mapped_column(String(2048))


class ProfessionalLink(TimestampMixin, Base):
    __tablename__ = "professional_links"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_accounts.id", ondelete="CASCADE"), index=True
    )
    label: Mapped[str] = mapped_column(String(100))
    url: Mapped[str] = mapped_column(String(2048))
    kind: Mapped[str] = mapped_column(String(30), default="portfolio")


class CareerGoal(TimestampMixin, Base):
    __tablename__ = "career_goals"
    __table_args__ = (
        UniqueConstraint("user_id", "target_title", "area", name="uq_goal_user_title_area"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_accounts.id", ondelete="CASCADE"), index=True
    )
    target_title: Mapped[str] = mapped_column(String(160))
    area: Mapped[str] = mapped_column(String(120))
    target_seniority: Mapped[str | None] = mapped_column(String(50))
    priority: Mapped[int] = mapped_column(Integer, default=1)


class JobSearchPreference(TimestampMixin, Base):
    __tablename__ = "job_search_preferences"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_accounts.id", ondelete="CASCADE"), unique=True, index=True
    )
    desired_job_count: Mapped[int] = mapped_column(Integer, default=20)
    frequency: Mapped[str] = mapped_column(String(20), default="manual")
    max_recommendations: Mapped[int] = mapped_column(Integer, default=20)
    search_breadth: Mapped[str] = mapped_column(String(20), default="balanced")
    minimum_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("60.00"))
    preferred_company_types: Mapped[list[str]] = mapped_column(JSON, default=list)
    preferred_company_sizes: Mapped[list[str]] = mapped_column(JSON, default=list)
    preferred_sectors: Mapped[list[str]] = mapped_column(JSON, default=list)
    preferred_companies: Mapped[list[str]] = mapped_column(JSON, default=list)
    blocked_companies: Mapped[list[str]] = mapped_column(JSON, default=list)
    culture_preferences: Mapped[list[str]] = mapped_column(JSON, default=list)
    benefit_preferences: Mapped[list[str]] = mapped_column(JSON, default=list)
    work_nature_preferences: Mapped[list[str]] = mapped_column(JSON, default=list)
    elimination_criteria: Mapped[list[str]] = mapped_column(JSON, default=list)
