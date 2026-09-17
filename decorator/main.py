# 1. 定義一個裝飾器函數，它必須接收一個函數 (func) 作為參數
def my_decorator(func):
    
    # 2. 在內部包裝一個全新的函數
    def wrapper():
        print("▶️ [裝飾器] 準備執行函式了...")
        
        func()  # 真正執行原本的函式
        
        print("⏹️ [裝飾器] 函式執行完畢！")
        
    # 3. 把這個包裝好的全新函數「回傳」出去
    return wrapper

# --- 如何使用？ ---
# 只要在你想外掛功能的函式上方，加上 @裝飾器名稱
@my_decorator
def say_hello():
    print("   Hello World!")

# 呼叫它
say_hello()