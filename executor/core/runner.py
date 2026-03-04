"""执行引擎 - BabyAGI 核心循环"""
import time
from datetime import datetime
from typing import Optional
from .task import Task, TaskStatus
from .queue import TaskQueue

class ExecutionRunner:
    """执行引擎"""
    
    def __init__(self, config: dict, queue: TaskQueue):
        self.config = config
        self.queue = queue
        self.iteration = 0
        self.running = False
    
    def run(self):
        """主循环"""
        self.running = True
        
        while self.running:
            self.iteration += 1
            print(f"\n{'='*60}")
            print(f"🔄 第 {self.iteration} 轮执行")
            print(f"{'='*60}")
            
            # 1. 获取任务
            task = self.queue.get_next()
            
            if not task:
                print("✨ 所有任务完成！")
                break
            
            print(f"📝 任务: [{task.priority}] {task.objective[:50]}...")
            
            # 2. 执行
            result = self._execute_task(task)
            
            # 3. 处理结果
            if result:
                self._handle_success(task)
            else:
                self._handle_failure(task)
            
            # 4. 休眠
            interval = self.config.get("executor", {}).get("poll_interval", 5)
            print(f"⏳ 等待 {interval} 秒...")
            time.sleep(interval)
    
    def _execute_task(self, task: Task) -> bool:
        """执行单个任务"""
        # TODO: 调用 OpenCode
        print(f"🤖 调用 OpenCode 执行任务...")
        return True  # 占位
    
    def _handle_success(self, task: Task):
        """处理成功"""
        print("✅ 任务完成")
        self.queue.update_status(task.id, TaskStatus.COMPLETED)
    
    def _handle_failure(self, task: Task):
        """处理失败"""
        print("❌ 任务失败")
        task.attempts += 1
        
        max_attempts = self.config.get("executor", {}).get("max_attempts", 3)
        
        if task.attempts < max_attempts:
            print(f"   将在下一轮重试 ({task.attempts}/{max_attempts})")
        else:
            print(f"   超过最大重试次数，标记为失败")
            self.queue.update_status(task.id, TaskStatus.FAILED)
    
    def save_state(self):
        """保存状态"""
        # TODO: 实现状态保存
        pass
