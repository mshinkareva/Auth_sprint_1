import pytest

from src.models.data import UserInDb


@pytest.mark.asyncio
async def test_post_user(make_post_request, make_get_request, make_user):
    await make_post_request('/api/v1/auth/signup', make_user)
    users_raw = await make_get_request('/api/v1/user/list', {})
    users = [UserInDb(**data) for data in users_raw]
    new_user = UserInDb(**make_user)
    assert new_user in users
