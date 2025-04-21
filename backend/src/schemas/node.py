from pydantic import BaseModel


class NodeInfo(BaseModel):
    ip: str
    hostname: str = ""
