# YOLO OBB 範例

旋轉框偵測（Oriented Bounding Box）：除了位置與類別，每個物件還會有旋轉角，框會貼合物體方向，適合斜放、會旋轉的物體（空拍、輪盤格子…）。

## 執行

```bash
uv run python sample/yolo_obb/main.py
```

首次執行會自動下載 `yolo26n-obb.pt` 與示例圖 `boats.jpg`。

## 輸出（`sample/yolo_obb/out/`）

- `obb.jpg`：旋轉框 + 標籤的疊圖

## 重點

| 屬性 | 說明 |
| --- | --- |
| `result.obb.xywhr` | 中心 x, y、寬、高、旋轉角（**弧度**）`(N, 5)` |
| `result.obb.xyxyxyxy` | 四個角點（原圖像素座標）`(N, 4, 2)` |
| `result.obb.cls` / `conf` | 類別 / 信心度 |

- 是 `result.obb`，不是 `result.boxes`。
- 旋轉模型以 `-obb` 結尾（`yolo26n-obb.pt`），與 detect / segment 的權重不同。
- 標註格式：每行 `class x1 y1 x2 y2 x3 y3 x4 y4`，四個角點座標為 0~1 的比例。
- 本專案的 OBB 資料集用 `gen-obb` 生成、`train-obb` 訓練，見 `cfg/obb/roulette/`。
