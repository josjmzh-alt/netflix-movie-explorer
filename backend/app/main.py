import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router, auth_router
from app.services.drive import is_authenticated
from app.services.loader import load_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    if is_authenticated():
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, load_data)
    yield


app = FastAPI(
    title="Netflix Movie Library Explorer",
    description="Internal tool for browsing and querying movie metadata from Google Drive",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(auth_router)
