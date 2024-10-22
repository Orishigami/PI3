import RPi.GPIO as GPIO
import time
from typing import Dict

class TrafficLightController:
    def __init__(self, config: Dict):
        """
        กำหนดค่าเริ่มต้นสำหรับระบบไฟจราจร
        :param config: Dictionary ที่เก็บการกำหนดค่า GPIO pins สำหรับแต่ละทิศทางและสี
        """
        self.config = config
        self.setup_gpio()

    def setup_gpio(self):
        """ตั้งค่าเริ่มต้นสำหรับ GPIO pins"""
        # ใช้หมายเลข GPIO แทนหมายเลขขา
        GPIO.setmode(GPIO.BCM)
        # ตั้งค่าทุก pin เป็น output
        for direction in self.config:
            for color in self.config[direction]:
                pin = self.config[direction][color]
                GPIO.setup(pin, GPIO.OUT)
                # เริ่มต้นด้วยการปิดไฟทั้งหมด
                GPIO.output(pin, GPIO.LOW)

    def turn_on_light(self, direction: str, color: str):
        """
        เปิดไฟ LED ตามทิศทางและสีที่กำหนด
        :param direction: ทิศทาง (NORTH, SOUTH, EAST, WEST)
        :param color: สี (RED, YELLOW, GREEN)
        """
        pin = self.config[direction][color]
        GPIO.output(pin, GPIO.HIGH)

    def turn_off_light(self, direction: str, color: str):
        """
        ปิดไฟ LED ตามทิศทางและสีที่กำหนด
        :param direction: ทิศทาง (NORTH, SOUTH, EAST, WEST)
        :param color: สี (RED, YELLOW, GREEN)
        """
        pin = self.config[direction][color]
        GPIO.output(pin, GPIO.LOW)

    def turn_off_all(self):
        """ปิดไฟทั้งหมด"""
        for direction in self.config:
            for color in self.config[direction]:
                self.turn_off_light(direction, color)

    def run_traffic_cycle(self):
        """
        รันรอบไฟจราจรพื้นฐาน:
        - เหนือ/ใต้: เขียว -> เหลือง -> แดง
        - ตะวันออก/ตะวันตก: แดง -> เขียว -> เหลือง
        """
        try:
            while True:
                # เหนือ-ใต้ เขียว, ตะวันออก-ตะวันตก แดง
                print("เหนือ-ใต้: เขียว | ตะวันออก-ตะวันตก: แดง")
                self.turn_on_light("NORTH", "GREEN")
                self.turn_on_light("SOUTH", "GREEN")
                self.turn_on_light("EAST", "RED")
                self.turn_on_light("WEST", "RED")
                time.sleep(10)

                # เหนือ-ใต้ เหลือง
                print("เหนือ-ใต้: เหลือง")
                self.turn_off_light("NORTH", "GREEN")
                self.turn_off_light("SOUTH", "GREEN")
                self.turn_on_light("NORTH", "YELLOW")
                self.turn_on_light("SOUTH", "YELLOW")
                time.sleep(3)

                # เหนือ-ใต้ แดง, ตะวันออก-ตะวันตก เขียว
                print("เหนือ-ใต้: แดง | ตะวันออก-ตะวันตก: เขียว")
                self.turn_off_light("NORTH", "YELLOW")
                self.turn_off_light("SOUTH", "YELLOW")
                self.turn_on_light("NORTH", "RED")
                self.turn_on_light("SOUTH", "RED")
                self.turn_off_light("EAST", "RED")
                self.turn_off_light("WEST", "RED")
                self.turn_on_light("EAST", "GREEN")
                self.turn_on_light("WEST", "GREEN")
                time.sleep(10)

                # ตะวันออก-ตะวันตก เหลือง
                print("ตะวันออก-ตะวันตก: เหลือง")
                self.turn_off_light("EAST", "GREEN")
                self.turn_off_light("WEST", "GREEN")
                self.turn_on_light("EAST", "YELLOW")
                self.turn_on_light("WEST", "YELLOW")
                time.sleep(3)

                # กลับไปเริ่มรอบใหม่
                self.turn_off_all()

        except KeyboardInterrupt:
            print("\nปิดโปรแกรม")
            self.cleanup()

    def cleanup(self):
        """ทำความสะอาด GPIO และปิดโปรแกรม"""
        self.turn_off_all()
        GPIO.cleanup()

# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    traffic_lights = {
        "NORTH": {"RED": 2, "YELLOW": 3, "GREEN": 4},
        "SOUTH": {"RED": 17, "YELLOW": 21, "GREEN": 22},
        "EAST": {"RED": 10, "YELLOW": 9, "GREEN": 11},
        "WEST": {"RED": 5, "YELLOW": 6, "GREEN": 13}
    }
    
    controller = TrafficLightController(traffic_lights)
    try:
        controller.run_traffic_cycle()
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        controller.cleanup()