from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware

from big_tech_jobs_api.config import get_settings
from big_tech_jobs_api.database import get_engine
from big_tech_jobs_api.health import HealthReport, HealthService, get_health_service


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield
    await get_engine().dispose()


app = FastAPI(
    title="Big Tech Jobs API",
    version="0.1.0",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["Content-Type", "X-Correlation-ID"],
)

router = APIRouter(prefix="/api/v1")
HealthServiceDependency = Annotated[HealthService, Depends(get_health_service)]


@router.get("/health/live")
async def liveness() -> dict[str, str]:
    return {"status": "alive"}


@router.get("/health", response_model=HealthReport)
async def health(
    health_service: HealthServiceDependency,
) -> HealthReport:
    return await health_service.check()


@router.get("/health/ready", response_model=HealthReport)
async def readiness(
    response: Response,
    health_service: HealthServiceDependency,
) -> HealthReport:
    report = await health_service.check()
    if not report.ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return report


app.include_router(router)
