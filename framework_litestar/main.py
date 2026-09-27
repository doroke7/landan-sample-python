from litestar import Litestar, get

from src.controller.resource.app_user import AppUserController


@get("/", sync_to_thread=False)
def health_check() -> dict:
    """健康檢查"""
    return {"status": "ok"}


app = Litestar(route_handlers=[health_check, AppUserController])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
