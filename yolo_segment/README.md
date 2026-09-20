# YOLO Segment 範例

實例分割（instance segmentation）：除了框與類別，每個物件還會有像素級遮罩。

## 執行

```bash
uv run python sample/yolo_segment/main.py
```

首次執行會自動下載 `yolov8n-seg.pt` 與示例圖 `bus.jpg`。

## 輸出（`sample/yolo_segment/out/`）

- `segment.jpg`：框 + 遮罩 + 標籤的疊圖
- `mask_<index>_<class>.png`：每個物件的二值遮罩（0 / 255）

## 重點

| 屬性 | 說明 |
| --- | --- |
| `result.masks.xy` | 每個物件的輪廓多邊形（原圖像素座標） |
| `result.masks.data` | 每個物件的二值遮罩 `(N, H, W)`，尺寸為模型輸入大小 |
| `result.boxes` | 與偵測相同（`cls` / `conf` / `xyxy`） |

- 分割模型以 `-seg` 結尾（`yolov8n-seg.pt`），與偵測模型 `yolov8n.pt` 不同。
- 訓練資料集標註為多邊形格式，官方測試集為 `coco8-seg.yaml`。
