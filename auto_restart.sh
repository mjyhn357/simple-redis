#!/bin/bash
echo "开始监控文件变化..."

while true; do
    echo "等待文件修改..."
    inotifywait -e modify *.py
    
    echo "检测到文件变化，重启服务器..."
    
    # 停止旧的服务器
    pkill -f redis-server
    sleep 2
    
    # 启动新的服务器
    python redis-server.py > logs/redis.log 2>&1 &
    echo "服务器已重启"
done
