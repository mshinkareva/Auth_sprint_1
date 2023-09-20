import json
from http import HTTPStatus
from time import sleep

import pytest_asyncio


@pytest_asyncio.fixture
def make_get_request(client):
    sleep(2)

    async def inner(api_url: str, query_data: dict):
        response = await client.get(url=api_url, params=query_data)
        if response.status_code != HTTPStatus.OK:
            raise Exception(
                f'Ошибка EndPoint FastApi {response.status_code} api_url={api_url} query_data {query_data}'
            )
        return json.loads(response.content)

    return inner


@pytest_asyncio.fixture
def make_post_request(client):

    async def inner(api_url: str, query_data: dict):
        response = await client.post(url=api_url, json=query_data)
        if response.status_code != HTTPStatus.OK:
            raise Exception(
                f'Ошибка EndPoint FastApi {response.status_code} api_url={api_url} query_data {query_data}'
            )
        return json.loads(response.content)

    return inner
