import aiohttp
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

router = APIRouter()



AUTH_URL = "https://oauth.vk.com/authorize"
TOKEN_URL = "https://oauth.vk.com/access_token"
CLIENT_ID = "51760522"
CLIENT_SECRET = "f13gGMANmXPC9TXp9nwz"
REDIRECT_URI = "https://127.0.0.1:444/api/openapi#/"


@router.get('/login/vk', tags=['oauth'])
async def vk_login():
    auth_request_url = f"{AUTH_URL}?client_id={CLIENT_ID}&display=page&redirect_uri={REDIRECT_URI}&scope=friends,email&response_type=code&v=5.150"
    return RedirectResponse(auth_request_url)


@router.get('/login/vk/callback', tags=['oauth'])
async def vk_callback(code: str):
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(TOKEN_URL, data=data) as response:
            response_data = await response.json()

    if "error" in response_data:
        raise HTTPException(status_code=400, detail=response_data["error_description"])

    access_token = response_data["access_token"]
    expires_in = response_data["expires_in"]
    user_id = response_data["user_id"]

    return {"access_token": access_token, "expires_in": expires_in, "user_id": user_id}
