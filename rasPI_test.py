from gpiozero import LED
from time import sleep
import datetime

# กำหนด LED ที่ขา GPIO 17
led = LED(2)

def main():
    try:
        while True:
            # แสดงเวลาปัจจุบัน
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"Current time: {current_time}")
            
            # เปิด-ปิด LED
            print("Turning on LED")
            led.on()
            sleep(1)
            
            print("Turning off LED")
            led.off()
            sleep(1)
            
            print("-" * 20)  # แสดงเส้นคั่น
            
    except KeyboardInterrupt:
        print("\nExiting program")
        led.off()  # ปิด LED ก่อนจบโปรแกรม
        
if __name__ == "__main__":
    print("Starting Raspberry Pi Demo")
    print("Press Ctrl+C to exit the program")
    main()
