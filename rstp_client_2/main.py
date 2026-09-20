"""
RTSP 截圖：用 PyAV (pip install av) 收流、解碼，每隔幾秒存一張，檔名 = 這張圖的時間。

用法
    python main.py rtsp://localhost:8554/mystream                 # 每 1 秒存一張到 ./shots
    python main.py rtsp://localhost:8554/mystream --interval 5    # 每 5 秒一張
    python main.py rtsp://localhost:8554/mystream --interval 0    # 每一幀都存

檔名： 20260920_171530_123.jpg  = 本機時間 17:15:30.123

時間怎麼來的
    use_wallclock_as_timestamps=1 讓 ffmpeg 收到每個封包時，就把「本機牆上時間」蓋在 pts 上。
    所以 frame.time (= pts * time_base) 就是收到這一幀的 Unix 時間。

    這是「本機收到的時間」，不是來源端拍下的時間；差距 = 網路傳輸 + 來源端編碼延遲。
    要來源端的時間 (RTCP SR 的 NTP)，PyAV 拿不到，得自己解 RTP，見 ../rstp_client/main.py。
"""
import argparse
import os
from datetime import datetime

import av


def main():
    o_argument_parser = argparse.ArgumentParser()
    o_argument_parser.add_argument("url")
    o_argument_parser.add_argument("--interval", type=float, default=1.0, help="每幾秒存一張，0 = 每一幀都存")
    o_argument_parser.add_argument("--out-dir", default="shots", help="圖片輸出資料夾")
    o_argument_parser.add_argument("--count", type=int, default=0, help="存幾張就結束，0 = 一直存")
    o_args = o_argument_parser.parse_args()
    os.makedirs(o_args.out_dir, exist_ok=True)

    d_options = {
        "rtsp_transport": "tcp",  # 走 TCP，不掉包
        "use_wallclock_as_timestamps": "1",  # pts 直接用收到封包當下的本機時間
    }
    o_container = av.open(o_args.url, options=d_options, timeout=10)

    f_last_saved = None
    i_saved = 0
    try:
        for o_frame in o_container.decode(video=0):
            f_unixtime = float(o_frame.time)  # 這一幀的 Unix 時間 (秒)

            if f_last_saved is not None and f_unixtime - f_last_saved < o_args.interval:
                continue

            o_dt = datetime.fromtimestamp(f_unixtime)
            s_stamp = o_dt.strftime("%Y%m%d_%H%M%S")
            i_ms = o_dt.microsecond // 1000
            s_path = os.path.join(o_args.out_dir, f"{s_stamp}_{i_ms:03d}.jpg")

            o_image = o_frame.to_image()
            o_image.save(s_path)
            print(f"[SHOT] {s_path}  unixtime(時間)={f_unixtime}")

            f_last_saved = f_unixtime
            i_saved += 1
            if o_args.count and i_saved >= o_args.count:
                break
    except KeyboardInterrupt:
        pass
    finally:
        o_container.close()
        print(f"共存 {i_saved} 張，資料夾：{o_args.out_dir}")


if __name__ == "__main__":
    main()
