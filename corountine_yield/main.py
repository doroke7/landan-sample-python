import asyncio
import time

# 1. 在古老版本中，必須用裝飾器宣告這是協程
@asyncio.coroutine
def fetch_data(user_id):
    print("[{}] 開始請求資料...".format(user_id))
    
    # 2. yield from 效果等同於 await
    # 它會在這裡把控制權交還給 Event Loop，等 2 秒後再回來
    yield from asyncio.sleep(2) 
    
    print("[{}] 成功拿到資料！".format(user_id))

@asyncio.coroutine
def main():
    start_time = time.time()
    
    # 3. 舊版一樣是用 asyncio.gather 來打包並發任務
    yield from asyncio.gather(
        fetch_data("A"),
        fetch_data("B"),
        fetch_data("C")
    )
    
    print("⏳ 總共花費時間: {:.2f} 秒".format(time.time() - start_time))

# 4. 舊版沒有 asyncio.run()，必須手動獲取事件循環並執行
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
finally:
    loop.close()