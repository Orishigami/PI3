from flask import Flask, Response
from picamera import PiCamera
from time import sleep
import io

app = Flask(__name__)

# ตั้งค่ากล้อง CSI
camera = PiCamera()
camera.resolution = (640, 480)  # กำหนดความละเอียดของภาพ
camera.framerate = 24  # กำหนดอัตราเฟรม

def generate_frames():
    with camera as cam:
        # เปิดสตรีมวิดีโอ
        cam.start_preview()
        sleep(2)  # รอให้กล้องเตรียมพร้อม

        stream = io.BytesIO()
        for _ in cam.capture_continuous(stream, format='jpeg', use_video_port=True):
            # รีเซ็ต stream ก่อนบันทึกข้อมูลใหม่
            stream.seek(0)
            frame = stream.read()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            # ล้าง stream สำหรับการจับภาพครั้งถัดไป
            stream.seek(0)
            stream.truncate()

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
