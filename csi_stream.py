from flask import Flask, Response
import cv2
import subprocess

app = Flask(__name__)

def generate_frames():
    # เปิด libcamera-vid ผ่าน subprocess
    command = [
        'libcamera-vid', '-t', '0', '--inline', '--width', '640', '--height', '480',
        '--framerate', '24', '-o', '-'
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)

    while True:
        # อ่านข้อมูลจาก stdout ของ subprocess
        frame = process.stdout.read(640 * 480 * 3)
        if not frame:
            break

        # ใช้ OpenCV เพื่อเข้ารหัสเป็น JPEG
        img = cv2.imdecode(np.frombuffer(frame, dtype=np.uint8), cv2.IMREAD_COLOR)
        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
