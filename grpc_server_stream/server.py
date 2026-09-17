import time
from concurrent import futures
import grpc

# 匯入調整後的自動生成程式碼
import message_pb2
import message_pb2_grpc

class MessageServiceServicer(message_pb2_grpc.MessageServiceServicer):
    
    def SubscribeMessages(self, request, context):
        print(f"收到來自用戶 [{request.user_id}] 的訂閱請求，主題: {request.topic}")
        
        for i in range(1, 6):  # 模擬推播 5 次
            
            # 檢查客戶端是否已斷開連線
            if not context.is_active():
                print("客戶端已斷開連線，停止推送。")
                break
                
            # 建立要回傳的訊息物件
            response = message_pb2.MessageResponse(
                content=f"這是推播給主題 [{request.topic}] 的即時訊息內容",
                timestamp=int(time.time()),
                sequence=i
            )

            # gRPC stream server 的重點是 存在一個 for 接續 yield 若干個 （或是 不斷迭代的 yield 或 yield from）
            
            print(f"正在發送第 {i} 條訊息...")
            yield response  # 使用 yield 將訊息像串流一樣傳回客戶端
            
            time.sleep(1)  # 模擬每秒產生一次即時資料

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # 註冊服務
    message_pb2_grpc.add_MessageServiceServicer_to_server(MessageServiceServicer(), server)
    
    server.add_insecure_port('[::]:50051')
    print("gRPC 伺服器已啟動，監聽 port 50051...")
    server.start()
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("伺服器關閉。")

if __name__ == '__main__':
    serve()