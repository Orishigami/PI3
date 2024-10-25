import RPi.GPIO as GPIO
import socket
import json
import time

# ตั้งค่า GPIO
GPIO.setmode(GPIO.BCM)

# กำหนดพินที่ใช้สำหรับไฟ LED
traffic_lights = {
    "A": {"RED": 4, "YELLOW": 3, "GREEN": 2},
    "B": {"RED": 22, "YELLOW": 27, "GREEN": 17},
    "C": {"RED": 11, "YELLOW": 9, "GREEN": 10}
}

# ตั้งค่า GPIO OUTPUT
for direction in traffic_lights:
    for color in traffic_lights[direction]:
        GPIO.setup(traffic_lights[direction][color], GPIO.OUT)

def set_traffic_light(direction, color):
    """ควบคุมไฟ LED ตามคำสั่งที่ได้รับ"""
    # ปิดไฟทั้งหมดในทิศทางนั้น
    for clr in traffic_lights[direction]:
        GPIO.output(traffic_lights[direction][clr], GPIO.LOW)
    # เปิดไฟตามสีที่กำหนด
    GPIO.output(traffic_lights[direction][color], GPIO.HIGH)

def main():
    # ตั้งค่าการเชื่อมต่อ
    HOST = '10.10.38.63'  # IP ของโน๊ตบุ๊ค
    PORT = 5000

    # สร้าง Socket Client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # เชื่อมต่อกับ Server
        client_socket.connect((HOST, PORT))
        print(f"Connected to server {HOST}:{PORT}")

        while True:
            # รับข้อมูลจาก Server
            data = client_socket.recv(1024).decode()
            if not data:
                break

            # แปลงข้อมูล JSON เป็น Dictionary
            command = json.loads(data)
            
            # ควบคุมไฟ LED
            direction = command["direction"]
            color = command["color"]
            set_traffic_light(direction, color)
            print(f"Set {direction} to {color}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        GPIO.cleanup()

if __name__ == "__main__":
    main()