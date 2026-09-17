from concurrent import futures
import logging
import grpc
# 引入自動生成的類別
from pb import helloworld_pb2
from pb import helloworld_pb2_grpc

# 實作在 proto 裡面定義的 GreeterServicer
class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        logging.info(f"收到來自 {request.name} 的請求")
        # 回傳 proto 定義的 HelloReply 訊息
        return helloworld_pb2.HelloReply(message=f"哈囉, {request.name}! 這是來自 gRPC Server 的回應。")

def serve():
    # 建立 gRPC 伺服器，並設定執行緒池（Thread Pool）
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    
    # 將實作的 Greeter 註冊到伺服器中
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    
    # 監聽 本地端 50051 連接埠
    server.add_insecure_port('[::]:8181')
    logging.info("gRPC Server 已啟動，監聽連接埠 8181...")
    server.start()
    # 保持伺服器持續運作
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()


##$ 公式
##1. 定義一個 proto 裡面有 GreeterService 服務 跟方法 SayHello
##2. 使用 grpcio-tools 生成 grcp python 的基礎程式碼 （一個是 grpc server代碼，一個是 grpc 資料定義代碼）
##3. 實作 GreeterService 服務的 SayHello 方法， 其中 Greeter , SayHello 是 proto 裡面定義的服務和方法 ,在這裡實作
##4. SayHello 方法的參數是 HelloRequest ，回傳的是 HelloReply（並且需要 helloworld_pb2 再包一層）