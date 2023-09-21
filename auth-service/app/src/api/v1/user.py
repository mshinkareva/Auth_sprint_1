import uuid
from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from src.api.v1.schemas.user import UserResponse
from src.models.user import User
from src.services.user import UserService, users_services

router = APIRouter()


@router.get(
    '/list',
    status_code=HTTPStatus.OK,
    tags=['user'],
    description='Users',
    summary="Список пользователей",
    response_model=List[UserResponse]
)
async def get_users(
    service: UserService = Depends(users_services),
) -> list[User]:
    result = await service.get_users()
    if not result:
        return []

    return result


@router.get(
    '/',
    status_code=HTTPStatus.OK,
    tags=['user'],
    description='User',
    summary="Получить пользователя",
    response_model=UserResponse
)
async def get_user(
    user_id: uuid.UUID,
    service: UserService = Depends(users_services),
) -> User:
    result = await service.get_user_by_id(user_id)
    if not result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='user not exist')
    return result
