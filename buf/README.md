## buf 的優點是什麼
1. buf 是一個 proto 生成基本代碼工具
2. buf 相當是一個工具，他把瑣碎的 proto指令，用 yaml 集成起來
3. buf 是跨平台（win ios），跨語言（適用各種語言）
4. buf 可以指定 編譯工具版本，避免不同研發 對於相同的 proto文件，由於 python 或 go 版本不同導致 生成的代碼不同。

## 方案A-原生 proto 產生 基本python gRPC程序
```
python -m grpc_tools.protoc --proto_path=proto --python_out=. --grpc_python_out=. proto/user_service.proto
```

## 方案B-原生 buf 產生 基本python gRPC程序
```
# 根據 buf.yaml + bug.gen.yaml 的配置
buf generate
```

