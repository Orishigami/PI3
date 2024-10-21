from gpiozero import LED
from time import sleep
import datetime

# กำหนด LED ที่ขา GPIO 17
led = LED(17)

def main():
    try:
        while True:
            # แสดงเวลาปัจจุบัน
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"เวลาปัจจุบัน: {current_time}")
            
            # เปิด-ปิด LED
            print("เปิด LED")
            led.on()
            sleep(1)
            
            print("ปิด LED")
            led.off()
            sleep(1)
            
            print("-" * 20)  # แสดงเส้นคั่น
            
    except KeyboardInterrupt:
        print("\nปิดโปรแกรม")
        led.off()  # ปิด LED ก่อนจบโปรแกรม
        
if __name__ == "__main__":
    print("เริ่มต้นโปรแกรม Raspberry Pi Demo")
    print("กด Ctrl+C เพื่อปิดโปรแกรม")
    main()