import sys
from anylabeling.app import main

def start_app():
    # 你可以預設一些參數，例如啟動時直接打開某個資料夾
    # sys.argv = ["anylabeling", "你的圖片路徑"] 
    
    print("正在透過 Python 環境啟動 X-AnyLabeling...")
    sys.exit(main())

if __name__ == "__main__":
    start_app()