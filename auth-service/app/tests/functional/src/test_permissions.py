import pytest

from src.models.permission import Permission

PAGE_SIZE = 50


@pytest.mark.asyncio
async def test_post_permissions(make_post_request, make_get_request, make_permission):
    await make_post_request('/api/v1/permission/create', make_permission)
    permissions_raw = await make_get_request('/api/v1/permission/list', {})
    permissions = [Permission(**data) for data in permissions_raw]
    new_permission = Permission(**make_permission)
    assert new_permission in permissions

