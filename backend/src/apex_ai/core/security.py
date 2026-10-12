from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from apex_ai.core.config import settings
from apex_ai.database.models import User
from apex_ai.database.session import get_db


bearer_scheme = HTTPBearer(auto_error=False)

VALID_PERMISSIONS = {
    "read",
    "write",
    "delete",
    "export",
    "research",
}


@dataclass(frozen=True)
class CurrentUser:
    id: int
    email: str | None
    permissions: frozenset[str]


def _get_jwt_secret() -> str:
    secret = settings.jwt_secret_key

    if len(secret) < 32:
        raise RuntimeError(
            "JWT_SECRET_KEY must contain at least 32 characters."
        )

    return secret


def create_access_token(
    user_id: int,
    permissions: set[str] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    if user_id <= 0:
        raise ValueError("user_id must be a positive integer")

    granted_permissions = permissions or set()

    if not granted_permissions.issubset(VALID_PERMISSIONS):
        raise ValueError("One or more permissions are invalid")

    expires_at = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(minutes=settings.access_token_expire_minutes)
    )

    payload = {
        "sub": str(user_id),
        "permissions": sorted(granted_permissions),
        "token_type": "access",
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        _get_jwt_secret(),
        algorithm=settings.jwt_algorithm,
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: AsyncSession = Depends(get_db),
) -> CurrentUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            _get_jwt_secret(),
            algorithms=[settings.jwt_algorithm],
            options={
                "require": ["sub", "exp", "token_type"],
            },
        )

        if payload.get("token_type") != "access":
            raise InvalidTokenError("Invalid token type")

        user_id = int(payload["sub"])
        if user_id <= 0:
            raise InvalidTokenError("Invalid user ID")

        permissions = payload.get("permissions", [])
        if (
            not isinstance(permissions, list)
            or not all(
                isinstance(permission, str)
                for permission in permissions
            )
            or not set(permissions).issubset(VALID_PERMISSIONS)
        ):
            raise InvalidTokenError("Invalid permissions")

    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is not configured",
        ) from exc

    except (InvalidTokenError, ValueError, TypeError, KeyError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = await db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return CurrentUser(
        id=user.id,
        email=user.email,
        permissions=frozenset(permissions),
    )


def require_permissions(
    *required_permissions: str,
) -> Callable:
    required = set(required_permissions)

    if not required.issubset(VALID_PERMISSIONS):
        raise ValueError("Unknown permission requested")

    async def permission_dependency(
        current_user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        if not required.issubset(current_user.permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )

        return current_user

    return permission_dependency