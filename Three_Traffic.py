import RPi.GPIO as GPIO
import time

# ตั้งค่า GPIO
GPIO.setmode(GPIO.BCM)  # ใช้หมายเลขพินแบบ BCM

# กำหนดพินที่ใช้สำหรับไฟ LED ของแต่ละฝั่ง
traffic_lights = {
    "A": {"RED": 4, "YELLOW": 3, "GREEN": 2},
    "B": {"RED": 22, "YELLOW": 27, "GREEN": 17},
    "C": {"RED": 11, "YELLOW": 9, "GREEN": 10},
}

# ตั้งค่าพินเป็น OUTPUT
for direction in traffic_lights:
    for color in traffic_lights[direction]:
        GPIO.setup(traffic_lights[direction][color], GPIO.OUT)

# ตัวแปรสำหรับระยะเวลาไฟแต่ละสี
initial_green_duration = {
    "A": 10,
    "B": 12,
    "C": 8,
}

YELLOW_DURATION = 3
ALL_RED_DURATION = 1.5

def set_traffic_light(direction, color):
    # ปิดไฟทั้งหมดก่อนในฝั่งนั้น
    for clr in traffic_lights[direction]:
        GPIO.output(traffic_lights[direction][clr], GPIO.LOW)
    # เปิดไฟตามสีที่กำหนด
    GPIO.output(traffic_lights[direction][color], GPIO.HIGH)

def turn_all_red():
    # เปิดไฟแดงทุกฝั่ง (ใช้ในกรณีที่ต้องการทำให้ทุกฝั่งหยุดพร้อมกัน)
    for direction in traffic_lights:
        set_traffic_light(direction, "RED")

def cycle_traffic_lights():
    try:
        # วนลำดับการปล่อยไฟในลำดับ A -> B -> C
        custom_direction_order = ["A", "B", "C"]
        current_direction_index = 0

        while True:
            current_direction = custom_direction_order[current_direction_index]
            green_time = initial_green_duration[current_direction]
            
            # ตั้งค่าไฟแดงให้กับทุกฝั่งก่อน
            for direction in custom_direction_order:
                if direction != current_direction:
                    set_traffic_light(direction, "RED")

            # แสดงไฟเขียวในฝั่งปัจจุบัน
            set_traffic_light(current_direction, "GREEN")
            print(f"ฝั่ง {current_direction}: ไฟเขียว {green_time} วินาที")
            time.sleep(green_time)  # รอเป็นเวลาตามที่กำหนด

            # เปลี่ยนเป็นไฟเหลือง
            set_traffic_light(current_direction, "YELLOW")
            print(f"ฝั่ง {current_direction}: ไฟเหลือง {YELLOW_DURATION} วินาที")
            time.sleep(YELLOW_DURATION)  # รอ 3 วินาที

            # เปิดไฟแดงในทุกฝั่ง
            turn_all_red()
            print("ทุกฝั่ง: ไฟแดง")
            time.sleep(ALL_RED_DURATION)  # รอเป็นระยะเวลาที่กำหนด

            # เปลี่ยนไปฝั่งถัดไป
            current_direction_index = (current_direction_index + 1) % len(custom_direction_order)

    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    cycle_traffic_lights()
