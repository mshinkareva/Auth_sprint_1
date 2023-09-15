from datetime import datetime

import pytest

pytest_plugins = (
    'fixtures.connections',
    'fixtures.requests',
)


@pytest.fixture
def make_permission():
    stamp = int(datetime.now().timestamp())
    return {'name': f'permission_{stamp}', 'description': f'permission_{stamp}'}
