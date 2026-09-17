## Google+Python 官方最建議的 proto 目錄結構
```
1. 根目錄有 proto 與 src 目錄
2. proto 目錄裡面的 .proto 目錄結構 應該 與 src 目錄對齊
3. proto 底下 + src 底下 皆有 pb2 目錄，即為 proto/pb2  src/pb2。（pb2 可以是其他名稱）
4. 核心思維就是從 proto/pb2 轉譯一樣結構的.proto 文件 變成 .py 代碼到 src/pb2
5. 其實其他語言也應該如此，但是其他語言沒有 python 目錄即為namespace 的問題
```
```
6. 例子：

===================================================================================
【項目根目錄】 (PYTHONPATH 起跑線)
===================================================================================
 ├── proto/                          # 👈 1. 原始碼大本營
 │    └── pb2/                       # 👈 3. 兩側一致的自訂名稱
 │         └── admin/                # 👈 2. 與 src 完全對齊的
 │              └── services/        #    「多層洋蔥結構」
 │                   └── user.proto
 │
 └── src/                            # 👈 1. 你的手寫業務代碼
      └── pb2/                       # 👈 3. 兩側一致的自訂名稱
           └── admin/                # 👈 4. 核心思維：被一比一「轉譯並搬運」
                └── services/        #    過來的實體 Python 檔案群
                     ├── user_pb2.py
                     └── user_pb2_grpc.py ── 💡 內部代碼: "import pb2.admin.services.user_pb2"
          main.py
```


# Python 生成 pb 代碼
```
python3 -m grpc_tools.protoc \
  --proto_path=./proto \
  --python_out=./src \
  --grpc_python_out=./src \
  $(find ./protos -name "*.proto")
```


## Python 參數說明
找到相對路徑的 proto文件，然後標示 proto_path 解構目錄
然後指定 message 跟 server 個別出去的目錄，
不會受到 proto 的 package影響目錄
```
python -m grpc_tools.protoc \             # 使用python指定的生祠次
--proto_path=. \                          # 如果 .proto 文件遇到 import 需要從哪裡找資源, 
 \                                        # 生成預設使用 proto 文件的相對目錄生成目錄, 
 \                                        # 如果加上這個參數，生成代碼時，編譯器會自動扣除 --proto_path 所指定的路徑
--python_out=./abc \
--grpc_python_out=./xyz \
./protos/helloworld.proto                 # 從哪些檔案開始（需要填寫相對目錄，跟 --proto_path 參數無關）
```




## 總結
```

```