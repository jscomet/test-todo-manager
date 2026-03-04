"""Task 数据模型"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TaskType(Enum):
    """任务类型"""
    CODER = "coder"
    REPAIR = "repair"
    PLANNER = "planner"

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "⏳ 待开始"
    EXECUTING = "🔄 进行中"
    COMPLETED = "✅ 已完成"
    FAILED = "❌ 失败"
    NEEDS_REVIEW = "👀 需审查"

@dataclass
class Task:
    """任务数据类"""
    id: str
    objective: str
    task_type: TaskType
    priority: str
    status: TaskStatus = TaskStatus.PENDING
    context: Dict[str, Any] = field(default_factory=dict)
    attempts: int = 0
    parent_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "objective": self.objective,
            "task_type": self.task_type.value,
            "priority": self.priority,
            "status": self.status.value,
            "context": self.context,
            "attempts": self.attempts,
            "parent_id": self.parent_id,
            "created_at": self.created_at,
            "completed_at": self.completed_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """从字典创建"""
        return cls(
            id=data["id"],
            objective=data["objective"],
            task_type=TaskType(data["task_type"]),
            priority=data["priority"],
            status=TaskStatus(data["status"]),
            context=data.get("context", {}),
            attempts=data.get("attempts", 0),
            parent_id=data.get("parent_id"),
            created_at=data["created_at"],
            completed_at=data.get("completed_at")
        )
