import threading
import time

# 1. 準備全域變數與一把鎖
balance = 0
my_lock = threading.Lock()

def add_money1():
    global balance
    
    # 2. 手動上鎖，進來搶廁所
    my_lock.acquire()
    try:
        # 3. 安全修改資料
        current = balance
        time.sleep(0.1)  # 故意製造延遲，等大家都來排隊
        balance = current + 1
        print(f"目前餘額: {balance}")
    finally:
        # 4. 手動開鎖，出來換下一個人
        my_lock.release()

def add_money2():
    global balance
    
    # 使用 with 語法自動加鎖與解鎖
    with my_lock:
        current = balance
        time.sleep(0.1)  # 故意製造延遲
        balance = current + 1
        print(f"目前餘額: {balance}")

# 5. 同時啟動 5 個執行緒（多線程）一起跑
for _ in range(5):
    t1 = threading.Thread(target=add_money1)
    t2 = threading.Thread(target=add_money2)
    
    t1.start()
    t2.start()