"""
BabyAGI Executor - 极简 AI 执行器
"""

import time
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from core.queue import TaskQueue
from core.runner import ExecutionRunner
from config import load_config

def main():
    """主入口"""
    print("🚀 BabyAGI Executor 启动")
    
    # 加载配置
    config = load_config()
    
    # 初始化任务队列 (从 JSON 加载)
    tasks_path = Path(__file__).parent / "tasks" / "tasks.json"
    queue = TaskQueue(str(tasks_path))
    stats = queue.get_stats()
    print(f"📋 从 tasks.json 加载: {stats['pending']} 个待处理 / {stats['total']} 个总计")
    
    # 初始化执行器
    runner = ExecutionRunner(config, queue)
    
    # 启动主循环
    try:
        runner.run()
    except KeyboardInterrupt:
        print("\n👋 用户中断，保存状态...")
        runner.save_state()
        print("✅ 状态已保存，退出")

if __name__ == "__main__":
    main()
