"""Create identity and profile tables.

Revision ID: 20260918_0001
Revises:
Create Date: 2026-09-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260918_0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def timestamps() -> list[sa.Column[object]]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "user_accounts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("password_hash", sa.String(512), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_user_accounts_email", "user_accounts", ["email"])
    op.create_table(
        "user_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["user_id"], ["user_accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index("ix_user_sessions_user_id", "user_sessions", ["user_id"])
    op.create_index("ix_user_sessions_token_hash", "user_sessions", ["token_hash"])
    op.create_index("ix_user_sessions_expires_at", "user_sessions", ["expires_at"])
    op.create_table(
        "user_profiles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("full_name", sa.String(200)),
        sa.Column("phone", sa.String(40)),
        sa.Column("current_location", sa.String(200)),
        sa.Column("professional_summary", sa.Text()),
        sa.Column("current_seniority", sa.String(50)),
        sa.Column("years_experience", sa.Numeric(4, 1)),
        sa.Column("countries_of_interest", sa.JSON(), nullable=False),
        sa.Column("acceptable_timezones", sa.JSON(), nullable=False),
        sa.Column("desired_work_modes", sa.JSON(), nullable=False),
        sa.Column("work_authorizations", sa.JSON(), nullable=False),
        sa.Column("needs_sponsorship", sa.Boolean()),
        sa.Column("willing_to_relocate", sa.Boolean()),
        sa.Column("salary_min", sa.Integer()),
        sa.Column("salary_max", sa.Integer()),
        sa.Column("salary_currency", sa.String(3)),
        sa.Column("onboarding_step", sa.Integer(), nullable=False),
        sa.Column("onboarding_completed", sa.Boolean(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["user_accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_user_profiles_user_id", "user_profiles", ["user_id"])
    op.create_table(
        "work_experiences",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("company", sa.String(200), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date()),
        sa.Column("is_current", sa.Boolean(), nullable=False),
        sa.Column("responsibilities", sa.Text()),
        sa.Column("results", sa.Text()),
        *timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["user_accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_work_experiences_user_id", "work_experiences", ["user_id"])
    op.create_table(
        "projects",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("role", sa.String(160)),
        sa.Column("results", sa.Text()),
        sa.Column("url", sa.String(2048)),
        *timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["user_accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_projects_user_id", "projects", ["user_id"])
    op.create_table(
        "education",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("institution", sa.String(200), nullable=False),
        sa.Column("degree", sa.String(160)),
        sa.Column("field_of_study", sa.String(160)),
        sa.Column("start_date", sa.Date()),
        sa.Column("end_date", sa.Date()),
        *timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["user_accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_education_user_id", "education", ["user_id"])
    op.create_table(
        "skills",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("normalized_name", sa.String(100), nullable=False),
        sa.Column("category", sa.String(30), nullable=False),
        sa.Column("proficiency", sa.String(30)),
        sa.Column("years_experience", sa.Numeric(4, 1)),
        *timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["user_accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "normalized_name", name="uq_skill_user_name"),
    )
    op.create_index("ix_skills_user_id", "skills", ["user_id"])
    op.create_table(
        "languages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("proficiency", sa.String(50), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["user_accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "name", name="uq_language_user_name"),
    )
    op.create_index("ix_languages_user_id", "languages", ["user_id"])
    op.create_table(
        "certifications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("issuer", sa.String(200)),
        sa.Column("issue_date", sa.Date()),
        sa.Column("credential_url", sa.String(2048)),
        *timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["user_accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_certifications_user_id", "certifications", ["user_id"])
    op.create_table(
        "professional_links",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("label", sa.String(100), nullable=False),
        sa.Column("url", sa.String(2048), nullable=False),
        sa.Column("kind", sa.String(30), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["user_accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_professional_links_user_id", "professional_links", ["user_id"])
    op.create_table(
        "career_goals",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("target_title", sa.String(160), nullable=False),
        sa.Column("area", sa.String(120), nullable=False),
        sa.Column("target_seniority", sa.String(50)),
        sa.Column("priority", sa.Integer(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["user_accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "target_title", "area", name="uq_goal_user_title_area"),
    )
    op.create_index("ix_career_goals_user_id", "career_goals", ["user_id"])
    op.create_table(
        "job_search_preferences",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("desired_job_count", sa.Integer(), nullable=False),
        sa.Column("frequency", sa.String(20), nullable=False),
        sa.Column("max_recommendations", sa.Integer(), nullable=False),
        sa.Column("search_breadth", sa.String(20), nullable=False),
        sa.Column("minimum_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("preferred_company_types", sa.JSON(), nullable=False),
        sa.Column("preferred_company_sizes", sa.JSON(), nullable=False),
        sa.Column("preferred_sectors", sa.JSON(), nullable=False),
        sa.Column("preferred_companies", sa.JSON(), nullable=False),
        sa.Column("blocked_companies", sa.JSON(), nullable=False),
        sa.Column("culture_preferences", sa.JSON(), nullable=False),
        sa.Column("benefit_preferences", sa.JSON(), nullable=False),
        sa.Column("work_nature_preferences", sa.JSON(), nullable=False),
        sa.Column("elimination_criteria", sa.JSON(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["user_accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_job_search_preferences_user_id", "job_search_preferences", ["user_id"])


def downgrade() -> None:
    for table in [
        "job_search_preferences",
        "career_goals",
        "skills",
        "professional_links",
        "certifications",
        "languages",
        "education",
        "projects",
        "work_experiences",
        "user_profiles",
        "user_sessions",
        "user_accounts",
    ]:
        op.drop_table(table)
