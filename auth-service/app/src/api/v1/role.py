from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from src.services.role import RoleService, role_services
from src.models.data import RoleInDb, RoleCreate, RoleUpdate, UserRole

router = APIRouter()


@router.post(
    '/create',
    status_code=HTTPStatus.OK,
    tags=['roles'],
    description='Create new Role',
    summary="Создать роль",
)
async def create_role(
        role: RoleCreate,
        service: RoleService = Depends(role_services)
) -> RoleInDb:
    result = await service.create_role(name=role.name, description=role.description)
    if not result:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Role is taken')

    return RoleInDb(name=role.name, description=role.description)


@router.get(
    '/list',
    status_code=HTTPStatus.OK,
    tags=['roles'],
    description='List Roles',
    summary="Список ролей",
)
async def get_role(
        service: RoleService = Depends(role_services)
) -> list[RoleInDb]:
    result = await service.get_roles()
    if not result:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Role not exist')

    return [RoleInDb(name=it.name, description=it.description) for it in result]


@router.delete(
    '/delete',
    status_code=HTTPStatus.NO_CONTENT,
    tags=['roles'],
    description='Delete Roles',
    summary="Удалить роль",
)
async def delete_role(
        name: Annotated[str, Query(alias='name')],
        service: RoleService = Depends(role_services)
) -> None:
    result = await service.delete_role(name=name)

    if not result:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Permission not exist')


@router.post(
    "/user_set",
    status_code=HTTPStatus.OK,
    tags=['roles'],
    description='User set Roles',
    summary="Назначить роль user",
)
async def user_set_role(
        user_role: UserRole,
        service: RoleService = Depends(role_services)
) -> bool:
    role = await service.set_user_role(login=user_role.login, name=user_role.role)

    if not role:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Role not exist')

    return True


@router.delete(
    "/user_del",
    status_code=HTTPStatus.OK,
    tags=['roles'],
    description='User delete Roles',
    summary="Удалить роль у пользователя user",
)
async def user_delete_role(
        user_role: UserRole,
        service: RoleService = Depends(role_services)
) -> bool:
    result = await service.delete_user_role(login=user_role.login, role=user_role.role)

    if not result:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='User not exist')

    return True

