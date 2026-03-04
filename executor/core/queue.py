"""任务队列管理"""
import sys
from pathlib import Path
from typing import List, Optional

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.task import Task, TaskStatus, TaskType

# 延迟导入避免循环依赖
def get_task_manager():
    from tasks import TaskManager
    return TaskManager


class TaskQueue:
    """任务队列 - 基于 JSON 文件"""
    
    def __init__(self, tasks_file: str = "tasks/tasks.json"):
        TaskManager = get_task_manager()
        self.manager = TaskManager(tasks_file)
    
    def get_next(self) -> Optional[Task]:
        """获取下一个最高优先级任务"""
        return self.manager.get_next()
    
    def add(self, task: Task):
        """添加任务"""
        self.manager.add(task)
    
    def update_status(self, task_id: str, status: TaskStatus):
        """更新任务状态"""
        self.manager.update_status(task_id, status)
    
    def get_stats(self) -> dict:
        """获取统计"""
        return self.manager.get_stats()
