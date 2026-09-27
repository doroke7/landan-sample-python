from litestar import Controller, get, post

from src.model.app_user import AppUser


class AppUserController(Controller):
    """AppUser 的路由邏輯都收在這個 class 裡。

    跟 sample/framework_fastapi 的版本不一樣：Litestar 原生就支援 class-based
    controller（繼承 litestar.Controller，用 path 屬性設前綴，方法上直接掛
    @get / @post），不用像 FastAPI 那樣自己用 router.add_api_route(...) 手動掛。
    """

    path = "/AppUser"

    # 假裝存在資料庫裡的東西，重啟就清空。這裡是 class 屬性不是 self.l_users = [] 這種
    # instance 屬性——實測過 Litestar 同一個 Controller 在整個 app 生命週期只會建立
    # 一次，不是每個 request 都重新 new 一個，所以掛在 class 上狀態一樣能跨 request 保留。
    l_users: list[dict] = []

    @get("/ShowOne", sync_to_thread=False)
    def show_one(self, name: str) -> dict:
        """查詢參數：/AppUser/ShowOne?name=poker -> name = "poker"，找出符合名字的使用者"""
        matched = [user for user in self.l_users if user["name"] == name]
        return {"name": name, "users": matched}

    @get("/ShowOnes", sync_to_thread=False)
    def show_ones(self, q: str | None = None) -> dict:
        """查詢參數：/AppUser/ShowOnes?q=poker -> q = "poker"；q 是 Optional，不帶也可以"""
        if q:
            matched = [user for user in self.l_users if q in user["name"]]
            return {"query": q, "users": matched}
        return {"query": None, "users": self.l_users}

    @post("/AddOne", sync_to_thread=False)
    def add_one(self, data: AppUser) -> dict:
        """POST body 是 JSON，Litestar 依 AppUser 這個 pydantic model 自動解析、驗證"""
        new_user = data.model_dump()
        self.l_users.append(new_user)
        return {"created": new_user, "total": len(self.l_users)}
