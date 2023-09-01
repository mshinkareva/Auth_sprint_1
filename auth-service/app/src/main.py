import logging

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.responses import ORJSONResponse
from async_fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from redis.asyncio import Redis
from sqlmodel import create_engine
from sqlmodel.ext.asyncio.session import AsyncEngine

from src.api.v1 import auth
from src.core.logger import LOGGING
from src.db import redis, postgres
from src.ratelimiter import RateLimiter
from src.settings import settings

app = FastAPI(
    title=settings.project_name,
    version='1.0.0',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)


class Settings(BaseModel):
    authjwt_secret_key: str = "secret"
    authjwt_denylist_enabled: bool = True
    authjwt_denylist_token_checks: set = {"access", "refresh"}


@AuthJWT.load_config
def get_config():
    return Settings()


@AuthJWT.token_in_denylist_loader
async def check_if_token_in_denylist(decrypted_token):
    jti = decrypted_token['jti']
    entry = await redis.redis.get(jti)
    return entry and entry == 'true'


@app.on_event('startup')
async def startup():
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)

    postgres.engine = AsyncEngine(
        create_engine(settings.pg_url(), echo=True, future=True)
    )


@app.on_event('shutdown')
async def shutdown():
    await redis.redis.close()


app.include_router(auth.router, prefix='/api/v1/auth')

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
