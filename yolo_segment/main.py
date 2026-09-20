from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

# 輸出目錄：與本檔案同層的 out/
this_file = Path(__file__)
this_dir = this_file.parent
out_dir = this_dir / "out"
out_dir.mkdir(exist_ok=True)

# 1. 加載官方預訓練「分割」模型（-seg 後綴，會自動下載）
model = YOLO("yolov8n-seg.pt")

# 2. 推理一張圖片（自動下載示例圖）
results = model("https://ultralytics.com/images/bus.jpg")
result = results[0]

# 3. 讀取分割結果
names = result.names
boxes = result.boxes
masks = result.masks

if masks is None:
    print("沒有偵測到任何物件")
else:
    class_ids = boxes.cls
    class_ids = class_ids.cpu()
    class_ids = class_ids.numpy()

    confs = boxes.conf
    confs = confs.cpu()
    confs = confs.numpy()

    # masks.xy：每個物件的輪廓多邊形（原圖像素座標，list of (N, 2) ndarray）
    polygons = masks.xy

    # masks.data：每個物件的二值遮罩 (num_objects, H, W)，尺寸為模型輸入大小
    mask_data = masks.data
    mask_data = mask_data.cpu()
    mask_data = mask_data.numpy()

    print(f"偵測到 {len(polygons)} 個物件")

    for index, polygon in enumerate(polygons):
        class_id = int(class_ids[index])
        class_name = names[class_id]
        conf = float(confs[index])

        # 遮罩面積（模型輸入尺寸下的像素數）
        area = int(np.sum(mask_data[index]))

        print(f"[{index}] {class_name} conf={conf:.2f} 輪廓點數={len(polygon)} 遮罩面積={area}")

        # 4. 單獨輸出每個物件的二值遮罩圖（0 / 255）
        mask_image = mask_data[index] * 255
        mask_image = mask_image.astype(np.uint8)
        mask_path = out_dir / f"mask_{index}_{class_name}.png"
        cv2.imwrite(str(mask_path), mask_image)

# 5. 輸出疊圖結果（框 + 遮罩 + 標籤）
plotted = result.plot()
plotted_path = out_dir / "segment.jpg"
cv2.imwrite(str(plotted_path), plotted)
print(f"已儲存：{plotted_path}")

# 6. 用小數據集訓練分割模型（僅測試流程，需要時取消註解）
# model.train(data="coco8-seg.yaml", epochs=3)

# 7. 驗證 / 導出 ONNX（需要時取消註解）
# metrics = model.val()
# print(metrics.seg)
# model.export(format="onnx")
