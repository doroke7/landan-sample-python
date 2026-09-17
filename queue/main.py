import queue
import threading
import time

q = queue.Queue()


def producer():
    for i in range(5):
        print(f"Produce: {i}")
        q.put(i)
        time.sleep(1)

    # 放入結束訊號
    q.put(None)


def consumer():
    while True:
        item = q.get()

        if item is None:
            q.task_done()
            break

        print(f"Consume: {item}")
        q.task_done()


t1 = threading.Thread(target=producer)
t2 = threading.Thread(target=consumer)

t1.start()
t2.start()

t1.join()

# 等待 Queue 所有工作完成
q.join()

t2.join()

print("Done")