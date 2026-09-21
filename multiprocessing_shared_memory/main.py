from multiprocessing import Process, shared_memory
import numpy as np

def writer_process(sName, shape, dtype):
    # 連接到已建立的共享記憶體
    oSharedMemory = shared_memory.SharedMemory(name=sName)
    # 將共享記憶體包裝成 NumPy 陣列 (直接操作實體記憶體，零複製！)
    img_array = np.ndarray(shape, dtype=dtype, buffer=oSharedMemory.buf)
    
    # 模擬填入影像數據 (例如 OpenCV 抓到的影像)
    img_array[:] = 255  # 將整張圖改成白色
    
    oSharedMemory.close()

if __name__ == "__main__":
    # 假設一張 1080p 的 BGR 影像 (1080, 1920, 3)，型態為 uint8
    image_shape = (1080, 1920, 3)
    image_dtype = np.uint8
    size_bytes = int(np.prod(image_shape) * np.dtype(image_dtype).itemsize)
    
    # 1. 建立共享記憶體
    oSharedMemory = shared_memory.SharedMemory(create=True, size=size_bytes)
    
    # 2. 開啟另一個 Process 寫入影像
    oProcess = Process(target=writer_process, args=(oSharedMemory.name, image_shape, image_dtype))
    oProcess.start()
    oProcess.join()
    
    # 3. 主行程直接讀取寫入後的影像數據
    main_img = np.ndarray(image_shape, dtype=image_dtype, buffer=oSharedMemory.buf)
    print("主行程讀取的平均像素值:", main_img.mean())  # 輸出 255.0
    
    # 4. 釋放與清理資源
    oSharedMemory.close()
    oSharedMemory.unlink()  # 告知作業系統回收這塊記憶體
