"""
Litestar 最小範例：健康檢查、路徑參數、查詢參數、POST JSON body。

跟 sample/fastapi/main.py 是同一組 API，方便對照兩個框架的寫法差異。
最大的不同：Litestar 沒有 app.get(...) 這種裝飾器掛路由的寫法，是先寫好一般函式
（用 @get / @post 裝飾器標記），再一個一個塞進 Litestar(route_handlers=[...])。

執行
    uv run python litestar/main.py

（注意：不能用 `uv run litestar --app litestar.main:app run` 或
`uv run uvicorn litestar.main:app` 這種模組路徑字串的方式啟動——「litestar」這個
名字一定會被解析成真正裝的 litestar 套件，永遠找不到 litestar.main 這個子模組。
這裡改成直接在檔案最後呼叫 uvicorn.run(app, ...)，用 `python litestar/main.py`
直接執行整份檔案，繞開這個問題。）

打開 http://127.0.0.1:8000/schema 有自動產生的 Swagger UI，可以直接在網頁上試打每個路由。

測試
    curl http://127.0.0.1:8000/
    curl http://127.0.0.1:8000/hello/world
    curl "http://127.0.0.1:8000/items?q=poker"
    curl -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d '{"name": "die", "price": 10.5}'
"""
from dataclasses import dataclass

from litestar import Litestar, get, post

# 假裝存在資料庫裡的東西，重啟就清空
l_items: list[dict] = []


@dataclass
class Item:
    """POST /items 的 request body，Litestar 用 dataclass（也支援 pydantic model）驗證欄位型別"""
    name: str
    price: float


@get("/", sync_to_thread=False)
def health_check() -> dict:
    """健康檢查"""
    return {"status": "ok"}


@get("/hello/{name:str}", sync_to_thread=False)
def hello(name: str) -> dict:
    """路徑參數：/hello/world -> name = "world"；型別要寫在路徑樣板裡（{name:str}）"""
    return {"message": f"哈囉，{name}"}


@get("/items", sync_to_thread=False)
def list_items(q: str | None = None) -> dict:
    """查詢參數：/items?q=poker -> q = "poker"；q 是 Optional，不帶也可以"""
    if q:
        matched = [item for item in l_items if q in item["name"]]
        return {"query": q, "items": matched}
    return {"query": None, "items": l_items}


@post("/items", sync_to_thread=False)
def create_item(data: Item) -> dict:
    """POST body 是 JSON，Litestar 依 Item 這個 dataclass 自動解析、驗證"""
    new_item = {"name": data.name, "price": data.price}
    l_items.append(new_item)
    return {"created": new_item, "total": len(l_items)}


app = Litestar(route_handlers=[health_check, hello, list_items, create_item])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
