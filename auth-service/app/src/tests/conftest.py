import logging

import pytest

LOGGER = logging.getLogger(__name__)

pytest_plugins = (
    'fixtures.generate_data',
    'fixtures.write_data',
    'fixtures.connections',
    'fixtures.requests',
)


@pytest.fixture
def make_redis_exist_key(redis_client):
    def inner(key: str):
        return redis_client.get(name=key) is not None

    return inner
