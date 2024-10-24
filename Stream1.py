from flask import Flask, Response
import cv2

app = Flask(__name__)

# เปิดกล้อง (0 หมายถึงกล้อง USB ตัวแรก)
camera = cv2.VideoCapture(0)

def generate_frames():
    while True:
        # อ่านภาพจากกล้อง
        success, frame = camera.read()
        if not success:
            break
        else:
            # ลดขนาดของเฟรมเพื่อลดภาระของระบบ
            frame = cv2.resize(frame, (640, 480))
            # เข้ารหัสภาพเป็น JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # ส่งภาพเป็นสตรีม MJPEG
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    # เรียกใช้ฟังก์ชัน generate_frames() เพื่อสตรีมวิดีโอ
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # รันเซิร์ฟเวอร์ Flask บนพอร์ต 5000
    app.run(host='0.0.0.0', port=5000)
