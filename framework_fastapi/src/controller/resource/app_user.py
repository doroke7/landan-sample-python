from fastapi import APIRouter

from src.model.app_user import AppUser


class AppUserController:
    """AppUser 的路由邏輯都收在這個 class 裡。

    FastAPI 沒有像 Django/Litestar 那樣原生的 class-based view，所以是自己用
    router.add_api_route(...) 把 instance method 掛成路由，取代 @router.get(...)
    這種裝飾器寫法（裝飾器要綁在 module-level 的 router 物件上，用在 instance
    method 不方便）。
    """

    def __init__(self):
        self.router = APIRouter(prefix="/AppUser")
        # 假裝存在資料庫裡的東西，重啟就清空；放在 instance 上，是這個 controller 自己的狀態
        self.l_users: list[dict] = []

        self.router.add_api_route("/ShowOne", self.show_one, methods=["GET"])
        self.router.add_api_route("/ShowOnes", self.show_ones, methods=["GET"])
        self.router.add_api_route("/AddOne", self.add_one, methods=["POST"])

    def show_one(self, name: str):
        """查詢參數：/AppUser/ShowOne?name=poker -> name = "poker"，找出符合名字的使用者"""
        matched = [user for user in self.l_users if user["name"] == name]
        return {"name": name, "users": matched}

    def show_ones(self, q: str | None = None):
        """查詢參數：/AppUser/ShowOnes?q=poker -> q = "poker"；q 是 Optional，不帶也可以"""
        if q:
            matched = [user for user in self.l_users if q in user["name"]]
            return {"query": q, "users": matched}
        return {"query": None, "users": self.l_users}

    def add_one(self, user: AppUser):
        """POST body 是 JSON，FastAPI 依 AppUser 這個 pydantic model 自動解析、驗證"""
        new_user = user.model_dump()
        self.l_users.append(new_user)
        return {"created": new_user, "total": len(self.l_users)}


# main.py 用 from src.controller.resource.app_user import router 拿這個，
# 對外只看得到 router，不用知道背後是 class 實作的
router = AppUserController().router
