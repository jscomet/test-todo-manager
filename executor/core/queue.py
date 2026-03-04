"""任务队列管理"""
import re
from pathlib import Path
from typing import List, Optional
from .task import Task, TaskStatus

class TaskQueue:
    """任务队列"""
    
    def __init__(self, plan_file: str):
        self.plan_file = Path(plan_file)
        self.tasks: List[Task] = []
        self._load_from_plan()
    
    def _load_from_plan(self):
        """从 PLAN.md 加载任务"""
        if not self.plan_file.exists():
            return
        
        content = self.plan_file.read_text(encoding='utf-8')
        
        # 解析任务表格
        # 格式: | 优先级 | 开发任务 | 状态 | ... |
        task_pattern = r'\|\s*([🔴🟡🟢])\s*\|\s*([^|]+?)\s*\|\s*(⏳|🔄|✅|❌)'
        matches = re.findall(task_pattern, content)
        
        for idx, (priority, objective, status_str) in enumerate(matches, 1):
            status_map = {
                "⏳": TaskStatus.PENDING,
                "🔄": TaskStatus.EXECUTING,
                "✅": TaskStatus.COMPLETED,
                "❌": TaskStatus.FAILED
            }
            
            task = Task(
                id=f"task-{idx:03d}",
                objective=objective.strip(),
                task_type=self._infer_task_type(objective),
                priority=priority,
                status=status_map.get(status_str, TaskStatus.PENDING)
            )
            
            # 只加载待开始的任务
            if task.status == TaskStatus.PENDING:
                self.tasks.append(task)
    
    def _infer_task_type(self, objective: str) -> str:
        """推断任务类型"""
        obj_lower = objective.lower()
        if "修复" in objective or "fix" in obj_lower:
            return "repair"
        elif "分解" in objective or "plan" in obj_lower:
            return "planner"
        else:
            return "coder"
    
    def get_next(self) -> Optional[Task]:
        """获取下一个最高优先级任务"""
        pending = [t for t in self.tasks if t.status == TaskStatus.PENDING]
        
        if not pending:
            return None
        
        # 按优先级排序
        priority_order = {"🔴": 0, "🟡": 1, "🟢": 2}
        pending.sort(key=lambda t: priority_order.get(t.priority, 3))
        
        return pending[0]
    
    def add(self, task: Task):
        """添加任务"""
        self.tasks.append(task)
    
    def update_status(self, task_id: str, status: TaskStatus):
        """更新任务状态"""
        for task in self.tasks:
            if task.id == task_id:
                task.status = status
                break
