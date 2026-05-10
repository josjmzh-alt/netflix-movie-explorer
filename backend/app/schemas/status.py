from typing import Optional

from pydantic import BaseModel


class StatusResponse(BaseModel):
    authenticated: bool
    loaded: bool
    loading: bool
    count: int
    error: Optional[str] = None
