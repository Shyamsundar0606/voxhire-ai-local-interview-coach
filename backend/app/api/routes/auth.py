from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import CurrentUser
from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    login_rate_limiter,
    verify_password,
)
from app.db.session import get_db
from app.models.candidate import Candidate
from app.models.refresh_token import RefreshToken
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse


router = APIRouter(prefix="/auth", tags=["auth"])


def _set_refresh_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=token,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.refresh_cookie_secure,
        samesite="lax",
        path="/api/v1/auth",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=get_settings().refresh_cookie_name,
        httponly=True,
        secure=get_settings().refresh_cookie_secure,
        samesite="lax",
        path="/api/v1/auth",
    )


def _create_refresh_record(
    db: Session, user: Candidate, raw_token: str, request: Request
) -> RefreshToken:
    record = RefreshToken(
        candidate_id=user.id,
        token_hash=hash_refresh_token(raw_token),
        expires_at=datetime.now(UTC)
        + timedelta(days=get_settings().refresh_token_expire_days),
        user_agent=request.headers.get("user-agent"),
    )
    db.add(record)
    db.flush()
    return record


def _token_response(user: Candidate, response: Response, raw_refresh_token: str) -> TokenResponse:
    _set_refresh_cookie(response, raw_refresh_token)
    settings = get_settings()
    return TokenResponse(
        access_token=create_access_token(user.id, settings),
        expires_in=settings.access_token_expire_minutes * 60,
        user=user,
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> TokenResponse:
    existing_user = db.scalar(select(Candidate).where(Candidate.email == payload.email))
    if existing_user is not None:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    user = Candidate(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    try:
        db.flush()
        raw_refresh_token = generate_refresh_token()
        _create_refresh_record(db, user, raw_refresh_token, request)
        db.commit()
        db.refresh(user)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists.") from exc

    return _token_response(user, response, raw_refresh_token)


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> TokenResponse:
    key = f"{request.client.host if request.client else 'unknown'}:{payload.email}"
    settings = get_settings()
    login_rate_limiter.check(key, settings.auth_rate_limit_max_attempts, settings.auth_rate_limit_window_seconds)
    user = db.scalar(select(Candidate).where(Candidate.email == payload.email))
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        login_rate_limiter.record_failure(key)
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    login_rate_limiter.clear(key)
    raw_refresh_token = generate_refresh_token()
    _create_refresh_record(db, user, raw_refresh_token, request)
    db.commit()
    return _token_response(user, response, raw_refresh_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> TokenResponse:
    raw_refresh_token = request.cookies.get(get_settings().refresh_cookie_name)
    if not raw_refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token is invalid or expired.")

    old_record = db.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(raw_refresh_token))
    )
    now = datetime.now(UTC)
    expires_at = old_record.expires_at if old_record is not None else now
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if (
        old_record is None
        or old_record.revoked_at is not None
        or expires_at <= now
    ):
        raise HTTPException(status_code=401, detail="Refresh token is invalid or expired.")

    user = db.get(Candidate, old_record.candidate_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Refresh token is invalid or expired.")

    new_raw_token = generate_refresh_token()
    new_record = _create_refresh_record(db, user, new_raw_token, request)
    old_record.revoked_at = now
    old_record.replaced_by_token_id = new_record.id
    db.commit()
    return _token_response(user, response, new_raw_token)


@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)) -> dict[str, str]:
    raw_refresh_token = request.cookies.get(get_settings().refresh_cookie_name)
    if raw_refresh_token:
        record = db.scalar(
            select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(raw_refresh_token))
        )
        if record is not None and record.revoked_at is None:
            record.revoked_at = datetime.now(UTC)
            db.commit()
    _clear_refresh_cookie(response)
    return {"status": "ok"}


@router.get("/me", response_model=UserResponse)
def me(current_user: CurrentUser) -> Candidate:
    return current_user