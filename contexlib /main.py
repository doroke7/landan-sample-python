from contextlib import contextmanager

@contextmanager
def db_transaction():
    """ 模擬一個資料庫交易的 try-except-finally 上下文管理器 """
    print("▶️ [開始] 自動開啟 Database Transaction")
    try:
        # yield 會把控制權交給 with 內部的程式碼
        # 如果你想傳遞物件（例如 db 連線），可以寫 yield db_connection
        yield 
        
        print("✅ [成功] 內部沒出錯，自動執行 Commit")
    except Exception as e:
        print(f"❌ [失敗] 內部出錯了！自動執行 Rollback。錯誤原因: {e}")
        raise # 決定要把錯誤繼續往外丟，還是吞掉。如果不寫 raise 就是吞掉。
    finally:
        print("⏹️ [結束] 自動關閉 Database 連線")

# --- 實際使用 ---

print("--- 測試 1：正常執行的狀況 ---")
with db_transaction():
    print("   正在寫入使用者資料...")
    print("   正在更新商品庫存...")

print("\n--- 測試 2：內部發生嚴重錯誤的狀況 ---")
try:
    with db_transaction():
        print("   正在扣除帳戶餘額...")
        raise ValueError("餘額不足！")  # 故意引發一個錯誤
except ValueError:
    print("最外層：成功捕捉到被 throw 出來的錯誤")