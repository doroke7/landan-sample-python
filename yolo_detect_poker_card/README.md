# YOLO Detect 範例：撲克牌（Card）

找出畫面中每張撲克牌的位置，只有 1 類（Card）。

## 安裝與執行

每個範例資料夾是獨立的 uv 專案（自己的 `pyproject.toml`、`.python-version`、`uv.lock`），在資料夾裡面安裝、執行：

```bash
cd sample/yolo_detect_poker_card
uv sync                    # 建立 .venv 並安裝依賴（第一次）
uv run python src/main.py  # 訓練
```

首次執行會自動下載 `yolo26n.pt`。

## 目錄

- `pyproject.toml`、`.python-version`、`uv.lock`：這個範例自己的 uv 專案設定（Python 3.12、ultralytics、torch）
- `cfg/index.yaml`：完整的 YOLO 訓練參數（從專案的 `cfg/detect/poker/card/index.yaml` 拷貝，路徑改成相對本資料夾），想調參數改這個檔案
- `cfg/data.yaml`：資料集描述檔（圖片路徑、類別名稱）
- `src/main.py`：訓練 + 用測試集評估
- `datasets/`：範例資料集（train/val/test 的 images + labels，YOLO 格式的 txt）
- `run/`：訓練完才會產生，`run/result/weights/best.pt` 是最好的權重，`run/test/` 是測試集評估結果
