#!/usr/bin/env python3
"""
默认优先级测试套件
测试 Todo 管理器中添加新任务时的默认优先级功能
"""

import json
import os
import sys
import unittest
from io import StringIO
from unittest.mock import patch

import todo


class TestDefaultPriorityBasic(unittest.TestCase):
    """测试默认优先级基本功能"""

    def setUp(self):
        """测试前准备：创建干净的测试环境"""
        self.test_file = "test_tasks_default_priority.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理：删除测试文件"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_task_default_priority(self):
        """测试添加任务时默认优先级为"中" """
        todo.add_task("测试任务")

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["priority"], "中")

    def test_add_task_explicit_medium_priority(self):
        """测试显式设置优先级为"中" """
        todo.add_task("中优先级任务", "中")

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["priority"], "中")

    def test_add_task_multiple_default_priority(self):
        """测试添加多个任务时默认优先级都为"中" """
        for i in range(5):
            todo.add_task(f"任务{i}")

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 5)
        for task in tasks:
            self.assertEqual(task["priority"], "中")

    def test_add_task_with_due_date_default_priority(self):
        """测试添加带截止日期的任务时默认优先级为"中" """
        todo.add_task("带截止日期任务", due_date="2026-12-31")

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["priority"], "中")
        self.assertEqual(tasks[0]["due_date"], "2026-12-31")

    def test_add_task_with_tags_default_priority(self):
        """测试添加带标签的任务时默认优先级为"中" """
        todo.add_task("带标签任务", tags=["工作", "紧急"])

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["priority"], "中")
        self.assertEqual(tasks[0]["tags"], ["工作", "紧急"])

    def test_add_task_with_all_options_default_priority(self):
        """测试添加带所有选项的任务时默认优先级为"中" """
        todo.add_task("完整任务", due_date="2026-06-15", tags=["测试", "验证"])

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        task = tasks[0]
        self.assertEqual(task["priority"], "中")
        self.assertEqual(task["due_date"], "2026-06-15")
        self.assertEqual(task["tags"], ["测试", "验证"])


class TestDefaultPriorityFunctionParameters(unittest.TestCase):
    """测试函数参数级别的默认优先级"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tasks_params.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_task_positional_content_only(self):
        """测试只传递内容参数时默认优先级"""
        todo.add_task("仅内容任务")

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["priority"], "中")

    def test_add_task_keyword_content_only(self):
        """测试使用关键字参数只传递内容时默认优先级"""
        todo.add_task(content="关键字内容任务")

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["priority"], "中")

    def test_add_task_priority_parameter_position(self):
        """测试优先级参数位置（第二个参数）"""
        todo.add_task("任务", "高")

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["priority"], "高")


class TestDefaultPriorityBackwardCompatibility(unittest.TestCase):
    """测试默认优先级的向后兼容性"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tasks_compat_priority.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_load_tasks_adds_default_priority_to_old_tasks(self):
        """测试加载旧任务时自动添加默认优先级"""
        old_tasks = [
            {"id": 1, "content": "旧任务 1", "done": False},
            {"id": 2, "content": "旧任务 2", "done": True},
        ]

        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(old_tasks, f, ensure_ascii=False, indent=2)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 2)
        for task in tasks:
            self.assertEqual(task["priority"], "中")

    def test_load_tasks_preserves_existing_priority(self):
        """测试加载任务时保留已有优先级"""
        old_tasks = [
            {"id": 1, "content": "高优先级任务", "done": False, "priority": "高"},
            {"id": 2, "content": "低优先级任务", "done": True, "priority": "低"},
        ]

        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(old_tasks, f, ensure_ascii=False, indent=2)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["priority"], "高")
        self.assertEqual(tasks[1]["priority"], "低")

    def test_add_task_to_old_file_gets_default_priority(self):
        """测试向旧格式文件添加任务时获得默认优先级"""
        old_tasks = [{"id": 1, "content": "旧任务", "done": False}]

        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(old_tasks, f, ensure_ascii=False, indent=2)

        todo.add_task("新任务")

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["priority"], "中")
        self.assertEqual(tasks[1]["priority"], "中")


class TestCLIDefaultPriority(unittest.TestCase):
    """测试 CLI 命令的默认优先级"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tasks_cli_default.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_cli_add_without_priority_flag(self):
        """测试 CLI add 命令不使用 --priority 标志时默认优先级"""
        sys.argv = ["todo", "add", "CLI 默认优先级任务"]

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.main()

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["priority"], "中")

    def test_cli_add_with_default_priority_flag(self):
        """测试 CLI add 命令显式使用 --priority 中时"""
        sys.argv = ["todo", "add", "显式中优先级", "--priority", "中"]

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.main()

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["priority"], "中")

    def test_cli_add_with_short_priority_flag_default(self):
        """测试 CLI add 命令使用 -p 短标志默认优先级"""
        sys.argv = ["todo", "add", "短标志任务", "-p", "中"]

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.main()

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["priority"], "中")

    def test_cli_add_mixed_options_default_priority(self):
        """测试 CLI add 命令混合选项时默认优先级"""
        sys.argv = [
            "todo",
            "add",
            "混合选项任务",
            "--due",
            "2026-12-31",
            "--tags",
            "测试",
        ]

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.main()

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["priority"], "中")
        self.assertEqual(tasks[0]["due_date"], "2026-12-31")
        self.assertEqual(tasks[0]["tags"], ["测试"])


class TestDefaultPrioritySortAndFilter(unittest.TestCase):
    """测试默认优先级在排序和过滤中的行为"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tasks_sort_filter.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_default_priority_tasks_sort_correctly(self):
        """测试默认优先级任务在排序中的位置"""
        todo.add_task("高优先级任务", "高")
        todo.add_task("默认优先级任务 1")
        todo.add_task("低优先级任务", "低")
        todo.add_task("默认优先级任务 2")

        tasks = todo.load_tasks()
        priority_order = {"高": 0, "中": 1, "低": 2}
        sorted_tasks = sorted(
            tasks, key=lambda t: priority_order.get(t.get("priority", "中"), 1)
        )

        self.assertEqual(sorted_tasks[0]["priority"], "高")
        self.assertEqual(sorted_tasks[1]["priority"], "中")
        self.assertEqual(sorted_tasks[2]["priority"], "中")
        self.assertEqual(sorted_tasks[3]["priority"], "低")

    def test_filter_by_medium_priority_includes_default(self):
        """测试按"中"优先级过滤包含默认优先级任务"""
        todo.add_task("默认任务 1")
        todo.add_task("高优先级任务", "高")
        todo.add_task("默认任务 2")
        todo.add_task("低优先级任务", "低")

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.list_tasks(priority_filter="中")

        output = captured_output.getvalue()
        self.assertIn("默认任务 1", output)
        self.assertIn("默认任务 2", output)
        self.assertNotIn("高优先级任务", output)
        self.assertNotIn("低优先级任务", output)


if __name__ == "__main__":
    print("=" * 60)
    print("默认优先级测试套件")
    print("=" * 60)
    unittest.main(verbosity=2)
