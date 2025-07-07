#!/usr/bin/env python3
import socket
import time

def test_redis():
    print("开始连接Redis...")
    
    # 连接到Redis服务器
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 6379))
    print("连接成功！")
    
    # 发送10个SET命令
    start_time = time.time()

    count = 10000
    for i in range(count):
        # 构造RESP格式的SET命令
        cmd = f"*3\r\n$3\r\nSET\r\n$9\r\ntest_key{i%10}\r\n$11\r\ntest_value{i%10}\r\n"
        sock.send(cmd.encode())
        
        # 接收响应
        response = sock.recv(1024)
        # print(f"SET test_key{i}: {response.decode().strip()}")
    
    end_time = time.time()
    print(f"完成{count}个SET操作，耗时: {end_time - start_time:.2f}秒")
    
    sock.close()

if __name__ == "__main__":
    test_redis()

