from pydantic import BaseModel


class CoreMessage(BaseModel):
    code: str
    ruText: str
    enText: str
    httpStatus: int


class ErrorResponse(BaseModel):
    detail: CoreMessage
