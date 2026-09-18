from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ApiModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AccountCreate(ApiModel):
    email: str = Field(min_length=3, max_length=320, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=12, max_length=128)


class LoginRequest(ApiModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=128)


class AccountRead(ApiModel):
    id: UUID
    email: str
    created_at: datetime


class AuthResponse(ApiModel):
    account: AccountRead


WorkMode = Literal["remote", "hybrid", "onsite"]


class ProfileUpdate(ApiModel):
    full_name: str | None = Field(default=None, max_length=200)
    phone: str | None = Field(default=None, max_length=40)
    current_location: str | None = Field(default=None, max_length=200)
    professional_summary: str | None = Field(default=None, max_length=4000)
    current_seniority: str | None = Field(default=None, max_length=50)
    years_experience: Decimal | None = Field(default=None, ge=0, le=80)
    countries_of_interest: list[str] = Field(default_factory=list, max_length=30)
    acceptable_timezones: list[str] = Field(default_factory=list, max_length=30)
    desired_work_modes: list[WorkMode] = Field(default_factory=list)
    work_authorizations: list[str] = Field(default_factory=list, max_length=30)
    needs_sponsorship: bool | None = None
    willing_to_relocate: bool | None = None
    salary_min: int | None = Field(default=None, ge=0, le=100_000_000)
    salary_max: int | None = Field(default=None, ge=0, le=100_000_000)
    salary_currency: str | None = Field(default=None, min_length=3, max_length=3)
    onboarding_step: int = Field(default=1, ge=1, le=4)
    onboarding_completed: bool = False

    @model_validator(mode="after")
    def validate_salary_range(self) -> "ProfileUpdate":
        if self.salary_min is not None and self.salary_max is not None:
            if self.salary_min > self.salary_max:
                raise ValueError("salary_min must not exceed salary_max")
        has_salary = self.salary_min is not None or self.salary_max is not None
        if has_salary and not self.salary_currency:
            raise ValueError("salary_currency is required when a salary range is supplied")
        return self


class ProfileRead(ProfileUpdate):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime


class WorkExperienceInput(ApiModel):
    company: str = Field(min_length=1, max_length=200)
    title: str = Field(min_length=1, max_length=200)
    start_date: date
    end_date: date | None = None
    is_current: bool = False
    responsibilities: str | None = Field(default=None, max_length=4000)
    results: str | None = Field(default=None, max_length=4000)

    @model_validator(mode="after")
    def validate_dates(self) -> "WorkExperienceInput":
        if self.is_current and self.end_date is not None:
            raise ValueError("a current experience cannot have an end date")
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("end_date must not be before start_date")
        return self


class WorkExperienceRead(WorkExperienceInput):
    id: UUID


class ProjectInput(ApiModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=4000)
    role: str | None = Field(default=None, max_length=160)
    results: str | None = Field(default=None, max_length=4000)
    url: str | None = Field(default=None, max_length=2048)


class ProjectRead(ProjectInput):
    id: UUID


class EducationInput(ApiModel):
    institution: str = Field(min_length=1, max_length=200)
    degree: str | None = Field(default=None, max_length=160)
    field_of_study: str | None = Field(default=None, max_length=160)
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> "EducationInput":
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must not be before start_date")
        return self


class EducationRead(EducationInput):
    id: UUID


class SkillInput(ApiModel):
    name: str = Field(min_length=1, max_length=100)
    category: Literal["technical", "behavioral"] = "technical"
    proficiency: str | None = Field(default=None, max_length=30)
    years_experience: Decimal | None = Field(default=None, ge=0, le=80)


class SkillRead(SkillInput):
    id: UUID


class LanguageInput(ApiModel):
    name: str = Field(min_length=1, max_length=100)
    proficiency: str = Field(min_length=1, max_length=50)


class LanguageRead(LanguageInput):
    id: UUID


class CertificationInput(ApiModel):
    name: str = Field(min_length=1, max_length=200)
    issuer: str | None = Field(default=None, max_length=200)
    issue_date: date | None = None
    credential_url: str | None = Field(default=None, max_length=2048)


class CertificationRead(CertificationInput):
    id: UUID


class ProfessionalLinkInput(ApiModel):
    label: str = Field(min_length=1, max_length=100)
    url: str = Field(min_length=1, max_length=2048)
    kind: Literal["portfolio", "publication", "profile"] = "portfolio"


class ProfessionalLinkRead(ProfessionalLinkInput):
    id: UUID


class CareerGoalInput(ApiModel):
    target_title: str = Field(min_length=1, max_length=160)
    area: str = Field(min_length=1, max_length=120)
    target_seniority: str | None = Field(default=None, max_length=50)
    priority: int = Field(default=1, ge=1, le=100)


class CareerGoalRead(CareerGoalInput):
    id: UUID


class SearchPreferenceUpdate(ApiModel):
    desired_job_count: int = Field(default=20, ge=1, le=500)
    frequency: Literal["manual", "daily", "weekly", "biweekly"] = "manual"
    max_recommendations: int = Field(default=20, ge=1, le=500)
    search_breadth: Literal["focused", "balanced", "broad"] = "balanced"
    minimum_score: Decimal = Field(default=Decimal("60"), ge=0, le=100)
    preferred_company_types: list[str] = Field(default_factory=list, max_length=30)
    preferred_company_sizes: list[str] = Field(default_factory=list, max_length=30)
    preferred_sectors: list[str] = Field(default_factory=list, max_length=30)
    preferred_companies: list[str] = Field(default_factory=list, max_length=100)
    blocked_companies: list[str] = Field(default_factory=list, max_length=100)
    culture_preferences: list[str] = Field(default_factory=list, max_length=30)
    benefit_preferences: list[str] = Field(default_factory=list, max_length=30)
    work_nature_preferences: list[str] = Field(default_factory=list, max_length=30)
    elimination_criteria: list[str] = Field(default_factory=list, max_length=30)

    @model_validator(mode="after")
    def validate_limit(self) -> "SearchPreferenceUpdate":
        if self.max_recommendations > self.desired_job_count:
            raise ValueError("max_recommendations must not exceed desired_job_count")
        return self


class SearchPreferenceRead(SearchPreferenceUpdate):
    id: UUID
    user_id: UUID


class Completeness(ApiModel):
    percentage: int
    missing: list[str]


class OnboardingRead(ApiModel):
    account: AccountRead
    profile: ProfileRead
    experiences: list[WorkExperienceRead]
    projects: list[ProjectRead]
    education: list[EducationRead]
    skills: list[SkillRead]
    languages: list[LanguageRead]
    certifications: list[CertificationRead]
    professional_links: list[ProfessionalLinkRead]
    career_goals: list[CareerGoalRead]
    search_preferences: SearchPreferenceRead
    completeness: Completeness
