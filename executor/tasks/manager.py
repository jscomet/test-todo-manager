"""任务管理器 - JSON 格式"""
import json
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent))

from core.task import Task, TaskStatus, TaskType


class TaskManager:
    """任务管理器 - 管理 tasks.json"""
    
    def __init__(self, tasks_file: str = "tasks/tasks.json"):
        self.tasks_file = Path(tasks_file)
        self._ensure_dir()
        self._tasks: List[Task] = []
        self._load()
    
    def _ensure_dir(self):
        """确保目录存在"""
        self.tasks_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _load(self):
        """从 JSON 加载任务"""
        if not self.tasks_file.exists():
            self._tasks = []
            return
        
        try:
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._tasks = []
            for task_data in data.get("tasks", []):
                task = self._dict_to_task(task_data)
                self._tasks.append(task)
                
        except Exception as e:
            print(f"⚠️ 加载任务失败: {e}")
            self._tasks = []
    
    def _save(self):
        """保存任务到 JSON"""
        data = {
            "version": "1.0",
            "updated_at": datetime.now().isoformat(),
            "tasks": [self._task_to_dict(t) for t in self._tasks]
        }
        
        with open(self.tasks_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _dict_to_task(self, data: Dict) -> Task:
        """字典转 Task 对象"""
        status_map = {
            "pending": TaskStatus.PENDING,
            "executing": TaskStatus.EXECUTING,
            "completed": TaskStatus.COMPLETED,
            "failed": TaskStatus.FAILED
        }
        
        type_map = {
            "coder": TaskType.CODER,
            "repair": TaskType.REPAIR,
            "planner": TaskType.PLANNER,
            "docs": TaskType.CODER
        }
        
        return Task(
            id=data["id"],
            objective=data["objective"],
            task_type=type_map.get(data.get("type", "coder"), TaskType.CODER),
            priority=data.get("priority", "🟡"),
            status=status_map.get(data.get("status", "pending"), TaskStatus.PENDING),
            context=data.get("context", {}),
            attempts=data.get("context", {}).get("attempts", 0)
        )
    
    def _task_to_dict(self, task: Task) -> Dict:
        """Task 对象转字典"""
        original = {}
        if self.tasks_file.exists():
            try:
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for t in data.get("tasks", []):
                    if t["id"] == task.id:
                        original = t
                        break
            except:
                pass
        
        status_str = {
            TaskStatus.PENDING: "pending",
            TaskStatus.EXECUTING: "executing",
            TaskStatus.COMPLETED: "completed",
            TaskStatus.FAILED: "failed"
        }.get(task.status, "pending")
        
        type_str = {
            TaskType.CODER: "coder",
            TaskType.REPAIR: "repair",
            TaskType.PLANNER: "planner"
        }.get(task.task_type, "coder")
        
        return {
            "id": task.id,
            "objective": task.objective,
            "type": type_str,
            "priority": task.priority,
            "status": status_str,
            "assignee": original.get("assignee", "AI"),
            "estimated_hours": original.get("estimated_hours"),
            "actual_hours": original.get("actual_hours"),
            "created_at": original.get("created_at"),
            "started_at": datetime.now().isoformat() if task.status == TaskStatus.EXECUTING else original.get("started_at"),
            "completed_at": datetime.now().isoformat() if task.status == TaskStatus.COMPLETED else original.get("completed_at"),
            "parent_id": original.get("parent_id"),
            "context": {**task.context, "attempts": task.attempts},
            "tags": original.get("tags", [])
        }
    
    def get_all(self) -> List[Task]:
        """获取所有任务"""
        return self._tasks.copy()
    
    def get_pending(self) -> List[Task]:
        """获取待处理任务"""
        return [t for t in self._tasks if t.status == TaskStatus.PENDING]
    
    def get_by_status(self, status: TaskStatus) -> List[Task]:
        """按状态获取任务"""
        return [t for t in self._tasks if t.status == status]
    
    def get_by_id(self, task_id: str) -> Optional[Task]:
        """按 ID 获取任务"""
        for t in self._tasks:
            if t.id == task_id:
                return t
        return None
    
    def add(self, task: Task) -> bool:
        """添加任务"""
        if self.get_by_id(task.id):
            print(f"⚠️ 任务 {task.id} 已存在")
            return False
        
        self._tasks.append(task)
        self._save()
        return True
    
    def update_status(self, task_id: str, status: TaskStatus) -> bool:
        """更新任务状态"""
        task = self.get_by_id(task_id)
        if not task:
            print(f"⚠️ 任务 {task_id} 不存在")
            return False
        
        task.status = status
        self._save()
        return True
    
    def update_task(self, task: Task) -> bool:
        """更新整个任务"""
        for i, t in enumerate(self._tasks):
            if t.id == task.id:
                self._tasks[i] = task
                self._save()
                return True
        return False
    
    def get_next(self) -> Optional[Task]:
        """获取下一个最高优先级待处理任务"""
        pending = self.get_pending()
        if not pending:
            return None
        
        priority_order = {"🔴": 0, "🟡": 1, "🟢": 2}
        pending.sort(key=lambda t: priority_order.get(t.priority, 3))
        
        return pending[0]
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        total = len(self._tasks)
        pending = len(self.get_pending())
        executing = len(self.get_by_status(TaskStatus.EXECUTING))
        completed = len(self.get_by_status(TaskStatus.COMPLETED))
        failed = len(self.get_by_status(TaskStatus.FAILED))
        
        return {
            "total": total,
            "pending": pending,
            "executing": executing,
            "completed": completed,
            "failed": failed,
            "progress": f"{completed}/{total} ({completed/total*100:.1f}%)" if total > 0 else "0%"
        }