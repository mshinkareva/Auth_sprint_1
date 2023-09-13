from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response

from src.api.v1.schemas.auth import LoginResponse
from src.core.config import logger
from src.models.data import UserSingUp, UserLogin
from src.services.auth import AuthService, get_auth_service

router = APIRouter()


@router.post(
    '/signup',
    status_code=HTTPStatus.OK,
    tags=['auth'],
    description='Register new user',
    summary="Регистрация нового пользователя",
)
async def register(
    user_create: UserSingUp, auth_service: AuthService = Depends(get_auth_service)
) -> HTTPStatus:
    logger.info(f"/signup - login: {user_create.login}")
    user_found = await auth_service.get_by_login(user_create.login)
    if user_found:
        logger.info(f"/signup - login: {user_create.login}, found")
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Username is taken'
        )

    user_found = await auth_service.get_by_mail(user_create.email)
    logger.info(f"/signup - email: {user_create.email}")
    if user_found:
        logger.info(f"/signup - email: {user_create.email}, found")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Mail is taken')

    try:
        await auth_service.add_user(user=user_create)
        logger.info(f"Signup successful for login: {user_create.login}")
        return HTTPStatus.CREATED
    except Exception as ex:
        logger.error(f"Signup failed due to error: {ex}")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(ex))


@router.post(
    '/login',
    status_code=HTTPStatus.OK,
    tags=['auth'],
    description='Login user',
    summary="Авторизация пользователя",
    response_model=LoginResponse,
)
async def login(
    user: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
) -> LoginResponse | Response:
    logger.info(f"/login user - login: {user.login}")
    user_found = await auth_service.get_by_login(user.login)
    if user_found:
        logger.info(f"/login user - login: {user.login}, found")
    else:
        logger.error("user not found")
        return Response(
            status_code=HTTPStatus.UNAUTHORIZED, content="Invalid login or password"
        )
    try:
        await auth_service.check_password(user=user)
        access_token = await auth_service.create_access_token(user_found.email)
        refresh_token = await auth_service.create_refresh_token(user_found.email)
        return LoginResponse(access_token=access_token, refresh_token=refresh_token)
    except ValueError as ex:
        logger.error(f"login failed due to error: {ex}")
        return Response(
            status_code=HTTPStatus.UNAUTHORIZED, content="invalid login or password"
        )


@router.post(
    '/logout',
    status_code=HTTPStatus.OK,
    tags=['auth'],
    description='Logout user',
    summary="Выход пользователя из сичтемы",
)
async def logout(
    auth_service: AuthService = Depends(get_auth_service),
) -> Response:
    logger.info("/logout user - get access and refresh tokens")
    await auth_service.auth.jwt_required()
    await auth_service.auth.jwt_refresh_token_required()
    subject = await auth_service.auth.get_jwt_subject()
    logger.info(f"/ get user - login: {subject.login}")
    user = auth_service.get_by_mail(subject)
    if user:
        logger.info(f"/Set expire tokens to redis")
        await auth_service.revoke_both_tokens(user.login)
    return Response(HTTPStatus.OK)


@router.post(
    '/refresh_token',
    status_code=HTTPStatus.OK,
    tags=['auth'],
    description='Refresh user tokens',
    summary="Обновление токенов пользователя",
    response_model=LoginResponse,
)
async def refresh_token(
    auth_service: AuthService = Depends(get_auth_service),
) -> Response | LoginResponse:
    logger.info("/refresh user - get access and refresh tokens")
    await auth_service.auth.jwt_required()
    await auth_service.auth.jwt_refresh_token_required()
    refresh_jti = (await auth_service.auth.auth.get_raw_jwt())['jti']

    jwt_subject = await auth_service.auth.get_jwt_subject()
    logger.info(f"/ get user - login: {jwt_subject.login}")
    user = auth_service.get_by_mail(jwt_subject)
    if not user:
        return Response(HTTPStatus.UNAUTHORIZED)

    logger.info(f"/Set expire tokens to redis")
    await auth_service.revoke_both_tokens(user.login)
    token_is_expired = auth_service.check_token_is_expired(user.login, refresh_jti)
    if token_is_expired:
        return Response(HTTPStatus.UNAUTHORIZED)
    new_access_token = auth_service.create_access_token(subject=jwt_subject)
    new_refresh_token = auth_service.create_access_token(subject=jwt_subject)

    return LoginResponse(
        access_token=new_access_token, refresh_token=new_refresh_token
    )
