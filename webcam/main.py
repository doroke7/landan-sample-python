from datetime import datetime
from pathlib import Path

import cv2

# 圖片儲存目錄（專案根目錄下的 runtime 資料夾）
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAVE_DIR = PROJECT_ROOT / 'runtime'
SAVE_DIR.mkdir(exist_ok=True)

# 初始化攝影機，0 代表系統預設的第一支 Webcam
cap = cv2.VideoCapture(0)

# 確保攝影機有成功開啟
if not cap.isOpened():
    print("無法開啟 Webcam")
    exit()

while True:
    # 逐格讀取畫面 
    # ret 是布林值（是否成功讀取），frame 是影像的數據矩陣
    ret, frame = cap.read()

    if not ret:
        print("無法接收畫面")
        break

    # 顯示畫面，視窗名稱設定為 'Live Webcam'
    cv2.imshow('Live Webcam', frame)

    # 每一毫秒檢查一次鍵盤輸入
    key = cv2.waitKey(1) & 0xFF

    # 按下 's' 則把當前畫面存成圖片，檔名為時間戳
    if key == ord('s'):
        now = datetime.now()
        timestamp = now.strftime('%Y-%m-%d_%H-%M-%S')
        file_path = SAVE_DIR / f'{timestamp}.png'
        cv2.imwrite(str(file_path), frame)
        print(f"已儲存圖片：{file_path}")

    # 按下小寫 'q' 則中斷迴圈
    if key == ord('q'):
        break

# 結束時釋放攝影機資源並關閉所有視窗
cap.release()
cv2.destroyAllWindows()
