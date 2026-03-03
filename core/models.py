"""核心数据模型

定义任务管理器的数据结构和枚举类型。
符合 SPEC.md 第 3 章数据模型规范。
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List
from enum import Enum


class Priority(Enum):
    """任务优先级枚举
    
    符合 SPEC 3.2 规范:
    - HIGH = "高" (🔴 红色)
    - MEDIUM = "中" (🟡 黄色)
    - LOW = "低" (🟢 绿色)
    """
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"
    
    def __str__(self) -> str:
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> "Priority":
        """从字符串创建优先级"""
        mapping = {
            "高": cls.HIGH,
            "中": cls.MEDIUM,
            "低": cls.LOW,
        }
        return mapping.get(value, cls.MEDIUM)


@dataclass
class Task:
    """任务数据类
    
    符合 SPEC 3.1 规范:
    - id: 唯一标识，从1递增
    - content: 任务内容，长度限制 1-200字符
    - done: 完成状态
    - priority: 优先级
    - created_at: ISO格式时间戳
    - completed_at: 完成时间（可选）
    - due_date: 截止日期 YYYY-MM-DD（可选）
    - tags: 标签列表（可选）
    - is_test: 是否测试任务
    """
    
    id: int
    content: str
    done: bool = False
    priority: Priority = field(default_factory=lambda: Priority.MEDIUM)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    due_date: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    is_test: bool = False
    
    def __post_init__(self):
        """初始化后验证"""
        # 确保 content 是字符串
        if not isinstance(self.content, str):
            self.content = str(self.content)
        
        # 确保 content 不为空
        self.content = self.content.strip()
        if not self.content:
            raise ValueError("任务内容不能为空")
        
        # 限制内容长度
        if len(self.content) > 200:
            self.content = self.content[:197] + "..."
        
        # 确保 priority 是 Priority 类型
        if isinstance(self.priority, str):
            self.priority = Priority.from_string(self.priority)
        
        # 确保 tags 是列表
        if self.tags is None:
            self.tags = []
    
    def to_dict(self) -> dict:
        """转换为字典（用于 JSON 序列化）"""
        data = asdict(self)
        # 将 Priority 枚举转换为字符串
        data["priority"] = self.priority.value
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """从字典恢复（用于 JSON 反序列化）"""
        # 处理优先级字段
        if "priority" in data:
            if isinstance(data["priority"], str):
                data["priority"] = Priority.from_string(data["priority"])
        
        # 移除多余的字段（向后兼容）
        valid_fields = {"id", "content", "done", "priority", 
                       "created_at", "completed_at", "due_date", 
                       "tags", "is_test"}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        return cls(**filtered_data)
    
    def mark_done(self) -> None:
        """标记任务为完成"""
        self.done = True
        self.completed_at = datetime.now().isoformat()
    
    def mark_undone(self) -> None:
        """标记任务为未完成"""
        self.done = False
        self.completed_at = None
    
    def add_tag(self, tag: str) -> None:
        """添加标签"""
        tag = tag.strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str) -> None:
        """移除标签"""
        if tag in self.tags:
            self.tags.remove(tag)
    
    def set_priority(self, priority: Priority) -> None:
        """设置优先级"""
        self.priority = priority
    
    def set_due_date(self, due_date: Optional[str]) -> None:
        """设置截止日期"""
        self.due_date = due_date
    
    @property
    def status_icon(self) -> str:
        """状态图标"""
        return "✅" if self.done else "⭕"
    
    @property
    def priority_icon(self) -> str:
        """优先级图标"""
        icons = {
            Priority.HIGH: "🔴",
            Priority.MEDIUM: "🟡",
            Priority.LOW: "🟢",
        }
        return icons.get(self.priority, "🟡")
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.status_icon} [{self.id}] {self.priority_icon} {self.content}"
    
    def __repr__(self) -> str:
        """详细表示"""
        return (f"Task(id={self.id}, content='{self.content[:30]}...', "
                f"done={self.done}, priority={self.priority.value})")
