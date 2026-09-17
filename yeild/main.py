

def tasks():
    yield "roar"  # 暫停！把控制權交還給遊戲主迴圈，等下一幀

    yield "patrolling"  # 又暫停！

    yield "attack"

y_tasks = tasks()

print(next(y_tasks))  
print(next(y_tasks))  
print(next(y_tasks))  


print("--------------------------------")

for s_task in tasks():
    print(s_task)


# 在傳統函數 非grpc 的，yeild 的好處就是 
# 1. 可以做出分段函數的效果；
# 2. 把函數for-loop化