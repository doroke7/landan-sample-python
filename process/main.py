from multiprocessing import Process
import os

def cpu_heavy_task(name):
    print(f"進程 {name} (PID: {os.getpid()}) 開始瘋狂計算...")
    # 模擬一個耗時的 CPU 計算
    count = 0
    for _ in range(50000000):
        count += 1
    print(f"進程 {name} 計算完成。")

if __name__ == "__main__":
    processes = []
    
    # 建立 4 個獨立的進程，分別丟給不同 CPU 核心
    for i in range(4):
        p = Process(target=cpu_heavy_task, args=(f"Worker-{i}",))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()
    print("所有核心計算結束！")