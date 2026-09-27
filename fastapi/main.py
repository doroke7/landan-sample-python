
from fastapi import FastAPI

from src.controller.resource.app_user import router as app_user_router

app = FastAPI(title="fastapi 範例")

app.include_router(app_user_router)


@app.get("/")
def health_check():
    """健康檢查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
