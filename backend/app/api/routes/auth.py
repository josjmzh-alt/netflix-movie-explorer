import asyncio

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from app.services.drive import FRONTEND_URL, complete_auth, get_auth_url
from app.services.loader import load_data

api_router = APIRouter(tags=["Auth"])
callback_router = APIRouter(tags=["Auth"])


@api_router.get("/auth/login-url")
def get_login_url():
    """Return the Google OAuth consent URL."""
    try:
        return {"url": get_auth_url()}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to start Google OAuth: {exc}")


@callback_router.get("/auth/callback", include_in_schema=False)
async def auth_callback(code: str):
    """Exchange the OAuth code, save tokens, and trigger Drive loading."""
    try:
        complete_auth(code)
    except Exception as exc:
        return RedirectResponse(url=f"{FRONTEND_URL}?auth_error={str(exc)}")

    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, load_data)

    return RedirectResponse(url=f"{FRONTEND_URL}?auth=success")
