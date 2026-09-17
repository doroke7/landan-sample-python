## import的注意事項
1. import 預備思維：python 是 1990s 發展的語言，所以受到當時 linux 系統影響很大
2. import . 的 點 代表當前目錄，但是py 文件必須要在模組目錄裡面才生效，使用 . 之後就不會去全局找模組
3. 同級的 python main.py ，的 。 是不生效的，除非到 main 的父級目錄執行 
4. 在 python package 是 【目錄裡面 有__init__.py 入口文件將 目錄入口的 目錄】 或 【目錄裡面 有 py 文件的目錄】，如果目錄裡面只有目錄， 不是 package
5. 換言之。 import a.b 然後用 a.b.c.test 是不行的 
6. import XX 的 xx，只能是一個類模組
（變量類：如文件裡面的 class, function, variable, 
  文件類：module（就是 py文件本身）, 
  目錄類： 標準-package （帶有 __init__.py 的目錄 ）,python 3.3+ 增加的 package 是任何目錄
  ），不能單純是目錄
7. 模組來源： 1.py 文件裡面的變量 2. py 文件本身 3. 帶有 __init__.py 的目錄 其他目錄
    5-1. 文件名是一個模組，文件裡面的變量也是一個模組
    5-2. from a.b.c import test (test.py 是一個模組)
    5-3. from a.b.c.test import Test (Test 類別 是一個模組)
    5-4. 在 c 目錄寫了 __init__.py c 目錄就算一個模組了
    5-5. from a import b 也是可以


# 結論：*.py 文件裡面的類別(變量類), 目錄下的 *.py 文件(模組類), 具有 __init__.py 的目錄或一般目錄（package類）， 剩下的路徑如果不夠透過 from 來定位