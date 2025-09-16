#!/bin/bash

# 检查当前目录是否存在feishu-bot.py
if [ ! -f "feishu-bot.py" ]; then
    echo "错误：当前目录下未找到feishu-bot.py文件"
    echo "请确保脚本在与feishu-bot.py相同的目录中运行"
    exit 1
fi

# 查找并杀死现有进程
echo "查找正在运行的feishu-bot.py进程..."
PID=$(ps aux | grep feishu-bot.py | grep -v grep | awk '{print $2}')

if [ -z "$PID" ]; then
    echo "没有找到正在运行的feishu-bot.py进程"
else
    echo "找到进程PID: $PID, 正在杀死..."
    kill -9 $PID
    echo "进程已终止"
fi

# 激活虚拟环境并重启
echo "正在重启feishu-bot.py..."
source venv/bin/activate
nohup python feishu-bot.py > /tmp/feishu-bot.log 2>&1 &

# 检查是否启动成功
sleep 2
NEW_PID=$(ps aux | grep feishu-bot.py | grep -v grep | awk '{print $2}')

if [ -z "$NEW_PID" ]; then
    echo "启动失败，请检查日志: /tmp/feishu-bot.log"
    exit 1
else
    echo "启动成功，新进程PID: $NEW_PID"
    echo "日志输出到: /tmp/feishu-bot.log"
    echo ""
    echo "使用方法："
    echo "1. 查看日志: tail -f /tmp/feishu-bot.log"
    echo "2. 停止服务: kill $NEW_PID"
    echo "3. 重启服务: ./restart-feishu.sh"
fi