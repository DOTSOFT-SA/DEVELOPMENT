"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError

from api.utils.settings import settings
from ..services.auth_service import AuthService
from ..utils.dependency_injection_container import get_auth_service

router = APIRouter()


@router.post("/login-token")
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        auth_service: AuthService = Depends(get_auth_service)
):
    """
    Endpoint to authenticate a user and generate an access token.

    This method accepts user credentials via the `OAuth2PasswordRequestForm`,
    validates the user credentials, and if valid, generates an access token
    that can be used for authorized API access.

    :param form_data: The credentials of the user (username and password) provided in the request body.
    :param auth_service: An instance of the `AuthService` used to authenticate the user and create the token.
    :return: A JSON response containing the access token and token type.
    :raises HTTPException: If the username or password is incorrect, an HTTP 401 Unauthorized exception is raised.
    """
    user = await auth_service.authenticate_user(
        username=form_data.username,
        user_password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = await auth_service.create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


async def verify_jwt(authorization: str = Header()):
    """
    Verifies the provided JWT token from the authorization header.

    This helper method checks the validity of the JWT token passed in the `Authorization`
    header. If the token is invalid or expired, it raises an HTTPException with a 401 status code.

    :param authorization: The Authorization header containing the JWT token prefixed by 'Bearer'.
    :return: None, raises HTTPException if the token is invalid.
    :raises HTTPException: If the JWT token is invalid or expired, a 401 Unauthorized exception is raised.
    """
    jwt_token = authorization.split(" ", 1)[1]
    try:
        jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Unauthorized token")
