import threading
import time

# 子執行緒的工作函數
def job():
  for i in range(5):
    print("Child thread:", i)
    time.sleep(1)

# 建立一個子執行緒
t = threading.Thread(target = job)

# 執行該子執行緒
t.start()

# 主執行緒繼續執行自己的工作
for i in range(3):
  print("Main thread:", i)
  time.sleep(1)

# 如果有些工作是要等待子執行緒執行完成後才能處理的話，
# 可以使用執行緒的 join 函數，等待該執行緒執行結束，
# 也就是說放在 join 之後的程式碼就會等到子執行緒執行完成後，才會接著執行。
t.join()

print("Done.")