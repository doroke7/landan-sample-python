"""YOLO classify 訓練範例：撲克牌正反面（Back / Flow / Front）

資料集：上一層的 datasets/
    train/<類別>/  val/<類別>/  test/<類別>/
    每個類別一個資料夾，資料夾名稱就是類別名稱，裡面是裁切後的 192x192 圖片
    classify 不需要 data.yaml 和 labels，YOLO 直接讀資料夾結構

訓練參數：上一層的 cfg/index.yaml（完整的 YOLO 訓練參數，每個欄位都有註解）

執行：
    cd sample/yolo_classify_poker_card
    uv sync                       # 第一次先安裝依賴
    uv run python src/main.py

訓練結果在上一層的 run/result/，最好的權重是 weights/best.pt
"""

import os
from pathlib import Path

import yaml
from ultralytics import YOLO

this_file = Path(__file__)
this_file = this_file.resolve()
src_dir = this_file.parent
this_dir = src_dir.parent

# cfg 裡的 data 路徑都相對於本資料夾，所以先切換到本資料夾
os.chdir(this_dir)

# 1. 讀訓練參數 cfg/index.yaml
cfg_path = this_dir / "cfg" / "index.yaml"
cfg_text = cfg_path.read_text(encoding="utf-8")
cfg = yaml.safe_load(cfg_text)
cfg_arg = str(cfg_path)

# YOLO 會把相對的 project 放到它自己的全域 runs 資料夾，這裡給絕對路徑，結果才會在本資料夾的 run/
project_dir = this_dir / cfg["project"]
project_path = str(project_dir)

# 2. 載入預訓練權重，開始訓練（其他參數都從 cfg/index.yaml 來）
model = YOLO(cfg["model"])
model.train(cfg=cfg_arg, project=project_path)

# 3. 用測試集評估訓練好的模型（imgsz、device 等沿用訓練時的設定）
metrics = model.val(data=cfg["data"], split="test", project=project_path, name="test")
print("top1 準確率:", metrics.top1)
