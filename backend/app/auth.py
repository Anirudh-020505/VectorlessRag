import logging
import logging

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from itsdangerous import BadSignature, SignatureExpired, TimestampSigner
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db_session
from app.models import User
from app.schemas import UserResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()
signer = TimestampSigner(settings.SECRET_KEY)

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


def _sign_user_id(user_id: str) -> str:
    return signer.sign(user_id).decode("utf-8")


def _unsign_user_id(token: str) -> str:
    return signer.unsign(token, max_age=60 * 60 * 24 * 7).decode("utf-8")


async def _upsert_google_user(db: AsyncSession, user_info: dict) -> User:
    google_id = user_info.get("sub")
    email = user_info.get("email")
    if not google_id or not email:
        raise HTTPException(status_code=400, detail="Google profile missing required fields.")

    existing = await db.execute(select(User).where(User.google_id == google_id))
    user = existing.scalar_one_or_none()

    name = user_info.get("name") or email
    picture = user_info.get("picture")
    if user:
        user.display_name = name
        user.avatar_url = picture
    else:
        user = User(
            google_id=google_id,
            email=email,
            display_name=name,
            avatar_url=picture,
        )
        db.add(user)

    await db.commit()
    await db.refresh(user)
    return user


@router.get("/google")
async def auth_google(request: Request):
    redirect_uri = request.url_for("auth_google_callback")
    google = oauth.create_client("google")
    if google is None:
        raise HTTPException(status_code=500, detail="Google OAuth client not configured.")
    return await google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback", name="auth_google_callback")
async def auth_google_callback(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
):
    google = oauth.create_client("google")
    if google is None:
        raise HTTPException(status_code=500, detail="Google OAuth client not configured.")

    try:
        token = await google.authorize_access_token(request)
        user_info = token.get("userinfo") or await google.parse_id_token(request, token)
        user = await _upsert_google_user(db, user_info)
    except Exception as exc:
        logger.exception("OAuth callback failed: %s", exc)
        raise HTTPException(status_code=400, detail="Google OAuth callback failed.") from exc

    response = RedirectResponse(url=f"{settings.CLIENT_URL}/app", status_code=302)
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=_sign_user_id(user.id),
        httponly=True,
        secure=settings.ENVIRONMENT.lower() == "production",
        samesite="none" if settings.ENVIRONMENT.lower() == "production" else "lax",
        max_age=60 * 60 * 24 * 7,
        path="/",
    )
    return response


@router.post("/logout")
async def logout():
    response = JSONResponse({"message": "Logged out"})
    response.delete_cookie(settings.SESSION_COOKIE_NAME, path="/")
    return response


@router.get("/me", response_model=UserResponse)
async def me(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    token = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated.")

    try:
        user_id = _unsign_user_id(token)
    except (BadSignature, SignatureExpired):
        raise HTTPException(status_code=401, detail="Invalid session.")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found.")

    return UserResponse.model_validate(user)
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from itsdangerous import BadSignature, SignatureExpired, TimestampSigner
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db_session
from app.models import User
from app.schemas import UserResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()
signer = TimestampSigner(settings.SECRET_KEY)

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


def _sign_user_id(user_id: str) -> str:
    return signer.sign(user_id).decode("utf-8")


def _unsign_user_id(token: str) -> str:
    return signer.unsign(token, max_age=60 * 60 * 24 * 7).decode("utf-8")


async def _upsert_google_user(db: AsyncSession, user_info: dict) -> User:
    google_id = user_info.get("sub")
    email = user_info.get("email")
    if not google_id or not email:
        raise HTTPException(status_code=400, detail="Google profile missing required fields.")

    existing = await db.execute(select(User).where(User.google_id == google_id))
    user = existing.scalar_one_or_none()

    name = user_info.get("name") or email
    picture = user_info.get("picture")
    if user:
        user.display_name = name
        user.avatar_url = picture
    else:
        user = User(
            google_id=google_id,
            email=email,
            display_name=name,
            avatar_url=picture,
        )
        db.add(user)

    await db.commit()
    await db.refresh(user)
    return user


@router.get("/google")
async def auth_google(request: Request):
    redirect_uri = request.url_for("auth_google_callback")
    google = oauth.create_client("google")
    if google is None:
        raise HTTPException(status_code=500, detail="Google OAuth client not configured.")
    return await google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback", name="auth_google_callback")
async def auth_google_callback(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
):
    google = oauth.create_client("google")
    if google is None:
        raise HTTPException(status_code=500, detail="Google OAuth client not configured.")

    try:
        token = await google.authorize_access_token(request)
        user_info = token.get("userinfo") or await google.parse_id_token(request, token)
        user = await _upsert_google_user(db, user_info)
    except Exception as exc:
        logger.exception("OAuth callback failed: %s", exc)
        raise HTTPException(status_code=400, detail="Google OAuth callback failed.") from exc

    response = RedirectResponse(url=f"{settings.CLIENT_URL}/app", status_code=302)
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=_sign_user_id(user.id),
        httponly=True,
        secure=settings.ENVIRONMENT.lower() == "production",
        samesite="none" if settings.ENVIRONMENT.lower() == "production" else "lax",
        max_age=60 * 60 * 24 * 7,
        path="/",
    )
    return response


@router.post("/logout")
async def logout():
    response = JSONResponse({"message": "Logged out"})
    response.delete_cookie(settings.SESSION_COOKIE_NAME, path="/")
    return response


@router.get("/me", response_model=UserResponse)
async def me(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    token = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated.")

    try:
        user_id = _unsign_user_id(token)
    except (BadSignature, SignatureExpired):
        raise HTTPException(status_code=401, detail="Invalid session.")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found.")

    return UserResponse.model_validate(user)
