
from a.b.c import test
from a.b.c.test import Test

# import a.b.c
# import a.b
from a.b import c

# 走的是 test.py 文件裡面的 Test 類別
o_test1 = test.Test()
o_test1.do('從 引入 test.py 後使用')

# 走的是 Test 類別
o_test2 = Test()
o_test2.do('從 引入 Test 類別 後使用')

# 走的是 a/b/c/__init__.py 的變量 Test
o_test3 = c.Test()
o_test3.do('從 引入 c/__init__.py 的變量類別 後使用')

# 走的是 a/b/c/test.py 的變量 Test
o_test4 = c.test.Test()
o_test4.do('從 引入 a/b/c/test.py 的類別 後使用')

