from datetime import datetime

import pytest

pytest_plugins = (
    'fixtures.connections',
    'fixtures.requests',
)


@pytest.fixture
def timestamp():
    return int(datetime.now().timestamp())


@pytest.fixture
def make_permission(timestamp):
    return {'name': f'permission_{timestamp}', 'description': f'permission_{timestamp}'}


@pytest.fixture
def make_role(timestamp):
    return {'name': f'role_{timestamp}', 'description': f'role_{timestamp}'}
