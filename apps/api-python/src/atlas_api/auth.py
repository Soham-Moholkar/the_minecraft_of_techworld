"""Authentication provider boundary.

The development bearer token keeps local onboarding deterministic while making
the authorization boundary explicit. ADR-0002 records the OIDC replacement path.
"""

import secrets
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from atlas_api.config import Settings, get_settings

bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class Principal:
    subject: str
    organization_slug: str
    roles: tuple[str, ...]


def require_principal(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Principal:
    """Validate credentials in constant time to avoid token oracle leakage."""

    if credentials is None or not secrets.compare_digest(
        credentials.credentials, settings.dev_token
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
    return Principal(subject="local-developer", organization_slug="northstar", roles=("owner",))
