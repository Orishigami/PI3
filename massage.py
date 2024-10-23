import socket

# ตั้งค่าการเชื่อมต่อ
host = '0.0.0.0'  # ฟังทุก IP ที่เชื่อมต่อเข้ามา
port = 12345

# สร้าง socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# ผูก socket กับ IP และ port
server_socket.bind((host, port))

# เริ่มฟังการเชื่อมต่อ
server_socket.listen(5)

print('Server listening on port', port)

while True:
    # รอการเชื่อมต่อ
    client_socket, addr = server_socket.accept()
    print('Connection from', addr)

    # รับข้อมูล
    data = client_socket.recv(1024).decode()
    print('Received from client:', data)

    # ปิดการเชื่อมต่อ
    client_socket.close()
