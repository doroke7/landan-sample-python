import copyreg
import pickle

"""
用 copyreg 來 pickle 一些 無法存入的特殊值
"""

class AdvancedCalculator:
    def __init__(self, op_type="add"):
        self.op_type = op_type
        self.formula = lambda x: x + 1
        self.count = 0  # 👈 這是會動態改變的資料！

# 🔧 改善後的拆解說明書：把所有狀態一網打盡
def extract_advanced(calc_obj):
    # 我們把動態的 count 還有 op_type 一起打包成一個 Dict 傳出去
    state = {
        "op_type": calc_obj.op_type,
        "count": calc_obj.count
    }
    return (rebuild_advanced, (state,))

# 🔧 改善後的組裝說明書
def rebuild_advanced(state):
    # 1. 先用 op_type 建立新物件（把 lambda 生回來）
    obj = AdvancedCalculator(state["op_type"])
    # 2. 把當時活生生的 count 數值塞回去
    obj.count = state["count"]
    return obj

copyreg.pickle(AdvancedCalculator, extract_advanced)

# --- 測試：如果中途資料變了 ---
c = AdvancedCalculator()
c.count = 999  # 👈 故意改成 999

# 打包再還原
frozen = pickle.dumps(c)
new_c = pickle.loads(frozen)

print(f"還原後的 count 依然是: {new_c.count}")  # 完美印出 999！