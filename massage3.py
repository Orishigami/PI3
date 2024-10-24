import RPi.GPIO as GPIO
import socket
import time

# ตั้งค่า GPIO ใช้หมายเลขพินแบบ BCM
GPIO.setmode(GPIO.BCM)

# กำหนดพินที่ใช้สำหรับไฟ LED ของแต่ละทิศทาง
traffic_lights = {
    "NORTH": {"RED": 4, "YELLOW": 3, "GREEN": 2},
    "SOUTH": {"RED": 22, "YELLOW": 27, "GREEN": 17},
    "EAST": {"RED": 11, "YELLOW": 9, "GREEN": 10},
    "WEST": {"RED": 13, "YELLOW": 6, "GREEN": 5}
}

# ตั้งค่าพินทุกตัวเป็น OUTPUT
for direction in traffic_lights:
    for color in traffic_lights[direction]:
        GPIO.setup(traffic_lights[direction][color], GPIO.OUT)

# กำหนดข้อมูลไคลเอนต์
SERVER_IP = '10.10.38.63'  # IP ของเซิร์ฟเวอร์
SERVER_PORT = 12345

def set_traffic_light(direction, color):
    for clr in traffic_lights[direction]:
        GPIO.output(traffic_lights[direction][clr], GPIO.LOW)
    GPIO.output(traffic_lights[direction][color], GPIO.HIGH)

def turn_all_red():
    for direction in traffic_lights:
        set_traffic_light(direction, "RED")

def main():
    try:
        # สร้าง socket สำหรับไคลเอนต์และเชื่อมต่อกับเซิร์ฟเวอร์
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, SERVER_PORT))
        print(f"Connected to server at {SERVER_IP}:{SERVER_PORT}")

        while True:
            # รอข้อมูลจากเซิร์ฟเวอร์เพื่อเปลี่ยนไฟ
            data = client_socket.recv(1024).decode()
            if data:
                parts = data.split()
                direction = parts[0]
                command = parts[1]
                yellow_duration = float(parts[2])
                all_red_duration = float(parts[3])

                if command == "skip_next":
                    print(f"Received skip signal for {direction}. Skipping to next direction.")
                    continue
                elif command == "normal_duration":
                    print(f"Received normal duration for {direction}. Setting green light.")
                    set_traffic_light(direction, "GREEN")
                    time.sleep(green_durations[direction])
                
                set_traffic_light(direction, "YELLOW")
                time.sleep(yellow_duration)

                turn_all_red()
                time.sleep(all_red_duration)

    except KeyboardInterrupt:
        pass
    finally:
        client_socket.close()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
