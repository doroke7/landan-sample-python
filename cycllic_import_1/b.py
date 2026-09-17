
class B():
    def bb():
        pass
    pass

b = B()

# 引入 a 之前都還沒有 從 a 用到 b，扣除了循環依賴
import a

a.show()