"""

如果你的任務是 I/O 密集型（例如：同時下載 100 張圖片、同時發送 50 個 API 請求、讀寫大量檔案）。
這時候原本的 threading 就能做到「真正」的多執行緒並發！
因為 Python 的 threading 在遇到網路等待
（Socket 阻塞）或檔案讀寫時，會主動釋放 GIL 鎖，讓其他執行緒進場。
這時候使用執行緒池是最優雅的解法：

"""

from concurrent.futures import ThreadPoolExecutor
import requests
import time

def download_site(url):
    # 遇到 requests 網路等待時，GIL 鎖會被自動釋放，換下一個執行緒下載
    response = requests.get(url)
    return f"{url}: {len(response.content)} bytes"

urls = ["https://www.google.com", "https://www.python.org", "https://www.github.com"]

# 建立一個擁有 3 個執行緒的池子
with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(download_site, urls)
    for r in results:
        print(r)