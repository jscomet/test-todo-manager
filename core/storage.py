"""数据存储模块

实现任务的持久化存储，支持 JSON 格式。
符合 SPEC.md 第 3.3 节存储格式规范和 4.2 节 Storage 接口。
"""

import json
from pathlib import Path
from typing import List
from abc import ABC, abstractmethod

from .models import Task


class Storage(ABC):
    """存储抽象基类

    符合 SPEC 4.2 Storage 接口规范
    """

    @abstractmethod
    def load(self) -> List[Task]:
        """加载任务列表"""
        pass

    @abstractmethod
    def save(self, tasks: List[Task]) -> None:
        """保存任务列表"""
        pass

    @abstractmethod
    def clear_test_tasks(self) -> int:
        """清理测试任务，返回清理数量"""
        pass


class JSONStorage(Storage):
    """JSON 文件存储实现

    符合 SPEC 3.3 存储格式:
    - tasks.json: 真实任务
    - test-tasks.json: 测试任务（隔离存储）
    """

    def __init__(self, data_dir: Path | None = None):
        """初始化存储

        Args:
            data_dir: 数据目录路径，默认为项目根目录下的 data/
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data"

        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.tasks_file = self.data_dir / "tasks.json"
        self.test_tasks_file = self.data_dir / "test-tasks.json"

        # 如果文件不存在，创建空文件
        if not self.tasks_file.exists():
            self._write_json(self.tasks_file, [])
        if not self.test_tasks_file.exists():
            self._write_json(self.test_tasks_file, [])

    def _read_json(self, file_path: Path) -> List[dict]:
        """读取 JSON 文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_json(self, file_path: Path, data: List[dict]) -> None:
        """写入 JSON 文件"""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, include_test: bool = False) -> List[Task]:
        """加载任务列表

        Args:
            include_test: 是否包含测试任务，默认 False

        Returns:
            Task 对象列表
        """
        tasks_data = self._read_json(self.tasks_file)
        tasks = [Task.from_dict(data) for data in tasks_data]

        if include_test:
            test_data = self._read_json(self.test_tasks_file)
            test_tasks = [Task.from_dict(data) for data in test_data]
            tasks.extend(test_tasks)

        return tasks

    def load_test_tasks(self) -> List[Task]:
        """单独加载测试任务"""
        test_data = self._read_json(self.test_tasks_file)
        return [Task.from_dict(data) for data in test_data]

    def save(self, tasks: List[Task]) -> None:
        """保存真实任务列表

        Args:
            tasks: Task 对象列表（仅保存 is_test=False 的任务）
        """
        # 过滤出真实任务
        real_tasks = [t for t in tasks if not t.is_test]
        data = [task.to_dict() for task in real_tasks]
        self._write_json(self.tasks_file, data)

    def save_test_tasks(self, test_tasks: List[Task]) -> None:
        """保存测试任务列表

        Args:
            test_tasks: Task 对象列表（仅保存 is_test=True 的任务）
        """
        data = [task.to_dict() for task in test_tasks if task.is_test]
        self._write_json(self.test_tasks_file, data)

    def add_task(self, task: Task) -> None:
        """添加单个任务

        Args:
            task: Task 对象
        """
        if task.is_test:
            test_tasks = self.load_test_tasks()
            test_tasks.append(task)
            self.save_test_tasks(test_tasks)
        else:
            tasks = self.load()
            tasks.append(task)
            self.save(tasks)

    def update_task(self, task: Task) -> None:
        """更新单个任务

        Args:
            task: Task 对象
        """
        if task.is_test:
            test_tasks = self.load_test_tasks()
            for i, t in enumerate(test_tasks):
                if t.id == task.id:
                    test_tasks[i] = task
                    break
            self.save_test_tasks(test_tasks)
        else:
            tasks = self.load()
            for i, t in enumerate(tasks):
                if t.id == task.id:
                    tasks[i] = task
                    break
            self.save(tasks)

    def delete_task(self, task_id: int) -> bool:
        """删除任务

        Args:
            task_id: 任务 ID

        Returns:
            是否删除成功
        """
        # 先在真实任务中查找
        tasks = self.load()
        for i, t in enumerate(tasks):
            if t.id == task_id:
                tasks.pop(i)
                self.save(tasks)
                return True

        # 再在测试任务中查找
        test_tasks = self.load_test_tasks()
        for i, t in enumerate(test_tasks):
            if t.id == task_id:
                test_tasks.pop(i)
                self.save_test_tasks(test_tasks)
                return True

        return False

    def get_next_id(self) -> int:
        """获取下一个任务 ID

        Returns:
            下一个可用的任务 ID
        """
        tasks = self.load(include_test=True)
        if not tasks:
            return 1
        return max(t.id for t in tasks) + 1

    def clear_test_tasks(self) -> int:
        """清理所有测试任务

        Returns:
            清理的任务数量
        """
        test_tasks = self.load_test_tasks()
        count = len(test_tasks)
        self._write_json(self.test_tasks_file, [])
        return count

    def clear_all(self) -> None:
        """清空所有数据（仅用于测试）"""
        self._write_json(self.tasks_file, [])
        self._write_json(self.test_tasks_file, [])
