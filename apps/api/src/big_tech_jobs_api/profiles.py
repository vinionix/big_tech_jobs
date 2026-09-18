from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import delete, select

from big_tech_jobs_api.dependencies import CurrentUser, DatabaseSession
from big_tech_jobs_api.models import (
    CareerGoal,
    Certification,
    Education,
    JobSearchPreference,
    Language,
    ProfessionalLink,
    Project,
    Skill,
    UserProfile,
    WorkExperience,
)
from big_tech_jobs_api.schemas import (
    AccountRead,
    CareerGoalInput,
    CareerGoalRead,
    CertificationInput,
    CertificationRead,
    Completeness,
    EducationInput,
    EducationRead,
    LanguageInput,
    LanguageRead,
    OnboardingRead,
    ProfessionalLinkInput,
    ProfessionalLinkRead,
    ProfileRead,
    ProfileUpdate,
    ProjectInput,
    ProjectRead,
    SearchPreferenceRead,
    SearchPreferenceUpdate,
    SkillInput,
    SkillRead,
    WorkExperienceInput,
    WorkExperienceRead,
)

router = APIRouter(tags=["profile"])


def calculate_completeness(
    profile: UserProfile,
    experiences: Sequence[WorkExperience],
    skills: Sequence[Skill],
    goals: Sequence[CareerGoal],
    preferences: JobSearchPreference,
) -> Completeness:
    checks = [
        (bool(profile.full_name), 10, "nome completo"),
        (bool(profile.current_location), 10, "localização atual"),
        (bool(profile.desired_work_modes), 10, "modalidade de trabalho"),
        (bool(profile.countries_of_interest), 10, "países de interesse"),
        (bool(experiences), 15, "experiência profissional"),
        (bool(skills), 15, "competências"),
        (bool(goals), 20, "objetivo profissional"),
        (preferences.desired_job_count > 0, 10, "preferências de busca"),
    ]
    return Completeness(
        percentage=sum(weight for complete, weight, _ in checks if complete),
        missing=[label for complete, _, label in checks if not complete],
    )


async def get_profile_bundle(db: DatabaseSession, user: CurrentUser) -> OnboardingRead:
    profile = await db.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
    preferences = await db.scalar(
        select(JobSearchPreference).where(JobSearchPreference.user_id == user.id)
    )
    if profile is None or preferences is None:
        raise HTTPException(status_code=500, detail="Account profile is incomplete")
    experiences = list(
        (await db.scalars(select(WorkExperience).where(WorkExperience.user_id == user.id))).all()
    )
    projects = list((await db.scalars(select(Project).where(Project.user_id == user.id))).all())
    education = list(
        (await db.scalars(select(Education).where(Education.user_id == user.id))).all()
    )
    skills = list((await db.scalars(select(Skill).where(Skill.user_id == user.id))).all())
    languages = list((await db.scalars(select(Language).where(Language.user_id == user.id))).all())
    certifications = list(
        (await db.scalars(select(Certification).where(Certification.user_id == user.id))).all()
    )
    professional_links = list(
        (
            await db.scalars(select(ProfessionalLink).where(ProfessionalLink.user_id == user.id))
        ).all()
    )
    goals = list(
        (
            await db.scalars(
                select(CareerGoal)
                .where(CareerGoal.user_id == user.id)
                .order_by(CareerGoal.priority, CareerGoal.created_at)
            )
        ).all()
    )
    return OnboardingRead(
        account=AccountRead.model_validate(user),
        profile=ProfileRead.model_validate(profile),
        experiences=[WorkExperienceRead.model_validate(item) for item in experiences],
        projects=[ProjectRead.model_validate(item) for item in projects],
        education=[EducationRead.model_validate(item) for item in education],
        skills=[SkillRead.model_validate(item) for item in skills],
        languages=[LanguageRead.model_validate(item) for item in languages],
        certifications=[CertificationRead.model_validate(item) for item in certifications],
        professional_links=[
            ProfessionalLinkRead.model_validate(item) for item in professional_links
        ],
        career_goals=[CareerGoalRead.model_validate(item) for item in goals],
        search_preferences=SearchPreferenceRead.model_validate(preferences),
        completeness=calculate_completeness(profile, experiences, skills, goals, preferences),
    )


@router.get("/onboarding", response_model=OnboardingRead)
async def read_onboarding(db: DatabaseSession, user: CurrentUser) -> OnboardingRead:
    return await get_profile_bundle(db, user)


@router.put("/profile", response_model=OnboardingRead)
async def update_profile(
    payload: ProfileUpdate, db: DatabaseSession, user: CurrentUser
) -> OnboardingRead:
    profile = await db.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
    if profile is None:
        raise HTTPException(status_code=500, detail="Account profile is incomplete")
    for field, value in payload.model_dump().items():
        setattr(profile, field, value)
    await db.commit()
    return await get_profile_bundle(db, user)


@router.post(
    "/profile/experiences", response_model=WorkExperienceRead, status_code=status.HTTP_201_CREATED
)
async def create_experience(
    payload: WorkExperienceInput, db: DatabaseSession, user: CurrentUser
) -> WorkExperienceRead:
    item = WorkExperience(user_id=user.id, **payload.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return WorkExperienceRead.model_validate(item)


@router.delete("/profile/experiences/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_experience(
    item_id: UUID, db: DatabaseSession, user: CurrentUser, response: Response
) -> None:
    item = await db.scalar(
        select(WorkExperience).where(
            WorkExperience.id == item_id, WorkExperience.user_id == user.id
        )
    )
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    await db.delete(item)
    await db.commit()


@router.post("/profile/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectInput, db: DatabaseSession, user: CurrentUser
) -> ProjectRead:
    item = Project(user_id=user.id, **payload.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return ProjectRead.model_validate(item)


@router.delete("/profile/projects/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(item_id: UUID, db: DatabaseSession, user: CurrentUser) -> None:
    item = await db.scalar(select(Project).where(Project.id == item_id, Project.user_id == user.id))
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    await db.delete(item)
    await db.commit()


@router.post(
    "/profile/education", response_model=EducationRead, status_code=status.HTTP_201_CREATED
)
async def create_education(
    payload: EducationInput, db: DatabaseSession, user: CurrentUser
) -> EducationRead:
    item = Education(user_id=user.id, **payload.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return EducationRead.model_validate(item)


@router.delete("/profile/education/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_education(item_id: UUID, db: DatabaseSession, user: CurrentUser) -> None:
    item = await db.scalar(
        select(Education).where(Education.id == item_id, Education.user_id == user.id)
    )
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    await db.delete(item)
    await db.commit()


@router.post("/profile/skills", response_model=SkillRead, status_code=status.HTTP_201_CREATED)
async def create_skill(payload: SkillInput, db: DatabaseSession, user: CurrentUser) -> SkillRead:
    normalized_name = payload.name.strip().casefold()
    existing = await db.scalar(
        select(Skill).where(Skill.user_id == user.id, Skill.normalized_name == normalized_name)
    )
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Skill already registered")
    item = Skill(
        user_id=user.id,
        normalized_name=normalized_name,
        **payload.model_dump(),
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return SkillRead.model_validate(item)


@router.delete("/profile/skills/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    item_id: UUID, db: DatabaseSession, user: CurrentUser, response: Response
) -> None:
    item = await db.scalar(select(Skill).where(Skill.id == item_id, Skill.user_id == user.id))
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    await db.delete(item)
    await db.commit()


@router.post("/profile/languages", response_model=LanguageRead, status_code=status.HTTP_201_CREATED)
async def create_language(
    payload: LanguageInput, db: DatabaseSession, user: CurrentUser
) -> LanguageRead:
    item = Language(user_id=user.id, **payload.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return LanguageRead.model_validate(item)


@router.delete("/profile/languages/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_language(item_id: UUID, db: DatabaseSession, user: CurrentUser) -> None:
    item = await db.scalar(
        select(Language).where(Language.id == item_id, Language.user_id == user.id)
    )
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    await db.delete(item)
    await db.commit()


@router.post(
    "/profile/certifications",
    response_model=CertificationRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_certification(
    payload: CertificationInput, db: DatabaseSession, user: CurrentUser
) -> CertificationRead:
    item = Certification(user_id=user.id, **payload.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return CertificationRead.model_validate(item)


@router.delete("/profile/certifications/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_certification(item_id: UUID, db: DatabaseSession, user: CurrentUser) -> None:
    item = await db.scalar(
        select(Certification).where(Certification.id == item_id, Certification.user_id == user.id)
    )
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    await db.delete(item)
    await db.commit()


@router.post(
    "/profile/links", response_model=ProfessionalLinkRead, status_code=status.HTTP_201_CREATED
)
async def create_professional_link(
    payload: ProfessionalLinkInput, db: DatabaseSession, user: CurrentUser
) -> ProfessionalLinkRead:
    item = ProfessionalLink(user_id=user.id, **payload.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return ProfessionalLinkRead.model_validate(item)


@router.delete("/profile/links/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_professional_link(item_id: UUID, db: DatabaseSession, user: CurrentUser) -> None:
    item = await db.scalar(
        select(ProfessionalLink).where(
            ProfessionalLink.id == item_id, ProfessionalLink.user_id == user.id
        )
    )
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    await db.delete(item)
    await db.commit()


@router.put("/career-goals", response_model=list[CareerGoalRead])
async def replace_career_goals(
    payload: list[CareerGoalInput], db: DatabaseSession, user: CurrentUser
) -> list[CareerGoalRead]:
    if len(payload) > 20:
        raise HTTPException(status_code=422, detail="At most 20 career goals are allowed")
    await db.execute(delete(CareerGoal).where(CareerGoal.user_id == user.id))
    items = [CareerGoal(user_id=user.id, **goal.model_dump()) for goal in payload]
    db.add_all(items)
    await db.commit()
    for item in items:
        await db.refresh(item)
    return [CareerGoalRead.model_validate(item) for item in items]


@router.put("/search-preferences", response_model=SearchPreferenceRead)
async def update_search_preferences(
    payload: SearchPreferenceUpdate, db: DatabaseSession, user: CurrentUser
) -> SearchPreferenceRead:
    preferences = await db.scalar(
        select(JobSearchPreference).where(JobSearchPreference.user_id == user.id)
    )
    if preferences is None:
        raise HTTPException(status_code=500, detail="Account preferences are incomplete")
    for field, value in payload.model_dump().items():
        setattr(preferences, field, value)
    await db.commit()
    await db.refresh(preferences)
    return SearchPreferenceRead.model_validate(preferences)
