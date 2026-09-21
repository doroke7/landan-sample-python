## RSTP client 應該怎麼寫
1. 利用享元模式 相同 url rstp 共用一個連結
2. 不同地方呼叫 這個client ，如果 url 相同，拿到的是同一個。



## 整套 視訊流推論應該怎麼做
1. 維護一個 rstp client ，具有 相同 url 拿到一個具體client
2. 這個 得到圖片的事情，具有緩存 1秒，並且產生唯一id（id 可以用 url + unixtime）

3. 維護一個 推論 模型，他具有 維護 worker，他會把 輸入的圖片（包含id） 輸入給推論模型
4. 如果 id 相同就回傳緩存，緩存具有 10秒

5. 由 service-controller 控制定時機制