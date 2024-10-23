import socket

# ตั้งค่าการเชื่อมต่อ
host = 'IP_ADDRESS_OF_SERVER'  # IP Address ของโน๊ตบุ๊คที่เป็น Server
port = 12345

# สร้าง socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# เชื่อมต่อไปยัง server
client_socket.connect((host, port))

# รับข้อมูลจาก server
data = client_socket.recv(1024).decode()
print('Received from server:', data)

# ปิดการเชื่อมต่อ
client_socket.close()
