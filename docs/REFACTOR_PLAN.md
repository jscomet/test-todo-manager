# Todo Manager 结构优化方案

## 目标
1. 分离真实任务与测试任务
2. 拆分 monolithic 的 todo.py
3. 添加测试任务自动清理机制
4. 提高可维护性和可扩展性

---

## 目录结构重构

```
todo-manager/
├── todo.py                    # 入口文件（精简至 ~100 行）
├── config.py                  # 配置文件
├── core/                      # 核心模块
│   ├── __init__.py
│   ├── models.py              # 数据模型（Task 类）
│   ├── storage.py             # 存储抽象层
│   └── exceptions.py          # 自定义异常
├── commands/                  # 命令模块
│   ├── __init__.py
│   ├── base.py                # 命令基类
│   ├── task_commands.py       # 任务增删改查
│   ├── tag_commands.py        # 标签管理
│   ├── export_commands.py     # 导出功能
│   └── query_commands.py      # 查询统计
├── services/                  # 业务逻辑层
│   ├── __init__.py
│   ├── task_service.py        # 任务服务
│   ├── filter_service.py      # 过滤服务
│   └── export_service.py      # 导出服务
├── data/                      # 数据目录
│   ├── tasks.json             # 真实任务
│   └── test-tasks.json        # 测试任务（隔离）
├── tests/                     # 测试目录
│   ├── __init__.py
│   ├── conftest.py            # pytest 配置
│   ├── unit/                  # 单元测试
│   ├── integration/           # 集成测试
│   └── fixtures/              # 测试数据
├── executor/                  # BabyAGI 执行器
│   ├── __init__.py
│   ├── runner.py              # 执行逻辑
│   ├── task_parser.py         # 任务解析（修复bug）
│   └── cleanup.py             # 清理工具
└── utils/                     # 工具函数
    ├── __init__.py
    ├── cli_utils.py           # CLI 辅助
    └── validators.py          # 数据验证
```

---

## 关键修改点

### 1. 数据模型化 (core/models.py)

```python
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List
from enum import Enum

class Priority(Enum):
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"

@dataclass
class Task:
    id: int
    content: str
    done: bool = False
    priority: Priority = Priority.MEDIUM
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    due_date: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    is_test: bool = False  # 区分测试任务
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        # 处理枚举转换
        if isinstance(data.get("priority"), str):
            data["priority"] = Priority(data["priority"])
        return cls(**data)
```

### 2. 存储层抽象 (core/storage.py)

```python
from abc import ABC, abstractmethod
from typing import List
from .models import Task
import json
import os

class Storage(ABC):
    @abstractmethod
    def load(self) -> List[Task]: ...
    
    @abstractmethod
    def save(self, tasks: List[Task]) -> None: ...
    
    @abstractmethod
    def clear_test_tasks(self) -> int: ...  # 返回清理数量

class JSONStorage(Storage):
    def __init__(self, filepath: str, separate_test: bool = True):
        self.filepath = filepath
        self.test_filepath = filepath.replace(".json", "-test.json")
        self.separate_test = separate_test
    
    def load(self) -> List[Task]:
        tasks = []
        # 加载真实任务
        if os.path.exists(self.filepath):
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                tasks.extend([Task.from_dict(t) for t in data])
        # 加载测试任务
        if self.separate_test and os.path.exists(self.test_filepath):
            with open(self.test_filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                test_tasks = [Task.from_dict(t) for t in data]
                for t in test_tasks:
                    t.is_test = True
                tasks.extend(test_tasks)
        return tasks
    
    def save(self, tasks: List[Task]) -> None:
        real_tasks = [t.to_dict() for t in tasks if not t.is_test]
        test_tasks = [t.to_dict() for t in tasks if t.is_test]
        
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(real_tasks, f, ensure_ascii=False, indent=2)
        
        if self.separate_test:
            with open(self.test_filepath, "w", encoding="utf-8") as f:
                json.dump(test_tasks, f, ensure_ascii=False, indent=2)
    
    def clear_test_tasks(self) -> int:
        """清理测试任务，返回清理数量"""
        tasks = self.load()
        test_count = sum(1 for t in tasks if t.is_test)
        if test_count > 0 and os.path.exists(self.test_filepath):
            os.remove(self.test_filepath)
        return test_count
```

### 3. 命令模式重构 (commands/base.py)

```python
from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace
from typing import Optional

class Command(ABC):
    name: str
    help: str
    
    @abstractmethod
    def add_arguments(self, parser: ArgumentParser) -> None: ...
    
    @abstractmethod
    def execute(self, args: Namespace) -> None: ...

class CommandRegistry:
    def __init__(self):
        self._commands: dict[str, Command] = {}
    
    def register(self, cmd: Command) -> None:
        self._commands[cmd.name] = cmd
    
    def get(self, name: str) -> Optional[Command]:
        return self._commands.get(name)
    
    def all(self) -> dict[str, Command]:
        return self._commands.copy()

# 使用示例
class AddCommand(Command):
    name = "add"
    help = "添加新任务"
    
    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("content", help="任务内容")
        parser.add_argument("--priority", choices=["高", "中", "低"], default="中")
        parser.add_argument("--due", help="截止日期")
        parser.add_argument("--tags", help="标签（逗号分隔）")
        parser.add_argument("--test", action="store_true", help="标记为测试任务")
    
    def execute(self, args: Namespace) -> None:
        from services.task_service import TaskService
        service = TaskService()
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
        service.create(
            content=args.content,
            priority=args.priority,
            due_date=args.due,
            tags=tags,
            is_test=args.test
        )
        print(f"✅ 已添加任务：{args.content}")
```

### 4. 修复任务解析 Bug (executor/task_parser.py)

```python
import re
from typing import Optional

class TaskParser:
    """修复之前 AI 分析文本被误添加为任务的问题"""
    
    # 需要过滤掉的无效内容模式
    INVALID_PATTERNS = [
        r"^根据分析",
        r"^已完成功能",
        r"^我需要",
        r"^\*\*",  # Markdown 标题
        r"^\d+\.",  # 列表项
        r"^-$",     # 单独横线
        r"^\s*$",   # 空行
    ]
    
    # 有效的测试任务模式
    VALID_TEST_PATTERNS = [
        r"测试.*",
        r"test_.*",
        r"CLI.*测试",
    ]
    
    @classmethod
    def is_valid_task(cls, content: str) -> bool:
        """验证内容是否是有效任务"""
        if not content or len(content.strip()) < 3:
            return False
        
        # 检查是否匹配无效模式
        for pattern in cls.INVALID_PATTERNS:
            if re.match(pattern, content.strip()):
                return False
        
        return True
    
    @classmethod
    def sanitize_task_content(cls, content: str) -> Optional[str]:
        """清理任务内容，返回 None 如果无效"""
        if not cls.is_valid_task(content):
            return None
        
        # 去除多余空白
        content = content.strip()
        
        # 限制长度
        if len(content) > 200:
            content = content[:197] + "..."
        
        return content
```

### 5. 自动清理机制 (executor/cleanup.py)

```python
from datetime import datetime, timedelta
from typing import List
from core.models import Task
from core.storage import Storage

class TaskCleaner:
    """自动清理测试任务"""
    
    def __init__(self, storage: Storage):
        self.storage = storage
    
    def cleanup_test_tasks(self, max_age_hours: int = 24) -> dict:
        """
        清理测试任务
        
        Args:
            max_age_hours: 测试任务最大保留时间，默认24小时
        
        Returns:
            {"removed": int, "kept": int}
        """
        tasks = self.storage.load()
        now = datetime.now()
        
        real_tasks = []
        removed = 0
        kept = 0
        
        for task in tasks:
            if not task.is_test:
                real_tasks.append(task)
                continue
            
            # 检查测试任务年龄
            created = datetime.fromisoformat(task.created_at)
            age = now - created
            
            if age > timedelta(hours=max_age_hours):
                removed += 1
            else:
                real_tasks.append(task)
                kept += 1
        
        self.storage.save(real_tasks)
        return {"removed": removed, "kept": kept}
    
    def cleanup_duplicates(self) -> int:
        """清理重复的任务（相同内容）"""
        tasks = self.storage.load()
        seen = set()
        unique_tasks = []
        removed = 0
        
        for task in tasks:
            key = (task.content.strip(), task.is_test)
            if key in seen:
                removed += 1
            else:
                seen.add(key)
                unique_tasks.append(task)
        
        # 重新编号
        for i, task in enumerate(unique_tasks, 1):
            task.id = i
        
        self.storage.save(unique_tasks)
        return removed
    
    def get_cleanup_report(self) -> str:
        """生成清理报告"""
        tasks = self.storage.load()
        test_count = sum(1 for t in tasks if t.is_test)
        real_count = len(tasks) - test_count
        
        return f"""
📊 任务清理报告
----------------
真实任务: {real_count}
测试任务: {test_count}
总计: {len(tasks)}
----------------
建议: 运行 cleanup 清理过期测试任务
"""
```

### 6. 新入口文件 (todo.py)

```python
#!/usr/bin/env python3
"""
Simple Todo Manager - 简单任务管理器
重构版本：模块化架构
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from core.storage import JSONStorage
from commands import AddCommand, ListCommand, DoneCommand, DeleteCommand
from commands import ExportCommand, StatsCommand, DueCommand
from commands import AddTagCommand, RemoveTagCommand, SetPriorityCommand
from commands.base import CommandRegistry
from executor.cleanup import TaskCleaner


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Simple Todo Manager - 简单任务管理器",
        prog="todo"
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 注册所有命令
    registry = CommandRegistry()
    commands = [
        AddCommand(), ListCommand(), DoneCommand(), DeleteCommand(),
        ExportCommand(), StatsCommand(), DueCommand(),
        AddTagCommand(), RemoveTagCommand(), SetPriorityCommand(),
    ]
    for cmd in commands:
        registry.register(cmd)
        sub = subparsers.add_parser(cmd.name, help=cmd.help)
        cmd.add_arguments(sub)
    
    # 添加清理命令
    cleanup_parser = subparsers.add_parser("cleanup", help="清理测试任务")
    cleanup_parser.add_argument("--max-age", type=int, default=24, 
                                help="测试任务最大保留小时数")
    cleanup_parser.add_argument("--duplicates", action="store_true",
                                help="清理重复任务")
    
    return parser, registry


def main():
    parser, registry = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 清理命令
    if args.command == "cleanup":
        config = Config()
        storage = JSONStorage(config.tasks_file)
        cleaner = TaskCleaner(storage)
        
        if args.duplicates:
            removed = cleaner.cleanup_duplicates()
            print(f"🗑️  已清理 {removed} 个重复任务")
        
        result = cleaner.cleanup_test_tasks(max_age_hours=args.max_age)
        print(f"🗑️  已清理 {result['removed']} 个过期测试任务")
        print(f"✅ 保留 {result['kept']} 个近期测试任务")
        return
    
    # 执行命令
    cmd = registry.get(args.command)
    if cmd:
        try:
            cmd.execute(args)
        except Exception as e:
            print(f"❌ 错误: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
```

### 7. 配置文件 (config.py)

```python
from pathlib import Path

class Config:
    """应用配置"""
    
    # 路径
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    
    # 文件
    tasks_file = DATA_DIR / "tasks.json"
    
    # 执行器配置
    EXECUTOR_CONFIG = {
        "cleanup_interval": 5,        # 每5轮执行一次清理
        "test_task_max_age_hours": 24,  # 测试任务保留24小时
        "enable_auto_cleanup": True,
    }
    
    # 测试模式
    TEST_MODE = False
```

---

## 迁移步骤

1. **创建新目录结构**
   ```bash
   mkdir -p core commands services executor utils data tests/{unit,integration,fixtures}
   ```

2. **迁移数据**
   - 备份当前 `tasks.json`
   - 运行迁移脚本分离测试任务

3. **逐步替换**
   - 先实现核心模块 (models, storage)
   - 再实现命令模块
   - 最后替换入口文件

4. **添加测试**
   - 为新模块编写单元测试
   - 确保重构后功能一致

---

## 预期收益

| 指标 | 当前 | 优化后 |
|------|------|--------|
| 主文件行数 | ~700 | ~100 |
| 模块数量 | 1 | 10+ |
| 数据隔离 | ❌ 混合 | ✅ 分离 |
| 测试任务清理 | ❌ 无 | ✅ 自动 |
| 扩展性 | ❌ 低 | ✅ 高 |

需要我开始实施重构吗？还是你想调整方案？
