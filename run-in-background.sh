#!/bin/bash
# run-in-background.sh - 后台运行 BabyAGI 执行器

PROJECT_DIR="/root/.openclaw/workspace/test/todo-manager"
LOG_FILE="$PROJECT_DIR/runtime.log"
PID_FILE="$PROJECT_DIR/executor.pid"

cd "$PROJECT_DIR"

# 清理可能存在的锁文件
rm -f /tmp/babyagi-executor.lock

# 启动执行器并将输出重定向到日志文件
./executor.sh >> "$LOG_FILE" 2>&1 &
PID=$!

# 保存进程ID
echo $PID > "$PID_FILE"

echo "✅ BabyAGI 执行器已启动"
echo "进程ID: $PID"
echo "日志文件: $LOG_FILE"
echo "PID文件: $PID_FILE"
echo ""
echo "查看实时日志: tail -f $LOG_FILE"
echo "停止执行: kill $PID"
