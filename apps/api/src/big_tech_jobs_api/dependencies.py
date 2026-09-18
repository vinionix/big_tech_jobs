from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from big_tech_jobs_api.config import get_settings
from big_tech_jobs_api.database import get_db_session
from big_tech_jobs_api.models import UserAccount, UserSession
from big_tech_jobs_api.security import hash_session_token

DatabaseSession = Annotated[AsyncSession, Depends(get_db_session)]


async def get_current_session(
    db: DatabaseSession,
    request: Request,
) -> UserSession:
    settings = get_settings()
    session_token = request.cookies.get(settings.session_cookie_name)
    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    query = select(UserSession).where(
        UserSession.token_hash == hash_session_token(session_token),
        UserSession.revoked_at.is_(None),
        UserSession.expires_at > datetime.now(UTC),
    )
    session = await db.scalar(query)
    if session is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    session.last_seen_at = datetime.now(UTC)
    return session


CurrentSession = Annotated[UserSession, Depends(get_current_session)]


async def get_current_user(db: DatabaseSession, session: CurrentSession) -> UserAccount:
    user = await db.get(UserAccount, session.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid account")
    return user


CurrentUser = Annotated[UserAccount, Depends(get_current_user)]
