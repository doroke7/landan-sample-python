"""
一次送出 10 個任務 (每個都是 1 + 2 + ... + 1 億)，但 worker 同時只能跑 4 個。

做法
    ProcessPoolExecutor(max_workers=4)
        - 10 個任務全部 submit 進去，池子自己排隊
        - 同一時間最多 4 個在跑，有一個跑完，就補下一個進來
        - 10 個任務 / 4 個 worker，大約分 3 輪：4 + 4 + 2

為什麼用 Process 不用 Thread
    「1 加到 1 億」是純 CPU 運算。Python 有 GIL，同一時間只有一個 thread 能真正在算，
    開 4 個 thread 不會變快。要真的 4 個並行，就要 4 個 process (各自一把 GIL)。
    (如果任務是等網路、等檔案 I/O，才適合 ThreadPoolExecutor)

流程
    main
     │  submit 10 次 (立刻回傳，不會等)
     ▼
    ┌───────────────────────────── 佇列 ─────────────────────────────┐
    │ #1 #2 #3 #4 │ #5 #6 #7 #8 #9 #10                              │
    └─────┬───────────────────────────┬─────────────────────────────┘
          ▼                           ▼
    worker x4 同時跑            有 worker 空出來，就從佇列補下一個
          │
          ▼
    as_completed：誰先跑完誰先印
"""
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

MAX_WORKERS = 4  # worker 同時並行的上限
TASK_COUNT = 10  # 一共送幾個任務
LIMIT = 100_000_000  # 1 加到 1 億


def sum_to(i_task_id: int, i_limit: int):
    """1 + 2 + ... + i_limit。回傳 (任務編號, 結果, 花費秒數, 哪個 process 跑的)。"""
    f_begin = time.time()
    i_total = 0
    for i_n in range(1, i_limit + 1):
        i_total += i_n
    f_cost = time.time() - f_begin
    return i_task_id, i_total, f_cost, os.getpid()


def main():
    f_start = time.time()

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as o_executor:
        # 連續送出 10 個任務：submit 不會等，馬上回傳 future，超過 4 個的自動排隊
        d_future_to_id = {}
        for i_task_id in range(1, TASK_COUNT + 1):
            o_future = o_executor.submit(sum_to, i_task_id, LIMIT)
            d_future_to_id[o_future] = i_task_id
            print(f"[送出] 任務 {i_task_id}")

        # 誰先跑完誰先處理
        for o_future in as_completed(d_future_to_id):
            i_task_id, i_total, f_cost, i_pid = o_future.result()
            f_elapsed = time.time() - f_start
            print(f"[完成] 任務 {i_task_id:>2}  結果={i_total}  單個耗時={f_cost:.1f}s  pid={i_pid}  總經過={f_elapsed:.1f}s")

    print(f"全部完成，總共 {time.time() - f_start:.1f} 秒")


# ProcessPoolExecutor 會重新 import 這個檔案，一定要有這個判斷，否則子 process 會無限開下去 (macOS / Windows)
if __name__ == "__main__":
    main()
