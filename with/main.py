# with = 保證「進入時初始化，離開時清理」

# 任何物件只要實作這兩個方法，就可以用 with：
class MyCtx:
    def __enter__(self):
        print("進入")

    def __exit__(self, exc_type, exc, tb):
        print("離開")

# with 是「自動呼叫 __enter__() 和 __exit__() 的語法糖」。

# 例子1: 開啟檔案使用 
###########################################################
# 有使用with
with open("test.txt", "w") as f:
    f.write("hello")

# 不使用 with
f = open("test.txt", "w")
try:
    f.write("hello")
finally:
    f.close()



# 例子2: 線程鎖
###########################################################
# 有使用with
import threading
lock = threading.Lock()
with lock:
    print("critical section")

# 不使用 with
lock.acquire()
try:
    print("critical section")
finally:
    lock.release()


