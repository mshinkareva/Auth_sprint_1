import uuid
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from src.models.data import PermissionCreate
from src.models.permission import Permission
from src.services.permission import PermissionService, permission_services

router = APIRouter()


@router.post(
    '/create',
    status_code=HTTPStatus.OK,
    tags=['permissions'],
    description='Create new permission',
    summary="Создать разрешение",
    response_model=Permission
)
async def create_permission(
    permission: PermissionCreate,
    service: PermissionService = Depends(permission_services),
) -> Permission:
    result = await service.create_permission(
        name=permission.name, description=permission.description
    )
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Permission is taken'
        )

    return result


@router.get(
    '/list',
    response_model=list[Permission],
    status_code=HTTPStatus.OK,
    tags=['permissions'],
    description='List Permissions',
    summary="Список разрешений",
)
async def get_permission(
    service: PermissionService = Depends(permission_services),
) -> list[Permission]:
    return await service.get_permissions()


@router.delete(
    '/delete',
    status_code=HTTPStatus.NO_CONTENT,
    tags=['permissions'],
    description='Delete Permission',
    summary="Удалить разрешение",
)
async def delete_permission(
    permission_id: Annotated[uuid.UUID, Query()],
    service: PermissionService = Depends(permission_services),
) -> None:
    result = await service.delete_permission(permission_id=permission_id)

    if not result:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Permission not exist'
        )
