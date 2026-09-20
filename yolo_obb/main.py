from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

# 輸出目錄：與本檔案同層的 out/
this_file = Path(__file__)
this_dir = this_file.parent
out_dir = this_dir / "out"
out_dir.mkdir(exist_ok=True)

# 1. 加載官方預訓練「旋轉框 (OBB)」模型（-obb 後綴，DOTA 資料集訓練，會自動下載）
model = YOLO("yolo26n-obb.pt")

# 2. 推理一張圖片（自動下載示例圖：空拍港口的船隻）
results = model("https://ultralytics.com/images/boats.jpg", conf=0.5)
result = results[0]

# 3. 讀取旋轉框結果
names = result.names
obb = result.obb

if obb is None or len(obb) == 0:
    print("沒有偵測到任何物件")
else:
    class_ids = obb.cls
    class_ids = class_ids.cpu()
    class_ids = class_ids.numpy()

    confs = obb.conf
    confs = confs.cpu()
    confs = confs.numpy()

    # obb.xywhr：中心點 x, y、寬 w、高 h、旋轉角 r（弧度）(N, 5)
    xywhr = obb.xywhr
    xywhr = xywhr.cpu()
    xywhr = xywhr.numpy()

    # obb.xyxyxyxy：四個角點（原圖像素座標）(N, 4, 2)，也就是 YOLO OBB 標註裡的 x1 y1 ... x4 y4
    corners = obb.xyxyxyxy
    corners = corners.cpu()
    corners = corners.numpy()

    total = len(obb)
    print(f"偵測到 {total} 個物件（只印前 2 個）")

    print_count = min(total, 2)
    for index in range(print_count):
        class_id = int(class_ids[index])
        class_name = names[class_id]
        conf = float(confs[index])

        cx, cy, w, h, r = xywhr[index]
        angle = float(np.degrees(r))

        print(f"[{index}] {class_name} conf={conf:.2f} 中心=({cx:.0f}, {cy:.0f}) 寬高=({w:.0f}, {h:.0f}) 角度={angle:.1f}°")

        # 四個角點依序為 (x1, y1) ... (x4, y4)
        print(f"     角點: {corners[index].round(0).tolist()}")

# 4. 輸出疊圖結果（旋轉框 + 標籤）
plotted = result.plot()
plotted_path = out_dir / "obb.jpg"
cv2.imwrite(str(plotted_path), plotted)
print(f"已儲存：{plotted_path}")

# 5. 用小數據集訓練 OBB 模型（僅測試流程，需要時取消註解）
# model.train(data="dota8.yaml", epochs=3, imgsz=640)

# 6. 驗證 / 導出 OpenVINO（需要時取消註解）
# metrics = model.val()
# print(metrics.box)
# model.export(format="openvino")
