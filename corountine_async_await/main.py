import asyncio
import time

# 1. 用 async def 宣告這是一個協程函數
async def fetch_data(user_id):
    print(f"[{user_id}] 開始請求資料...")
    
    # 2. 用 await 代表：這裡要等網路回應，我先主動讓出 CPU 控制權去休息
    # 這裡必須配合非同步的 function (例如 asyncio.sleep)
    await asyncio.sleep(2) 
    
    print(f"[{user_id}] 成功拿到資料！")

async def main():
    start_time = time.time()
    
    # 3. 同時啟動 3 個協程（打包成一個任務清單並發執行）
    await asyncio.gather(
        fetch_data("A"),
        fetch_data("B"),
        fetch_data("C")
    )
    
    print(f"⏳ 總共花費時間: {time.time() - start_time:.2f} 秒")

# 4. 啟動非同步事件循環 (Event Loop) 來跑 main 協程
asyncio.run(main())