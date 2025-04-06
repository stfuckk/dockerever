from pydantic import BaseModel
from typing import Optional, Any


class CoreMessage(BaseModel):
    code: str
    ruText: str
    enText: str
    httpStatus: int
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    detail: CoreMessage
