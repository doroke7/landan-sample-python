import logging
# 引入自動生成的類別
from pb import helloworld_pb2
from pb import helloworld_pb2_grpc

# 實作在 proto 裡面定義的 GreeterServicer
class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        logging.info(f"收到來自 {request.name} 的請求")
        # 回傳 proto 定義的 HelloReply 訊息
        return helloworld_pb2.HelloReply(message=f"哈囉, {request.name}! 這是來自 gRPC Server 的回應。")