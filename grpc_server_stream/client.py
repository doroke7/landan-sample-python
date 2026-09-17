import grpc

# 匯入調整後的自動生成程式碼
import message_pb2
import message_pb2_grpc

def run():
    # 建立與伺服器的連線通道
    with grpc.insecure_channel('localhost:50051') as channel:
        # 建立 Stub (客戶端代理)
        stub = message_pb2_grpc.MessageServiceStub(channel)
        
        # 準備請求內容
        request = message_pb2.MessageRequest(
            topic="TechNews",
            user_id="user_9527"
        )
        
        print("正在向伺服器訂閱即時訊息串流...")
        
        try:
            # 呼叫 RPC 方法，拿到的是一個可迭代的串流物件
            response_stream = stub.SubscribeMessages(request)
            
            # 使用 for 迴圈不斷接收伺服器傳過來的訊息
            for response in response_stream:
                print("\n=== 收到伺服器推播 ===")
                print(f"序號: {response.sequence}")
                print(f"時間戳: {response.timestamp}")
                print(f"內容: {response.content}")
                
            print("\n串流結束：伺服器已完成所有資料發送。")
            
        except grpc.RpcError as e:
            print(f"gRPC 連線發生錯誤: {e.details()}")

if __name__ == '__main__':
    run()