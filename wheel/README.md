## 請在更目錄安裝 python



## 打包 wheel + tar.gz 套件出來
```
python -m build
```



## 以 “源碼” 安裝(冷安裝，不跟代碼修改)爲 python 的 pip pakcage
```
pip install .
```



## 以 “源碼” 安裝(熱安裝，會跟代碼修改)爲 python 的 pip pakcage
```
pip install -e .
```

## 以 “打包” 安裝(冷安裝，不跟代碼修改)爲 python 的 pip pakcage
```
pip install dist/printer-1.0.0-py3-none-any.whl
```


## 使用 whl 文件有什麼好處
```
方便部署 運行
```

## pip 安裝 whl 文件 或 安裝 目錄到底做了什麼事情
```
把這個項目當作 一個 pip package 使用 並且安裝這個項目的附屬套件
```


##這個包名
（也就是你寫 import xxx 時的那個 xxx）是由你代碼中的**「資料夾名稱」**決定的，而不是由 pyproject.toml 裡的 name 決定的！
