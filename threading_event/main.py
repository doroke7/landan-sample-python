import threading
import time

o_event = threading.Event()


def thread_1(o_event: threading.Event):
    print("thread1: 開始...")
    print("thread1: 等待事件...")
    o_event.wait()  # 阻塞直到 event.set()
    print("thread1: 收到事件...")


def thread_2(o_event: threading.Event):
    print("thread2: 開始...")
    print("thread2: 發送事件...")
    o_event.set()



o_thread_1 = threading.Thread(target=thread_1, args=(o_event,))
o_thread_1.start()

time.sleep(3)

o_thread_2 = threading.Thread(target=thread_2, args=(o_event,))
o_thread_2.start()


o_thread_1.join() # join 是等待線程執行完畢 ，類似 await xxx
o_thread_2.join()
