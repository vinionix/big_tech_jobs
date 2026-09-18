import asyncio
from collections.abc import Awaitable
from datetime import UTC, datetime
from typing import Literal

import httpx
from pydantic import BaseModel
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from big_tech_jobs_api.config import Settings, get_settings
from big_tech_jobs_api.database import get_engine


class ServiceStatus(BaseModel):
    status: Literal["healthy", "unavailable", "disabled"]
    required: bool
    detail: str | None = None


class HealthReport(BaseModel):
    status: Literal["healthy", "degraded", "unhealthy"]
    ready: bool
    checked_at: datetime
    services: dict[str, ServiceStatus]


class HealthService:
    def __init__(self, settings: Settings, engine: AsyncEngine) -> None:
        self._settings = settings
        self._engine = engine

    async def _check_postgres(self) -> None:
        async with self._engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

    async def _check_redis(self) -> None:
        client = Redis.from_url(self._settings.redis_url)
        try:
            await client.ping()
        finally:
            await client.aclose()

    async def _check_ollama(self) -> None:
        if not self._settings.ollama_base_url:
            return
        async with httpx.AsyncClient(
            timeout=self._settings.ollama_timeout_seconds,
            trust_env=False,
        ) as client:
            response = await client.get(f"{self._settings.ollama_base_url.rstrip('/')}/api/tags")
            response.raise_for_status()

    async def _status(
        self,
        operation: Awaitable[None],
        *,
        required: bool,
        max_wait_seconds: float = 3.0,
    ) -> ServiceStatus:
        try:
            async with asyncio.timeout(max_wait_seconds):
                await operation
        # The public response intentionally exposes only the exception type.
        except Exception as exc:
            return ServiceStatus(
                status="unavailable",
                required=required,
                detail=type(exc).__name__,
            )
        return ServiceStatus(status="healthy", required=required)

    async def check(self) -> HealthReport:
        postgres, redis = await asyncio.gather(
            self._status(self._check_postgres(), required=True),
            self._status(self._check_redis(), required=True),
        )

        if self._settings.ollama_base_url:
            ollama = await self._status(
                self._check_ollama(),
                required=False,
                max_wait_seconds=self._settings.ollama_timeout_seconds + 0.5,
            )
        else:
            ollama = ServiceStatus(status="disabled", required=False)

        services = {"postgres": postgres, "redis": redis, "ollama": ollama}
        ready = all(item.status == "healthy" for item in services.values() if item.required)
        optional_unavailable = any(
            item.status == "unavailable" for item in services.values() if not item.required
        )
        status: Literal["healthy", "degraded", "unhealthy"]
        if not ready:
            status = "unhealthy"
        elif optional_unavailable:
            status = "degraded"
        else:
            status = "healthy"

        return HealthReport(
            status=status,
            ready=ready,
            checked_at=datetime.now(UTC),
            services=services,
        )


def get_health_service() -> HealthService:
    return HealthService(get_settings(), get_engine())
