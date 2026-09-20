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