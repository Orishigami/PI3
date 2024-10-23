import socket
import json
import RPi.GPIO as GPIO
import time

# ตั้งค่า GPIO
GPIO.setmode(GPIO.BCM)  # ใช้หมายเลขพินแบบ BCM

# กำหนดพินที่ใช้สำหรับไฟ LED ของแต่ละทิศทาง
traffic_lights = {
    "NORTH": {"RED": 4, "YELLOW": 3, "GREEN": 2},
    "SOUTH": {"RED": 22, "YELLOW": 27, "GREEN": 17},
    "EAST": {"RED": 11, "YELLOW": 9, "GREEN": 10},
    "WEST": {"RED": 13, "YELLOW": 6, "GREEN": 5}
}

# ตั้งค่าพินเป็น OUTPUT
for direction in traffic_lights:
    for color in traffic_lights[direction]:
        GPIO.setup(traffic_lights[direction][color], GPIO.OUT)

# กำหนดระยะเวลาไฟเหลืองและไฟแดง
YELLOW_DURATION = 3
ALL_RED_DURATION = 1.5

# กำหนดระยะเวลาไฟเขียวพื้นฐานและสูงสุดของแต่ละทิศ
green_durations = {
    "NORTH": 15,
    "SOUTH": 12,
    "EAST": 10,
    "WEST": 18
}

max_green_durations = {
    "NORTH": 20,
    "SOUTH": 20,
    "EAST": 20,
    "WEST": 20
}

# ลำดับการปล่อยไฟจราจร
custom_direction_order = ["NORTH", "EAST", "SOUTH", "WEST"]

# กำหนดจำนวนรถเริ่มต้นในแต่ละทิศ
car_counts = {}

def set_traffic_light(direction, color):
    # ปิดไฟทั้งหมดก่อนในทิศทางนั้น
    for clr in traffic_lights[direction]:
        GPIO.output(traffic_lights[direction][clr], GPIO.LOW)
    # เปิดไฟตามสีที่กำหนด
    GPIO.output(traffic_lights[direction][color], GPIO.HIGH)

def turn_all_red():
    # เปิดไฟแดงทุกทิศ (ใช้ในกรณีที่ต้องการทำให้ทุกทิศหยุดพร้อมกัน)
    for direction in traffic_lights:
        set_traffic_light(direction, "RED")

def print_car_counts():
    # ฟังก์ชันเพื่อปริ้นจำนวนรถในแต่ละทิศ
    print("Current car counts:")
    for direction, count in car_counts.items():
        print(f"{direction}: {count} cars")
    print("-" * 30)

def print_traffic_light_status(direction, light):
    # ฟังก์ชันเพื่อปริ้นสถานะของไฟจราจรในทิศทางปัจจุบัน
    print(f"Traffic light status: Direction = {direction}, Light = {light}")

def receive_data_from_server():
    # ตั้งค่าการเชื่อมต่อ
    host = '10.10.38.63'  # IP Address ของโน๊ตบุ๊คที่เป็น Server
    port = 12345

    # สร้าง socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # เชื่อมต่อไปยัง server
    client_socket.connect((host, port))
    
    try:
        while True:
            # รับข้อมูลจาก server
            data = client_socket.recv(1024).decode()
            if not data:
                break
            server_car_counts = json.loads(data)
            for direction in server_car_counts.keys():
                car_counts[direction] = server_car_counts.get(direction, car_counts.get(direction, 0))
    finally:
        # ปิดการเชื่อมต่อ
        client_socket.close()

def main():
    try:
        current_direction_index = 0
        current_direction = custom_direction_order[current_direction_index]
        current_light = "GREEN"
        light_start_time = time.time()
        last_update_time = time.time()
        last_car_decrease_time = time.time()

        # แสดงสถานะไฟเริ่มต้น
        print_traffic_light_status(current_direction, current_light)
        set_traffic_light(current_direction, "GREEN")

        while True:
            elapsed = time.time() - light_start_time

            if current_light == "GREEN":
                if car_counts.get(current_direction, 0) == 0 or elapsed > max_green_durations[current_direction]:
                    current_light = "YELLOW"
                    set_traffic_light(current_direction, "YELLOW")
                    light_start_time = time.time()
                    print_traffic_light_status(current_direction, current_light)
                elif elapsed > green_durations[current_direction]:
                    pass  # ปล่อยไฟเขียวจนกว่าจะครบเวลาสูงสุด

            elif current_light == "YELLOW" and elapsed > YELLOW_DURATION:
                current_light = "RED"
                turn_all_red()  # เปิดไฟแดงทุกทิศ
                light_start_time = time.time()
                print_traffic_light_status(current_direction, current_light)
            elif current_light == "RED" and elapsed > ALL_RED_DURATION:
                while True:
                    current_direction_index = (current_direction_index + 1) % len(custom_direction_order)
                    current_direction = custom_direction_order[current_direction_index]
                    if car_counts.get(current_direction, 0) > 0:
                        break
                current_light = "GREEN"
                set_traffic_light(current_direction, "GREEN")
                light_start_time = time.time()
                print_traffic_light_status(current_direction, current_light)

            # รับข้อมูลจาก server ทุกๆ 1 วินาที
            if time.time() - last_update_time > 1:
                receive_data_from_server()
                last_update_time = time.time()
                # ปริ้นจำนวนรถเมื่อมีการอัปเดต
                print_car_counts()

            # ลดจำนวนรถในทิศที่มีสัญญาณไฟเป็นสีเขียวหรือสีเหลืองทุกๆ วินาที
            if time.time() - last_car_decrease_time > 1:
                if current_light in ["GREEN", "YELLOW"]:
                    car_counts[current_direction] = max(0, car_counts.get(current_direction, 0) - 1)
                    # ปริ้นจำนวนรถเมื่อมีการลด
                    print_car_counts()
                last_car_decrease_time = time.time()

            time.sleep(0.1)  # ลดการใช้งาน CPU

    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
