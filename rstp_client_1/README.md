## SDP 格式
```
sdp: v=0
o=- 0 0 IN IP4 127.0.0.1
s=rtsp://192.168.254.102:8554/mystream
c=IN IP4 0.0.0.0
t=0 0
m=video 0 RTP/AVP 96
a=control:trackID=0
a=rtpmap:96 H264/90000
a=fmtp:96 packetization-mode=1; profile-level-id=64001F; sprop-parameter-sets=Z2QAH6y0AoAt03BQYFBtChNQ,aO4G8sA=
m=audio 0 RTP/AVP 97
a=control:trackID=1
a=rtpmap:97 mpeg4-generic/44100/1
a=fmtp:97 config=1208; indexdeltalength=3; indexlength=3; mode=AAC-hbr; profile-level-id=1; sizelength=13; streamtype=5


```

## 核心思維
1. RSTP 每一次都會回傳 cpu tick 數量
2. RSTP 一段時間會回傳 unix time 時間
3. 只要 我把當前 tick 數 - 上一次 的 tick 數 （並且知道一個 tick 多少時間）， 再加上 上一次 unix time 就是時間了。