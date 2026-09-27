from pydantic import BaseModel


class AppUser(BaseModel):
    """POST /AppUser/AddOne 的 request body，FastAPI 會自動用這個 model 驗證欄位型別"""
    name: str
    email: str
