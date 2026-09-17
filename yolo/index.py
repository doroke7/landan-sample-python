from ultralytics import YOLO

# 1. 加载官方预训练模型（会自动下载）
model = YOLO("yolov8n.pt")

# 2. 推理一张图片（自动下载示例图）
results = model("https://ultralytics.com/images/bus.jpg")

# 打印检测结果

print("打印检测结果")

print(results[0].boxes)

# 3. 用小数据集训练（仅测试流程）
model.train(
    data="coco8.yaml",   # 官方小数据集，会自动下载
    epochs=3
)

# 4. 验证模型
metrics = model.val()
print("打印 metrics")

print(metrics)

# 5. 导出 ONNX（用于部署）
model.export(format="onnx")