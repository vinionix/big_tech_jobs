import httpx

from big_tech_jobs_api.health import HealthReport, ServiceStatus, get_health_service
from big_tech_jobs_api.main import app


class StubHealthService:
    def __init__(self, *, ready: bool) -> None:
        self.ready = ready

    async def check(self) -> HealthReport:
        service_status = "healthy" if self.ready else "unavailable"
        return HealthReport(
            status="healthy" if self.ready else "unhealthy",
            ready=self.ready,
            checked_at="2026-09-18T00:00:00Z",
            services={
                "postgres": ServiceStatus(status=service_status, required=True),
                "redis": ServiceStatus(status="healthy", required=True),
                "ollama": ServiceStatus(status="disabled", required=False),
            },
        )


def client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    )


async def test_liveness() -> None:
    async with client() as test_client:
        response = await test_client.get("/api/v1/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


async def test_readiness_is_successful_when_required_services_are_healthy() -> None:
    app.dependency_overrides[get_health_service] = lambda: StubHealthService(ready=True)
    try:
        async with client() as test_client:
            response = await test_client.get("/api/v1/health/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["ready"] is True


async def test_readiness_fails_when_a_required_service_is_unavailable() -> None:
    app.dependency_overrides[get_health_service] = lambda: StubHealthService(ready=False)
    try:
        async with client() as test_client:
            response = await test_client.get("/api/v1/health/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json()["ready"] is False
