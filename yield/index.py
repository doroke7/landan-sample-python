astr='ABC'
# 列表
alist=[1,2,3]
# 字典
adict={"name":"wangbm","age":18}
# 生成器
agen=(i for i in range(4,8))

def gen(*args, **kw):
    print(kw)
    for item in args:
        for i in item:
            yield i

new_list=gen(astr, alist, adict, agen, abc='2222')
print(list(new_list))
