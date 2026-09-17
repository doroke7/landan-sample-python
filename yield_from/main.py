'''

def sub_generator():
    yield "A"
    yield "B"

def main_generator():
    # 以前必須這樣一筆一筆撈出來，再傳出去
    for item in sub_generator():
        yield item
    yield "C"

# 測試
print(list(main_generator()))  # 輸出: ['A', 'B', 'C']


'''


def sub_generator():
    yield "A"
    yield "B"

def main_generator():
    yield from sub_generator()  # 一行搞定！直接把管道接通
    yield "C"

# 測試
print(list(main_generator()))  # 輸出: ['A', 'B', 'C']


## 簡單的說 yield from 就是一個 yield 展開 語法糖