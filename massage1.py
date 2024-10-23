import socket

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
        print('Received from server:', data)
finally:
    # ปิดการเชื่อมต่อ
    client_socket.close()
