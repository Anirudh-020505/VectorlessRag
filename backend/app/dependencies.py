from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, Request
from itsdangerous import BadSignature, SignatureExpired, TimestampSigner
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db_session
from app.models import User

settings = get_settings()
signer = TimestampSigner(settings.SECRET_KEY)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db_session():
        yield session


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    # Attempt to load an authenticated user if a cookie exists
    token = request.cookies.get(settings.SESSION_COOKIE_NAME)
    user = None
    
    if token:
        try:
            user_id = signer.unsign(token, max_age=60 * 60 * 24 * 7).decode("utf-8")
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
        except (Exception):
            # Ignore signature errors, rely on fallback
            pass

    # If no authenticated user is found, lazily auto-create and return a global anonymous user
    if not user:
        result = await db.execute(select(User).where(User.email == "anonymous@local.dev"))
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(
                google_id="anonymous",
                email="anonymous@local.dev",
                display_name="Global Test User",
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
    return user
