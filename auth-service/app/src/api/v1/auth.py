from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from src.models.data import UserSingUp, UserLogin
from src.services.auth import AuthService, get_auth_service
from src.core.config import logger

router = APIRouter()


@router.post(
    '/signup',
    status_code=HTTPStatus.OK,
    tags=['auth'],
    description='Register new user',
    summary="Регистрация пользователя ",
)
async def register(
        user_create: UserSingUp,
        user_service: AuthService = Depends(get_auth_service)
) -> UserLogin:
    logger.info(f"/signup - login: {user_create.login}")

    user_found = await user_service.get_by_login(user_create.login)
    if user_found:
        logger.info(f"/signup - login: {user_create.login}, found")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Username is taken')

    user_found = await user_service.get_by_mail(user_create.email)
    logger.info(f"/signup - emain: {user_create.email}")
    if user_found:
        logger.info(f"/signup - email: {user_create.email}, found")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Mail is taken')

    await user_service.add_user(user=user_create)
    logger.info(f"/signup - OK")
    return UserLogin(login=user_create.login, password=user_create.password)


@router.post(
    '/login',
    status_code=HTTPStatus.OK,
    tags=['auth'],
)
async def login(
        user: UserLogin,
        user_service: AuthService = Depends(get_auth_service)
) -> dict[str, str]:
    logger.info(f"/login - login: {user.login}, password: {user.password}")
    password_verified = await user_service.check_password(user.login, user.password)
    logger.info(f"/login - verified: {password_verified}")

    if not password_verified:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Bad username or password")

    token = await user_service.create_token(user=user)
    logger.info(f"/login - OK")

    return token


@router.delete('/logout',
               status_code=HTTPStatus.OK,
               tags=['auth'],
               description='Logout new user',
               summary="Разлогин пользователя ",
               )
async def logout(
        login: Annotated[str, Query(alias='login')],
        service: AuthService = Depends(get_auth_service)
) -> dict[str, str]:
    await service.revoke_both_tokens(login)
    return {'detail': 'Access and refresh token has been revoke'}
