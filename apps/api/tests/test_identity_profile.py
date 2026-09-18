from collections.abc import AsyncIterator

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from big_tech_jobs_api.database import Base, get_db_session
from big_tech_jobs_api.main import app


@pytest.fixture
async def session_factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_db() -> AsyncIterator[AsyncSession]:
        async with factory() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_db
    try:
        yield factory
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()


def client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    )


async def register(test_client: httpx.AsyncClient, email: str) -> httpx.Response:
    return await test_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "a-secure-password"},
    )


async def test_register_session_logout_and_duplicate_email(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with client() as test_client:
        response = await register(test_client, "Person@Example.com")
        assert response.status_code == 201
        assert response.json()["account"]["email"] == "person@example.com"
        assert "HttpOnly" in response.headers["set-cookie"]
        assert "SameSite=lax" in response.headers["set-cookie"]

        me = await test_client.get("/api/v1/auth/me")
        assert me.status_code == 200

        logout = await test_client.post("/api/v1/auth/logout")
        assert logout.status_code == 204
        assert (await test_client.get("/api/v1/auth/me")).status_code == 401

        duplicate = await register(test_client, "person@example.com")
        assert duplicate.status_code == 409


async def test_onboarding_is_resumable_and_reports_completeness(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with client() as test_client:
        assert (await register(test_client, "profile@example.com")).status_code == 201

        initial = await test_client.get("/api/v1/onboarding")
        assert initial.json()["completeness"]["percentage"] == 10

        updated = await test_client.put(
            "/api/v1/profile",
            json={
                "full_name": "Ada Lovelace",
                "current_location": "Rio de Janeiro, BR",
                "professional_summary": "Engenheira de software",
                "countries_of_interest": ["Brasil"],
                "desired_work_modes": ["remote", "hybrid"],
                "onboarding_step": 2,
            },
        )
        assert updated.status_code == 200
        assert updated.json()["profile"]["onboarding_step"] == 2
        assert updated.json()["completeness"]["percentage"] == 50

        resumed = await test_client.get("/api/v1/onboarding")
        assert resumed.json()["profile"]["full_name"] == "Ada Lovelace"
        assert resumed.json()["profile"]["onboarding_step"] == 2


async def test_profile_resources_are_isolated_between_users(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with client() as first, client() as second:
        await register(first, "first@example.com")
        created = await first.post(
            "/api/v1/profile/skills",
            json={"name": "Python", "category": "technical", "proficiency": "advanced"},
        )
        assert created.status_code == 201
        skill_id = created.json()["id"]

        await register(second, "second@example.com")
        second_profile = await second.get("/api/v1/onboarding")
        assert second_profile.json()["skills"] == []

        cross_user_delete = await second.delete(f"/api/v1/profile/skills/{skill_id}")
        assert cross_user_delete.status_code == 404

        first_profile = await first.get("/api/v1/onboarding")
        assert [skill["name"] for skill in first_profile.json()["skills"]] == ["Python"]


async def test_search_quantity_is_user_configurable(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with client() as test_client:
        await register(test_client, "preferences@example.com")
        response = await test_client.put(
            "/api/v1/search-preferences",
            json={
                "desired_job_count": 73,
                "max_recommendations": 31,
                "frequency": "weekly",
                "search_breadth": "broad",
                "minimum_score": 42,
            },
        )
        assert response.status_code == 200
        assert response.json()["desired_job_count"] == 73
        assert response.json()["max_recommendations"] == 31


async def test_extended_profile_collections_are_persisted(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with client() as test_client:
        await register(test_client, "trajectory@example.com")
        requests = [
            ("/api/v1/profile/projects", {"title": "Sistema distribuído", "role": "Backend"}),
            ("/api/v1/profile/education", {"institution": "42 Rio", "degree": "Software"}),
            ("/api/v1/profile/languages", {"name": "Inglês", "proficiency": "avançado"}),
            ("/api/v1/profile/certifications", {"name": "CCNA", "issuer": "Cisco"}),
            (
                "/api/v1/profile/links",
                {"label": "GitHub", "url": "https://github.com/example", "kind": "portfolio"},
            ),
        ]
        for path, payload in requests:
            assert (await test_client.post(path, json=payload)).status_code == 201

        onboarding = (await test_client.get("/api/v1/onboarding")).json()
        assert onboarding["projects"][0]["title"] == "Sistema distribuído"
        assert onboarding["education"][0]["institution"] == "42 Rio"
        assert onboarding["languages"][0]["name"] == "Inglês"
        assert onboarding["certifications"][0]["name"] == "CCNA"
        assert onboarding["professional_links"][0]["label"] == "GitHub"
