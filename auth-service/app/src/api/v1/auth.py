from http import HTTPStatus
from typing import Annotated

from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends, HTTPException, Query
from werkzeug.security import check_password_hash, generate_password_hash

from src.models.user import User
from src.models.user import UserLogin
from src.services.auth import AuthService, get_auth_service

router = APIRouter()


@router.post(
    '/signup',
    status_code=HTTPStatus.CREATED,
    tags=['auth'],
    description='Register new user',
    summary="Регистрация пользователя ",
)
async def register(
        login: Annotated[str, Query(alias='login')] = 'leoleoleo',
        password: Annotated[str, Query(alias='password')] = 'leoleoleo',
        email: Annotated[str, Query(alias='mail')] = 'leo@mail.ru',
        first_name: Annotated[str, Query(alias='')] = 'leoleo',
        last_name: Annotated[str, Query(alias='')] = 'leoleo',
        user_service: AuthService = Depends(get_auth_service)
) -> UserLogin:
    user_found = await user_service.get_by_login(login)
    if user_found:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Username is taken')

    user_found = await user_service.get_by_mail(email)

    if user_found:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Mail is taken')

    hashed_pwd = generate_password_hash(password)
    user = User(
        login=login,
        password=hashed_pwd,
        first_name=first_name,
        last_name=last_name,
        email=email,

    )
    await user_service.add_user(user)
    return UserLogin(login=user.login, password=user.password)


@router.post('/login', status_code=HTTPStatus.OK,
             tags=['auth'], )
async def login(
        login: Annotated[str, Query(alias='login')] = 'leoleoleo',
        password: Annotated[str, Query(alias='password')] = 'leoleoleo',
        Authorize: AuthJWT = Depends(),
        user_service: AuthService = Depends(get_auth_service)):
    hashed_pwd = generate_password_hash(password)

    password_verified = await user_service.check_password(login, hashed_pwd)

    if not password_verified:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Bad username or password")

    access_token = await Authorize.create_access_token(subject=login)
    refresh_token = await Authorize.create_refresh_token(subject=login)
    return {"access_token": access_token, "refresh_token": refresh_token}


@router.delete('/logout',
               status_code=HTTPStatus.OK,
               tags=['auth'],
               description='Logout new user',
               summary="Разлогин пользователя ", )
async def logout(login: Annotated[str, Query(alias='login')] = 'leoleoleo',
                 authorize: AuthJWT = Depends(), service: AuthService = Depends(get_auth_service)) -> dict[str, str]:
    await authorize.jwt_refresh_token_required()
    await service.revoke_both_tokens(login, authorize)
    return {'detail': 'Access and refresh token has been revoke'}
