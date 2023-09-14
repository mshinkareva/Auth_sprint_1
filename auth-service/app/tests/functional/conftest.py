import logging
from datetime import datetime

import pytest

LOGGER = logging.getLogger(__name__)

pytest_plugins = (
    'fixtures.connections',
    'fixtures.requests',
)


@pytest.fixture
def make_redis_exist_key(redis_client):
    def inner(key: str):
        return redis_client.get(name=key) is not None

    return inner


@pytest.fixture
def make_permission():
    stamp = int(datetime.now().timestamp())
    return {'name': f'permission_{stamp}', 'description': f'permission_{stamp}'}
