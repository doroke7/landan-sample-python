## 學習重點
```txt
A. 下載代碼
B. 以 uv 安裝 python 基本套件
C. Labelme 標記套件使用辦法
   > 一種介面，如果告訴框架，定義我們的 物品是什麼

D. 定義你的 推論流程 pipeline

E. Yolo 套件的使用辦法 
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

# C. Labelme 標記套件使用辦法
1. 以命令啟動Labelme 標記套件
```zsh 
cd yolo_labelme 
uv run labelme ./datasets --labels ./cfg/classes.txt

```
2. 定義“全”類型基本設定檔
```
./cfg/classes.txt
```

3. 放你想要標記的圖片集合
```
./datasets
```
# D. 定義我們的 推論 pipeline （撲克牌為例子） 

## D-1. 策略A (找 卡 -> 判斷 卡類型 -)
優點: 每個基礎模型小，可以用 nano 等級模型
缺點: 推論流程複雜
```
              原始照片
                 │
                 ▼
        ① detect {Card}──── 找出畫面中每張撲克牌的位置（不分花色/正反面，只有 1 類）
                 │
                 │ 依 box 裁切
                 ▼
        ② classify「card」── 判斷這張牌是 {Front}／{Back}／{Flow}
                 │
        ┌────────┼─────────────┐
        ▼        ▼             ▼
      Back     Flow          Front
        │        │             │
        └───┬────┘             │
            ▼                  │
        輸出：Back / Flow       ├──► ③ classify「suit」── {Spade}|{Diamond}|{Heart}|{Club}
        （不用判斷花色點數）      │
                               └──► ④ classify「rank」── {A}|{2}~{10}|{J}|{Q}|{K}
                                          │
                                          ▼
                                    輸出：花色 + 點數
```

## D-2. 策略B (detect「Front / Back / Flow」 -> 如果是 Front -> classify-rank, classify-suit)

介於策略 A 和策略 C 之間：detect 不是只找「Card」，而是直接把正面、卡背、Flow 卡分成 3 類，省掉策略 A 的 classify「card」那一步；只有正面（Front）才需要再判斷花色和點數。對應專案現有的 detect strategy `poker/front_back_flow`（`cfg/poker/detect/front_back_flow/index.yaml`），這個 strategy 有練，但目前沒有接進 `annotate-auto-label` 的 pipeline。
```
              原始照片
                 │
                 ▼
        ① detect「Front / Back / Flow」── 找出每張撲克牌的位置，並直接判斷是正面／卡背／Flow 卡（共 3 類）
                 │
        ┌────────┼─────────────┐
        ▼        ▼             ▼
      Back     Flow          Front
        │        │             │
        └───┬────┘             │ 依 box 裁切
            ▼                  │
        輸出：Back / Flow       ├──► ② classify「suit」── Spade|Diamond|Heart|Club
        （不用判斷花色點數）      │
                               └──► ③ classify「rank」── A|2~10|J|Q|K
                                          │
                                          ▼
                                    輸出：花色 + 點數
```

## D-3. 策略C (直接 detect 每一張牌：梅花1、梅花2 ... 加上 卡背、Flow 卡)
優點： 推論流程 pipeline 簡單
缺點： 樣本數量需要很大 （照片多）, 需要用 大型XL模型（Yolo XL 版本） 
```
              原始照片
                 │
                 ▼
        ① detect「54 類」── 一次找出畫面中每張撲克牌的位置，並直接判斷是哪一張牌／卡背／Flow 卡
                                  │
    ┌─────────┬─────────┬─────────┼─────────┬─────────┬─────────┐     
    ▼         ▼         ▼         ▼         ▼         ▼         ▼
 Club_A    Club_2    Club_3      ...     Spade_K    Back      Flow

  （共 54 條路線）

        正面 52 種
          梅花 Club    : Club_A    Club_2    ...  Club_10    Club_J    Club_Q    Club_K
          方塊 Diamond : Diamond_A Diamond_2 ...  Diamond_10 Diamond_J Diamond_Q Diamond_K
          紅心 Heart   : Heart_A   Heart_2   ...  Heart_10   Heart_J   Heart_Q   Heart_K
          黑桃 Spade   : Spade_A   Spade_2   ...  Spade_10   Spade_J   Spade_Q   Spade_K
        非正面 2 種
          卡背         : Back
          Flow 卡      : Flow

        輸出：花色 + 點數，或 Back / Flow
        （detect 的類別名稱就是答案，不用再 classify）
```








# E. yolo 套件的使用辦法。
1. 按照 Yolo Detect 官方格式 給他喂統計資料。一定得按照這個格式，除非你自己寫 Torch
```
   a. train 訓練母體資料, 裡面有所有 Card 的標記文案, 大約放 80%的照片
   b. val 訓練時候驗證資料, 裡面有 Card 的標記文案, 大約放 10%的照片
   c. test 訓練完成的資料, 裡面有 Card 的標記文案, 大約放 10%的照片
   d. 以 原圖 + txt 放置文件
   e. cfg 訓練參數文件
```
2. Detect 是什麼？
```
   思維：detect 是給模型 “大圖”，然後模型幫我們 “找東西” + “判斷類型”
   程式碼：就是 給他圖片 buffer， 模型 return 東西的 array 包含類型
```
3. 以 detect-poker-card 為例子，使用 yolo detect 訓練 ，（detect:撲克牌:卡片 所有位置的 模型）
```
cd sample/yolo_detect_poker_card
```

4. 使用 yolo classiy 訓練 ，以 detect-poker-card 為例子 （切圖前提下，classify:卡片:是 【Flow, Back, Front】的 模型）
```
uv run python ./src/main.py
```

5. 產生一個 best.pt 模型，他是一個 torch 格式的模型
```
給他圖片 buffer， 模型 return 東西的 array 包含類型
```


6. 按照 Yolo Calssify 官方格式 給他喂統計資料。一定得按照這個格式，除非你自己寫 Torch
```
   a. train 訓練母體資料, 裡面有所有 Card 的標記文案, 大約放 80%的照片
   b. val 訓練時候驗證資料, 裡面有 Card 的標記文案, 大約放 10%的照片
   c. test 訓練完成的資料, 裡面有 Card 的標記文案, 大約放 10%的照片
   d. 以 裁切圖 + 目錄區分 放置文件
   e. cfg 訓練參數文件
```
7. Classify 是什麼？
```
   思維：detect 是給模型 “小圖”，然後模型幫我們 “判斷類型”
   程式碼：就是 給他圖片 buffer， 模型 return 東西的類型 （不含位置）
```
8. 以 classify-poker-suit 為例子，使用 yolo detect 訓練 ，（detect:撲克牌:卡片 所有位置的 模型）
```
cd ./yolo_classify_poker_suit
```

9. 使用 yolo classiy 訓練 ，以 classify-poker-suit 為例子 
```
uv run python ./src/main.py
```

10. 產生一個 best.pt 模型，他是一個 torch 格式的模型
```
給他圖片 buffer， 模型 return 東西的類型 （不含位置）
```
