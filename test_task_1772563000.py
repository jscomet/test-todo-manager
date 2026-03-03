#!/usr/bin/env python3
"""
测试任务_1772563000 - Todo 管理器综合功能验证
验证 Todo 管理器的标签管理和优先级修改功能
"""

import json
import os
import subprocess
import sys
import unittest
from io import StringIO
from unittest.mock import patch

import todo


class TestTagManagement(unittest.TestCase):
    """标签管理功能测试"""

    def setUp(self):
        """测试前准备：创建干净的测试环境"""
        self.test_file = "test_1772563000.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        # 初始化一个任务用于测试
        todo.add_task("测试任务")

    def tearDown(self):
        """测试后清理：删除测试文件"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_tag_to_task(self):
        """测试为任务添加标签"""
        todo.add_tag(1, "工作")
        tasks = todo.load_tasks()
        self.assertIn("工作", tasks[0]["tags"])

    def test_add_multiple_tags(self):
        """测试添加多个标签"""
        todo.add_tag(1, "工作")
        todo.add_tag(1, "紧急")
        todo.add_tag(1, "重要")
        tasks = todo.load_tasks()
        self.assertEqual(len(tasks[0]["tags"]), 3)
        self.assertIn("工作", tasks[0]["tags"])
        self.assertIn("紧急", tasks[0]["tags"])
        self.assertIn("重要", tasks[0]["tags"])

    def test_add_duplicate_tag(self):
        """测试添加重复标签（不应重复添加）"""
        todo.add_tag(1, "测试")
        todo.add_tag(1, "测试")
        tasks = todo.load_tasks()
        self.assertEqual(len(tasks[0]["tags"]), 1)
        self.assertEqual(tasks[0]["tags"], ["测试"])

    def test_remove_tag_from_task(self):
        """测试从任务移除标签"""
        todo.add_tag(1, "工作")
        todo.add_tag(1, "紧急")
        todo.remove_tag(1, "工作")
        tasks = todo.load_tasks()
        self.assertNotIn("工作", tasks[0]["tags"])
        self.assertIn("紧急", tasks[0]["tags"])

    def test_remove_nonexistent_tag(self):
        """测试移除不存在的标签"""
        todo.add_tag(1, "工作")
        # 不应该抛出异常，只会有提示
        todo.remove_tag(1, "不存在的标签")
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["tags"], ["工作"])

    def test_add_tag_to_nonexistent_task(self):
        """测试为不存在的任务添加标签"""
        # 不应该抛出异常，只会有提示
        todo.add_tag(999, "测试")
        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)

    def test_remove_tag_from_nonexistent_task(self):
        """测试从不存在的任务移除标签"""
        # 不应该抛出异常，只会有提示
        todo.remove_tag(999, "测试")
        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)


class TestPriorityModification(unittest.TestCase):
    """优先级修改功能测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_priority_1772563000.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_change_priority_from_medium_to_high(self):
        """测试将优先级从中改为高"""
        todo.add_task("测试任务", "中")
        todo.set_priority(1, "高")
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["priority"], "高")

    def test_change_priority_from_high_to_low(self):
        """测试将优先级从高改为低"""
        todo.add_task("测试任务", "高")
        todo.set_priority(1, "低")
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["priority"], "低")

    def test_change_priority_from_low_to_medium(self):
        """测试将优先级从低改为中"""
        todo.add_task("测试任务", "低")
        todo.set_priority(1, "中")
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["priority"], "中")

    def test_set_same_priority(self):
        """测试设置相同的优先级"""
        todo.add_task("测试任务", "中")
        todo.set_priority(1, "中")
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["priority"], "中")

    def test_set_priority_nonexistent_task(self):
        """测试为不存在的任务设置优先级"""
        todo.add_task("测试任务", "中")
        # 不应该抛出异常，只会有提示
        todo.set_priority(999, "高")
        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["priority"], "中")


class TestCLITagCommands(unittest.TestCase):
    """CLI 标签命令测试 - 简化版本"""

    def test_cli_add_tag_command_exists(self):
        """测试 CLI add-tag 命令可用"""
        result = subprocess.run(
            ["python3", "todo.py", "add-tag", "--help"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("tag", result.stdout)

    def test_cli_remove_tag_command_exists(self):
        """测试 CLI remove-tag 命令可用"""
        result = subprocess.run(
            ["python3", "todo.py", "remove-tag", "--help"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("tag", result.stdout)


class TestCLIPriorityCommand(unittest.TestCase):
    """CLI 优先级命令测试 - 简化版本"""

    def test_cli_set_priority_command_exists(self):
        """测试 CLI set-priority 命令可用"""
        result = subprocess.run(
            ["python3", "todo.py", "set-priority", "--help"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("priority", result.stdout)
        self.assertIn("高", result.stdout)
        self.assertIn("中", result.stdout)
        self.assertIn("低", result.stdout)


class TestIntegration(unittest.TestCase):
    """集成测试 - 测试标签和优先级的组合功能"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_integration_1772563000.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_task_with_tags_and_priority(self):
        """测试任务同时有标签和优先级"""
        todo.add_task("综合任务", "高", "2026-12-31", ["工作", "紧急"])
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["priority"], "高")
        self.assertEqual(tasks[0]["tags"], ["工作", "紧急"])
        self.assertEqual(tasks[0]["due_date"], "2026-12-31")

    def test_modify_task_with_multiple_attributes(self):
        """测试修改有多个属性的任务"""
        todo.add_task("复杂任务", "中", "2026-12-31", ["工作"])
        todo.set_priority(1, "高")
        todo.add_tag(1, "紧急")
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["priority"], "高")
        self.assertIn("工作", tasks[0]["tags"])
        self.assertIn("紧急", tasks[0]["tags"])
        self.assertEqual(tasks[0]["due_date"], "2026-12-31")

    def test_filter_by_tag_and_priority(self):
        """测试按标签和优先级过滤"""
        todo.add_task("任务 1", "高", None, ["工作"])
        todo.add_task("任务 2", "中", None, ["工作"])
        todo.add_task("任务 3", "高", None, ["生活"])

        # 按标签过滤
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            todo.list_tasks(tag_filter="工作")
            output = mock_stdout.getvalue()
            self.assertIn("任务 1", output)
            self.assertIn("任务 2", output)
            self.assertNotIn("任务 3", output)

        # 按优先级过滤
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            todo.list_tasks(priority_filter="高")
            output = mock_stdout.getvalue()
            self.assertIn("任务 1", output)
            self.assertNotIn("任务 2", output)
            self.assertIn("任务 3", output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
