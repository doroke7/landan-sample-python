from pydantic import BaseModel


class AppUser(BaseModel):
    """POST /AppUser/AddOne 的 request body，Litestar 直接支援用 pydantic model 當 DTO"""
    name: str
    email: str
