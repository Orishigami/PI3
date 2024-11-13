import RPi.GPIO as GPIO
import socket
import json
import time
from typing import Dict, Any

class TrafficLightController:
    def __init__(self, host: str, port: int):
        # GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # การกำหนดค่าเริ่มต้นสำหรับส่งไปยัง server
        self.config = {
            "camera_ids": {
                "A": 2,
                "B": 0,
                "C": 1,
                "D": 4
            },
            "direction_names": {
                "A": "North",
                "B": "East",
                "C": "South",
                "D": "West"
            },
            "direction_order": ["A", "B", "C", "D"],
            "green_durations": {
                "A": 10,
                "B": 15,
                "C": 10,
                "D": 15
            },
            "max_green_durations": {
                "A": 30,
                "B": 30,
                "C": 30,
                "D": 30
            }
        }
        
        # Traffic light pin configuration
        self.traffic_lights = {
            "A": {"RED": 4, "YELLOW": 3, "GREEN": 2},    # ทิศเหนือ
            "B": {"RED": 22, "YELLOW": 27, "GREEN": 17}, # ทิศตะวันออก
            "C": {"RED": 11, "YELLOW": 9, "GREEN": 10},   # ทิศใต้
            "D": {"RED": 13, "YELLOW": 6, "GREEN": 5}      # ตะวันตก
        }
        
        # Initialize GPIO pins
        self._setup_gpio()
        
        # Network configuration
        self.host = host
        self.port = port 
        self.socket = None
        self.is_running = False
    
    def _setup_gpio(self) -> None:
        """Initialize all GPIO pins as OUTPUT"""
        for direction in self.traffic_lights:
            for color, pin in self.traffic_lights[direction].items():
                try:
                    GPIO.setup(pin, GPIO.OUT)
                    GPIO.output(pin, GPIO.LOW)  # Ensure all lights start OFF
                except Exception as e:
                    print(f"Error setting up GPIO pin {pin}: {e}")
                    raise
    
    def _set_all_red_except(self, except_direction: str) -> None:
        """Set all directions to RED except the specified direction"""
        for direction in self.traffic_lights:
            if direction != except_direction:
                # Turn off all lights first
                for color in self.traffic_lights[direction]:
                    GPIO.output(self.traffic_lights[direction][color], GPIO.LOW)
                # Turn on RED light
                GPIO.output(self.traffic_lights[direction]["RED"], GPIO.HIGH)
    
    def set_traffic_light(self, direction: str, color: str) -> bool:
        """
        Control LED state for specified direction and color.
        If GREEN is set for any direction, all other directions will be set to RED.
        Returns: True if successful, False otherwise
        """
        try:
            if direction not in self.traffic_lights:
                print(f"Invalid direction: {direction}")
                return False
            
            if color not in self.traffic_lights[direction]:
                print(f"Invalid color: {color}")
                return False
            
            # If setting GREEN, set all other directions to RED first
            if color == "GREEN":
                self._set_all_red_except(direction)
            
            # Turn off all lights in this direction
            for clr in self.traffic_lights[direction]:
                GPIO.output(self.traffic_lights[direction][clr], GPIO.LOW)
            
            # Turn on requested light
            GPIO.output(self.traffic_lights[direction][color], GPIO.HIGH)
            
            print(f"Set {self.config['direction_names'][direction]} to {color}")
            return True
            
        except Exception as e:
            print(f"Error setting traffic light: {e}")
            return False
    
    def connect_and_send_config(self) -> bool:
        """Establish connection to the server and send configuration"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)  # 5 second timeout
            self.socket.connect((self.host, self.port))
            print(f"Connected to server {self.host}:{self.port}")
            
            # ส่งข้อมูล configuration ไปยัง server
            config_json = json.dumps(self.config)
            self.socket.send(config_json.encode())
            print("Sent configuration to server:")
            print(f"Camera IDs: {self.config['camera_ids']}")
            print(f"Direction names: {self.config['direction_names']}")
            print(f"Direction order: {self.config['direction_order']}")
            print(f"Green durations: {self.config['green_durations']}")
            print(f"Max green durations: {self.config['max_green_durations']}")
            
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def process_command(self, data: str) -> bool:
        """Process received command"""
        try:
            command = json.loads(data)
            if not isinstance(command, dict):
                print("Invalid command format")
                return False
            
            required_keys = {"direction", "color"}
            if not all(key in command for key in required_keys):
                print("Missing required keys in command")
                return False
            
            success = self.set_traffic_light(command["direction"], command["color"])
            return success
            
        except json.JSONDecodeError:
            print("Invalid JSON format")
            return False
        except Exception as e:
            print(f"Error processing command: {e}")
            return False
    
    def run(self) -> None:
        """Main loop to receive and process commands"""
        self.is_running = True
        reconnect_delay = 1  # Initial reconnect delay (seconds)
        
        while self.is_running:
            if not self.socket:
                if not self.connect_and_send_config():
                    time.sleep(reconnect_delay)
                    reconnect_delay = min(reconnect_delay * 2, 60)  # Exponential backoff
                    continue
                reconnect_delay = 1  # Reset delay after successful connection
            
            try:
                data = self.socket.recv(1024).decode()
                if not data:
                    print("Server disconnected")
                    self.socket.close()
                    self.socket = None
                    continue
                
                self.process_command(data)
                
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error in main loop: {e}")
                self.socket.close()
                self.socket = None
    
    def cleanup(self) -> None:
        """Clean up resources"""
        self.is_running = False
        if self.socket:
            self.socket.close()
        GPIO.cleanup()

def main():
    # กำหนด IP address ของ server
    HOST = '10.10.42.167'  # แก้ไขเป็น IP address ของ server
    PORT = 5000
    
    controller = TrafficLightController(HOST, PORT)
    
    try:
        controller.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        controller.cleanup()

if __name__ == "__main__":
    main()
