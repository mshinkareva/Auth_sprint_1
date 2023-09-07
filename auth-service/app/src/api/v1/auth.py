from http import HTTPStatus

from fastapi import APIRouter, Depends

from src.core.config import logger
from src.models.data import UserSingUp, UserLogin
from src.services.auth import AuthService, get_auth_service

router = APIRouter()


@router.post(
    '/signup',
    status_code=HTTPStatus.OK,
    tags=['auth'],
    description='Register new user',
    summary="Регистрация пользователя ",
)
async def register(
    user_create: UserSingUp, user_service: AuthService = Depends(get_auth_service)
) -> UserLogin:
    logger.info(f"/signup - login: {user_create.login}")

    await user_service.add_user(user=user_create)
    logger.info(f"/signup - OK")
    return UserLogin(login=user_create.login, password=user_create.password)

