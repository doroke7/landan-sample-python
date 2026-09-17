import cv2

rtsp_url = "rtsp://192.168.254.101:8554/live"

cap = cv2.VideoCapture(rtsp_url)

ret, frame = cap.read()

if ret:
    cv2.imwrite("snapshot.jpg", frame)
    print("saved snapshot.jpg")
else:
    print("failed to read frame")

cap.release()