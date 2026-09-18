from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from big_tech_jobs_api.config import get_settings
from big_tech_jobs_api.dependencies import CurrentSession, CurrentUser, DatabaseSession
from big_tech_jobs_api.models import JobSearchPreference, UserAccount, UserProfile, UserSession
from big_tech_jobs_api.schemas import AccountCreate, AccountRead, AuthResponse, LoginRequest
from big_tech_jobs_api.security import (
    create_session_token,
    hash_password,
    hash_session_token,
    normalize_email,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


def set_session_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    max_age = settings.session_ttl_days * 24 * 60 * 60
    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        max_age=max_age,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        path="/",
    )


async def issue_session(db: DatabaseSession, user: UserAccount, response: Response) -> None:
    settings = get_settings()
    token = create_session_token()
    db.add(
        UserSession(
            user_id=user.id,
            token_hash=hash_session_token(token),
            expires_at=datetime.now(UTC) + timedelta(days=settings.session_ttl_days),
        )
    )
    await db.commit()
    set_session_cookie(response, token)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: AccountCreate, response: Response, db: DatabaseSession) -> AuthResponse:
    user = UserAccount(
        email=normalize_email(payload.email),
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    try:
        await db.flush()
        db.add(UserProfile(user_id=user.id))
        db.add(JobSearchPreference(user_id=user.id))
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        ) from exc
    await db.refresh(user)
    await issue_session(db, user, response)
    return AuthResponse(account=AccountRead.model_validate(user))


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, response: Response, db: DatabaseSession) -> AuthResponse:
    user = await db.scalar(
        select(UserAccount).where(UserAccount.email == normalize_email(payload.email))
    )
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")
    await issue_session(db, user, response)
    return AuthResponse(account=AccountRead.model_validate(user))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response, db: DatabaseSession, session: CurrentSession) -> None:
    session.revoked_at = datetime.now(UTC)
    await db.commit()
    response.delete_cookie(get_settings().session_cookie_name, path="/")


@router.get("/me", response_model=AuthResponse)
async def me(user: CurrentUser) -> AuthResponse:
    return AuthResponse(account=AccountRead.model_validate(user))
