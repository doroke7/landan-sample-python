"""
RTSP client：讀取每一幀的「絕對時間」(NTP 牆上時間)，純標準庫，不需安裝套件。

原理
    RTP 封包只帶相對時間戳 (rtp_ts)，起點隨機。
    RTCP Sender Report (SR) 會給一組對照： rtp_ts_sr  <->  ntp_time_sr
    所以任一封包的絕對時間 = ntp_time_sr + (rtp_ts - rtp_ts_sr) / clock_rate

用法
    python main.py rtsp://localhost:8554/mystream
    python main.py rtsp://user:pass@host:8554/cam --seconds 30

注意
    - 拿到的時間是「來源端」的時鐘。攝影機要開 NTP 校時；ffmpeg / OBS 推流則是推流主機的時間。
    - 來源沒送 SR 時，收不到絕對時間 (會顯示 no-sr)。
    - 只支援 TCP interleaved 傳輸、無認證或 URL 帶帳密的 Basic 認證 (不支援 Digest)。

流程
    OPTIONS -> DESCRIBE (取 SDP) -> SETUP (要求 TCP interleaved) -> PLAY -> 持續讀封包
    interleaved 封包格式： '$' + channel(1 byte) + length(2 bytes) + payload
        channel 0 = RTP (影像資料)，channel 1 = RTCP (含 SR)

絕對時間 abs 是怎麼算出來的

    ┌─────────────────────────────────────────────────────────────┐
    │ 握手                                                        │
    │   DESCRIBE 拿到 SDP ──> pick_video() ──> clock_rate (90000) │
    │   SETUP / PLAY (TCP interleaved)                            │
    └──────────────────────────────┬──────────────────────────────┘
                                   ▼
                     sock_recv_interleaved() 持續收封包
                                   │
                  ┌────────────────┴────────────────┐
             channel 1 (RTCP)                  channel 0 (RTP)
                  │                                 │
                  ▼                                 ▼
             parse_sr()                        parse_rtp()
        取出 SR 裡的兩個值：                  取出這一幀的：
          sr_rtp_ts   (計數)                    i_ts  (rtp_ts 計數)
          sr_unix     (牆上時間)
                  │                                 │
                  ▼                                 │
      存成校準點 (sr_rtp_ts, sr_unix)               │
                  │                                 │
                  └────────────────┬────────────────┘
                                   ▼
                       校準點還沒收到？ ──是──> 印 abs=no-sr
                                   │否
                                   ▼
             i_diff = i_ts - sr_rtp_ts        (差幾個 tick，處理 32-bit 環繞)
                                   ▼
             秒數   = i_diff / clock_rate     (tick 換成秒)
                                   ▼
             abs    = sr_unix + 秒數          (校準點時間 + 經過秒數)

    數字範例 (clock_rate = 90000)
        SR：  rtp_ts=90000  <->  22:13:20.500
        RTP： rtp_ts=180000
        差值 = 90000 tick = 1 秒  ->  abs = 22:13:21.500
"""
import argparse
import base64
import re
import socket
import struct
import time
from urllib.parse import urlparse

# NTP epoch (1900-01-01) 與 Unix epoch (1970-01-01) 相差的秒數
NTP_UNIX_OFFSET = 2208988800


def parse_sr(b_payload: bytes):
    """解析 RTCP compound packet，回傳第一個 SR 的 (rtp_ts, unix_time)，沒有則 None。"""
    # 一個 RTCP 封包可能串了多個子封包 (SR + SDES ...)，逐個往後走
    i_pos = 0
    while i_pos + 4 <= len(b_payload):
        # 子封包 header：版本/旗標(1B)、packet type(1B)、長度(2B，單位為 4 bytes，且不含第一個 word)
        i_first, i_pt, i_len = struct.unpack_from("!BBH", b_payload, i_pos)
        i_size = (i_len + 1) * 4
        if i_pt == 200 and i_size >= 28:  # 200 = Sender Report
            # SR 內容：ssrc、ntp 秒、ntp 小數、rtp 時間戳 (後面還有封包數、位元組數，不需要)
            _, i_ntp_sec, i_ntp_frac, i_rtp_ts = struct.unpack_from("!IIII", b_payload, i_pos + 4)

            # NTP 時間 = 32-bit 整數秒 + 32-bit 小數 (單位 1/2^32 秒)，轉成 Unix 秒 (float)
            f_unix = i_ntp_sec - NTP_UNIX_OFFSET + i_ntp_frac / 2**32
            return i_rtp_ts, f_unix
        i_pos += i_size
    return None


def parse_rtp(b_payload: bytes):
    """回傳 (payload_type, seq, rtp_ts, marker)。"""
    # RTP 固定 header 12 bytes：旗標、(marker+payload type)、序號、時間戳、ssrc
    i_b0, i_b1, i_seq, i_ts, _ssrc = struct.unpack_from("!BBHII", b_payload, 0)
    # marker 位元在影像中通常代表「一幀的最後一個封包」
    return i_b1 & 0x7F, i_seq, i_ts, bool(i_b1 & 0x80)


class RtspClient:
    def __init__(self, s_url: str):
        o_u = urlparse(s_url)

        self.url = s_url
        self.host = o_u.hostname
        self.port = o_u.port or 554  # RTSP 預設 port
        # URL 帶帳密時，組成 Basic 認證 header
        self.auth = ""
        if o_u.username:
            s_cred = f"{o_u.username}:{o_u.password or ''}"
            self.auth = "Authorization: Basic " + base64.b64encode(s_cred.encode()).decode() + "\r\n"
        # 請求用的 URL 不含帳密
        self.req_url = f"rtsp://{self.host}:{self.port}{o_u.path or '/'}" + (f"?{o_u.query}" if o_u.query else "")
        self.sock = socket.create_connection((self.host, self.port), timeout=10)
        self.buf = b""  # 接收緩衝：socket 讀到的資料先放這，再依需要切出
        self.cSeq = 0  # 相當於 request_id（每個請求 +1），只是 RTSP 習慣叫它 CSeq
        self.session = ""  # SETUP 後伺服器給的 Session ID，之後每個請求都要帶

    def sock_recv(self):
        # 從 socket 再讀一批資料接到緩衝後面；對方關閉連線時 recv 回傳空 bytes
        byte_buffers = self.sock.recv(65536)
        if not byte_buffers:
            raise ConnectionError("server closed connection")
        self.buf += byte_buffers

    def sock_read(self, i_position: int) -> bytes:
        # 精確讀出 i_position bytes：緩衝不夠就繼續 sock_recv (TCP 是串流，不保證一次收滿)
        while len(self.buf) < i_position:
            self.sock_recv()
        b_out, self.buf = self.buf[:i_position], self.buf[i_position:]
        return b_out

    def request(self, s_method: str, s_url: str = "", d_headers: dict | None = None):
        """送出一個 RTSP 請求，回傳 (回應 header dict, body 字串)。狀態碼非 200 會丟例外。"""
        self.cSeq += 1
        s_msg = f"{s_method} {s_url or self.req_url} RTSP/1.0\r\nCSeq: {self.cSeq}\r\n"
        s_msg += "User-Agent: py-rtsp-ntp\r\n" + self.auth
        if self.session:
            s_msg += f"Session: {self.session}\r\n"
        for s_k, s_v in (d_headers or {}).items():
            s_msg += f"{s_k}: {s_v}\r\n"
        self.sock.sendall((s_msg + "\r\n").encode())  # 空行代表 header 結束

        # 讀 header (直到空行)
        while b"\r\n\r\n" not in self.buf:
            self.sock_recv()
        b_head, self.buf = self.buf.split(b"\r\n\r\n", 1)
        s_head = b_head.decode(errors="replace")
        s_status_line, *a_header_lines = s_head.split("\r\n")
        # 第一行： RTSP/1.0 200 OK
        s_version, s_status_code, s_reason = s_status_line.split(" ", 2)
        i_status = int(s_status_code)
        d_resp = {}
        for s_line in a_header_lines:
            if ":" in s_line:
                s_k, s_v = s_line.split(":", 1)
                d_resp[s_k.strip().lower()] = s_v.strip()  # key 統一轉小寫


        # 有 Content-Length 就再讀 body (DESCRIBE 的 SDP 就在這裡)
        i_body_len = int(d_resp.get("content-length", 0))
        s_body = ""
        if i_body_len:
            byte_body = self.sock_read(i_body_len)
            s_body = byte_body.decode(errors="replace")
        if i_status != 200:
            raise RuntimeError(f"{s_method} failed: {s_status_line}")
        if "session" in d_resp:
            # 格式可能是 "12345678;timeout=60"，只取 ID
            s_session_id, s_sep, s_params = d_resp["session"].partition(";")
            self.session = s_session_id
        return d_resp, s_body

    def sock_recv_interleaved(self):
        """回傳 (channel, payload)。中間若夾雜 RTSP 文字回應則略過。"""
        while True:
            b_first = self.sock_read(1)
            if b_first == b"$":  # '$' 開頭 = interleaved 封包
                i_ch, i_len = struct.unpack("!BH", self.sock_read(3))
                return i_ch, self.sock_read(i_len)
            # 非 interleaved 資料 (例如 RTSP 回應)，整段 header 丟掉
            self.buf = b_first + self.buf
            while b"\r\n\r\n" not in self.buf:
                self.sock_recv()
            _, self.buf = self.buf.split(b"\r\n\r\n", 1)

    def close(self):
        # 盡量通知伺服器結束 session；失敗也無所謂，反正要關 socket
        try:
            self.request("TEARDOWN")
        except Exception:
            pass
        self.sock.close()


def pick_video(s_sdp: str):
    """從 SDP 找出第一個 video track，回傳 (codec, payload_type, clock_rate, control)，次序與 main() 的 print 一致。"""
    # SDP 範例：
    #   m=video 0 RTP/AVP 96          <- 一個媒體段落的開頭 (最後一欄是 payload type)
    #   a=rtpmap:96 H264/90000        <- payload type 對應的編碼與 clock rate
    #   a=control:trackID=0           <- SETUP 時要用的 track 路徑
    s_codec, i_pt, i_rate, s_control = "", None, 90000, None  # 影像 clock rate 預設 90000
    b_in_video = False
    for s_line in s_sdp.splitlines():
        s_line = s_line.strip()
        if s_line.startswith("m="):
            b_in_video = s_line.startswith("m=video")
            if b_in_video:
                s_media, s_port, s_proto, s_pt, *a_more_pt = s_line.split()
                i_pt = int(s_pt)
            elif s_control:
                break  # 已取得 video 資訊，遇到下一個媒體段落就結束
        elif b_in_video and s_line.startswith("a=control:"):
            s_control = s_line[len("a=control:"):]
        elif b_in_video and s_line.startswith("a=rtpmap:"):
            o_m = re.match(r"a=rtpmap:(\d+)\s+([^/]+)/(\d+)", s_line)
            if o_m and int(o_m.group(1)) == i_pt:
                s_codec, i_rate = o_m.group(2), int(o_m.group(3))
    if s_control is None:
        raise RuntimeError("SDP 中找不到 video track")
    return s_codec, i_pt, i_rate, s_control


def main():
    o_argument_parser = argparse.ArgumentParser()
    o_argument_parser.add_argument("url")
    o_argument_parser.add_argument("--seconds", type=int, default=0, help="執行秒數，0 = 一直跑")
    o_args = o_argument_parser.parse_args()

    # 1. 握手：OPTIONS 確認連線、DESCRIBE 取得 SDP
    o_client = RtspClient(o_args.url)
    o_client.request("OPTIONS")
    _, s_sdp = o_client.request("DESCRIBE", d_headers={"Accept": "application/sdp"})
    print(f"sdp: {s_sdp}")

    s_codec, i_pt, i_rate, s_control = pick_video(s_sdp)
    print(f"video: {s_codec} pt={i_pt} clock_rate={i_rate}")

    # 2. SETUP：要求用同一條 TCP 連線傳資料 (RTP 走 channel 0、RTCP 走 channel 1)，再 PLAY 開始接收
    #    control 可能是完整 URL，也可能是相對路徑
    s_track_url = s_control if s_control.startswith("rtsp://") else o_client.req_url.rstrip("/") + "/" + s_control
    o_client.request("SETUP", s_track_url, {"Transport": "RTP/AVP/TCP;unicast;interleaved=0-1"})
    o_client.request("PLAY", d_headers={"Range": "npt=0.000-"})

    # 3. 收封包：SR 更新時間對照，RTP 用對照換算絕對時間
    i_last_rtp_ts = None  # 最近一次 SR 的 rtp_ts (校準點的計數)；還沒收到就是 None
    f_last_unixtime = None  # 最近一次 SR 的 unix 時間 (校準點的牆上時間)；還沒收到就是 None
    i_last_ts = None  # 上一幀的 rtp_ts，用來判斷是不是同一幀
    f_end = time.time() + o_args.seconds if o_args.seconds else None
    try:
        while f_end is None or time.time() < f_end:
            i_ch, byte_data = o_client.sock_recv_interleaved()
            if i_ch == 1:  # RTCP(能收到 NTP 時間)
                t_sr = parse_sr(byte_data)
                if t_sr:
                    i_last_rtp_ts, f_last_unixtime = t_sr
                    print(f"[SR] rtp_ts(相對計數)={i_last_rtp_ts}  ntp(來源牆上時間)={f_last_unixtime}")
            elif i_ch == 0 and len(byte_data) >= 12:  # RTP (至少要有 12 bytes 的 header)
                i_ptype, i_seq, i_ts, b_marker = parse_rtp(byte_data)
                # 同一 rtp_ts 的多個封包屬於同一幀，只在該幀第一個封包印一次
                if i_ts == i_last_ts:
                    continue
                i_last_ts = i_ts
                f_abs = 'no-sr'
                if f_last_unixtime is not None:
                    # 當前tick數差 = 這次的tick - 上一次的tick 然後取正
                    i_diff = ((i_ts - i_last_rtp_ts + 2**31) % 2**32) - 2**31

                    # 絕對時間 = 上一次的 unix 時間緩衝 + 差異tick / clock_rate          
                    f_unixtime = f_last_unixtime + i_diff / i_rate                    
 
                print(f"seq={i_seq} rtp_ts(相對計數)={i_ts}  abs(絕對時間)={f_unixtime}")
    except KeyboardInterrupt:
        pass
    finally:
        o_client.close()


if __name__ == "__main__":
    main()
