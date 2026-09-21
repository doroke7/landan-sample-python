.PHONY: venv install build run docker compose clean submodule

PY_VERSION := 3.14
PYTHON ?= python3
VENV := .venv
PIP := $(VENV)/bin/pip
PY := $(VENV)/bin/python


init:
	@rm -Rf .venv
	@uv venv .venv --python $(PY_VERSION)
	@uv venv --seed


# 為什麼用 uv 取代 【pip freeze】或 【pip install pipreqs】
## pip freeze的問題： pip freeze > requirements.txt 。   有依賴樹不准的問題， 問題是 “沒有 lock 文件”
## pip install pipreqs 的問題：pipreqs是透過“代碼分析”去 “猜測” 套件跟版本，並不是直接取得註冊的版本資訊
## uv sync 是透過 pyproject.toml (～= package.json) + uv.lock (～= package-lock.json) 來維持版本號跟依賴樹


## 以往 python 套件管理需要使用各種獨立工具，各種組合拳，使用起來太分散 。uv 解決了這個問題
# 名稱            用途                     傳統用法範例                          uv 用法範例
# --------------  ----------------------  -----------------------------------  -------------------------------
# Python版本管理   管理不同 Python 版本      pyenv install 3.12                  uv python install 3.12
# 虛擬環境         建立獨立 Python 環境      python -m venv .venv               uv venv
# 套件安裝         安裝第三方套件            pip install fastapi                uv add fastapi
# 依賴鎖定         鎖定版本依賴              pip-compile requirements.in        uv lock
# 同步依賴         安裝鎖定後所有依賴         pip-sync                           uv sync
# 執行程式         執行 Python 程式          python main.py                     uv run main.py
# 建置套件         打包 Python 套件          python -m build                    uv build

install:
	@uv sync --active                        

