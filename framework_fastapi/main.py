
from fastapi import FastAPI


app = FastAPI(title="fastapi 範例")


@app.get("/")
def health_check():
    """健康檢查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
