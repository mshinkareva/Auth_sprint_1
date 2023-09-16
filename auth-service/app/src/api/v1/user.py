from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from src.core.config import logger
from src.models.user import User
from src.models.data import UserInDb
from src.services.user import UserService, users_services

router = APIRouter()



@router.get(
    '/list',
    status_code=HTTPStatus.OK,
    tags=['user'],
    description='Users',
    summary="Список пользователей",
)
async def get_users(
    service: UserService = Depends(users_services),
) -> list[UserInDb]:
    result = await service.get_users()
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='user not exist'
        )

    return [UserInDb(login=user.login, email=user.email) for user in result]

@router.get(
    '/',
    status_code=HTTPStatus.OK,
    tags=['user'],
    description='User',
    summary="Получить пользователя",
)
async def get_user(
    user: str, service: UserService = Depends(users_services),
) -> UserInDb:
    result = await service.get_user(login=user)
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='user not exist'
        )
    return result

