## 學習重點
```txt
A. 下載代碼
B. 以 uv 安裝 python 基本套件
C. Labelme 標記套件使用辦法
   > 一種介面，如果告訴框架，定義我們的 物品是什麼

D. Yolo 套件的使用辦法 
   > detect
   > classify
```

# A. 下載代碼
```zsh
git clone https://github.com/doroke7/landan-sample-python.git
```
# B. 以 uv 安裝 python 基本套件
```zsh
cd landan-sample-python
cd yolo_labelme && uv venv .venv --seed --clear && uv sync && cd ..
cd yolo_detect_poker_card && uv venv .venv --seed --clear && uv sync && cd ..
cd yolo_classify_poker_suit &&  uv venv .venv --seed --clear && uv sync && cd ..
cd landan-sample-pythonyolo_classify_poker_rank && uv venv .venv --seed --clear && uv sync && cd ..

```

# C. 
```zsh Labelme 標記套件使用辦法
cd yolo_labelme 
uv run labelme datasets --labels cfg/classes.txt

```


# D. yolo 套件的使用辦法。
1. 我們需要按照 Yolo 官方格式 給他統計資料，然後訓練 >> 你要用別人的工具，就要按照別人的遊戲規則。除非你自己寫 Torch
2. Detect 是什麼？
   思維：detect 是給模型 “大圖”，然後模型幫我們 “找東西” + “判斷類型”
   程式碼：就是 給他圖片 buffer， 模型 return 東西的 array 包含類型
2. 使用腳本 python ，喂給他訓練格式的資料夾規格，然後訓練
3. 使用 yolo detect 訓練 ，以 detect-poker-card 為例子（detect:撲克牌:卡片 所有位置的 模型）
   a. train 訓練母體資料, 裡面有所有 Card 的標記文案, 大約 80%的照片
   b. val 訓練時候驗證資料, 裡面有 Card 的標記文案, 大約 10%的照片
   c. test 訓練完成的資料, 裡面有 Card 的標記文案, 大約 10%的照片
   d. 以 原圖 + txt 放置文件

4. 使用 yolo classiy 訓練 ，以 detect-poker-card 為例子 （切圖前提下，classify:卡片:是 【Flow, Back, Front】的 模型）
   a. train 訓練母體資料, 裡面有所有 Flow,Back,Front 的截圖資料夾 , 大約 80%
   b. val 訓練時候驗證資料, 裡面有 Flow,Back,Front 的截圖資料夾 , 大約 10%
   c. test 訓練完成的資料, 裡面有 Flow,Back,Front 的截圖資料夾 , 大約 10%

5. 使用 yolo classiy 訓練 ，以 detect-poker-rank 為例子 （切圖前提下，classify:前片:是 【什麼點數】的 模型）
6. 使用 yolo classiy 訓練 ，以 detect-poker-suit 為例子 （切圖前提下，classify:前片:是 【什麼花色】的 模型）

