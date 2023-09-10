from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from src.core.config import logger
from src.models.data import PermissionCreate, PermissionInDb
from src.services.permission import PermissionService, permission_services

router = APIRouter()


@router.post(
    '/create',
    status_code=HTTPStatus.OK,
    tags=['permissions'],
    description='Create new permission',
    summary="Создать разрешение",
)
async def create_permission(
        permission: PermissionCreate,
        service: PermissionService = Depends(permission_services)
) -> PermissionInDb:
    result = await service.create_permission(name=permission.name, description=permission.description)
    if not result:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Permission is taken')

    return PermissionInDb(name=permission.name, description=permission.description)


@router.get(
    '/list',
    status_code=HTTPStatus.OK,
    tags=['permissions'],
    description='List Permissions',
    summary="Список разрешений",
)
async def get_permission(
        service: PermissionService = Depends(permission_services)
) -> list[PermissionInDb]:
    result = await service.get_permissions()
    if not result:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Permission not exist')

    return [PermissionInDb(name=it.name, description=it.description) for it in result]


@router.delete(
    '/delete',
    status_code=HTTPStatus.OK,
    tags=['permissions'],
    description='Delete Permission',
    summary="Удалить разрешение",
)
async def delete_role(
        name: Annotated[str, Query(alias='name')],
        service: PermissionService = Depends(permission_services)
) -> bool:
    result = await service.delete_permission(name=name)

    if not result:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Role not exist')

    return True


