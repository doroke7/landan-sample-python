from datetime import datetime
from pathlib import Path

import cv2

# 圖片儲存目錄（專案根目錄下的 runtime 資料夾）
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAVE_DIR = PROJECT_ROOT / 'runtime'
SAVE_DIR.mkdir(exist_ok=True)

# 最多探測前幾個裝置索引
MAX_DEVICES = 10


def list_devices():
    """逐一嘗試開啟索引 0 ~ MAX_DEVICES-1，回傳可用的 (索引, 寬, 高) 清單。
    OpenCV 沒有列舉裝置的 API，只能靠嘗試開啟來判斷。"""
    devices = []
    for index in range(MAX_DEVICES):
        probe = cv2.VideoCapture(index)
        if probe.isOpened():
            width = int(probe.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(probe.get(cv2.CAP_PROP_FRAME_HEIGHT))
            devices.append((index, width, height))
        probe.release()
    return devices


def choose_device(devices):
    """列出可用裝置並讓使用者輸入要使用的索引。只有一個裝置時直接使用。"""
    if len(devices) == 1:
        return devices[0][0]

    print("偵測到以下裝置：")
    for index, width, height in devices:
        print(f"  [{index}] {width}x{height}")

    valid_indexes = [index for index, _, _ in devices]
    while True:
        answer = input("請輸入要使用的裝置索引：").strip()
        if answer.isdigit() and int(answer) in valid_indexes:
            return int(answer)
        print("輸入無效，請重新輸入")


devices = list_devices()
if not devices:
    print("找不到任何 Webcam")
    exit()

device_index = choose_device(devices)

# 初始化選定的攝影機
cap = cv2.VideoCapture(device_index)

# 確保攝影機有成功開啟
if not cap.isOpened():
    print(f"無法開啟 Webcam（索引 {device_index}）")
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
