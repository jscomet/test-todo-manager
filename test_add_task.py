#!/usr/bin/env python3
"""
添加功能测试套件
测试 Todo 管理器中的添加任务功能
"""

import json
import os
import sys
import unittest
from datetime import datetime
from io import StringIO
from unittest.mock import patch

# 导入被测试模块
import todo


class TestAddTaskFunctionality(unittest.TestCase):
    """测试添加任务功能的单元测试类"""

    def setUp(self):
        """测试前准备：创建干净的测试环境"""
        self.test_data_dir = Path("test-output/test_add_task")
        self.test_data_dir.mkdir(parents=True, exist_ok=True)
        todo._test_data_dir = str(self.test_data_dir)

        tasks_file = self.test_data_dir / "tasks.json"
        test_tasks_file = self.test_data_dir / "test-tasks.json"
        for f in [tasks_file, test_tasks_file]:
            if f.exists():
                f.unlink()

    def tearDown(self):
        """测试后清理：删除测试文件"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_task_basic(self):
        """测试基本添加任务功能"""
        todo.add_task("测试任务")

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["content"], "测试任务")
        self.assertEqual(tasks[0]["done"], False)
        self.assertEqual(tasks[0]["priority"], "中")
        self.assertIn("created_at", tasks[0])

    def test_add_task_with_priority(self):
        """测试添加不同优先级的任务"""
        test_cases = [
            ("高优先级任务", "高"),
            ("中优先级任务", "中"),
            ("低优先级任务", "低"),
        ]

        for content, priority in test_cases:
            todo.add_task(content, priority)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 3)

        for i, (content, priority) in enumerate(test_cases):
            self.assertEqual(tasks[i]["content"], content)
            self.assertEqual(tasks[i]["priority"], priority)

    def test_add_task_with_due_date(self):
        """测试添加带截止日期的任务"""
        due_date = "2026-12-31"
        todo.add_task("带截止日期任务", "高", due_date)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["content"], "带截止日期任务")
        self.assertEqual(tasks[0]["due_date"], due_date)
        self.assertEqual(tasks[0]["priority"], "高")

    def test_add_task_with_tags(self):
        """测试添加带标签的任务"""
        tags = ["工作", "紧急", "项目 A"]
        todo.add_task("带标签任务", "中", None, tags)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["content"], "带标签任务")
        self.assertEqual(tasks[0]["tags"], tags)
        self.assertNotIn("due_date", tasks[0])

    def test_add_task_with_all_fields(self):
        """测试添加包含所有字段的任务"""
        content = "完整任务"
        priority = "高"
        due_date = "2026-06-15"
        tags = ["工作", "重要"]

        todo.add_task(content, priority, due_date, tags)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        task = tasks[0]
        self.assertEqual(task["content"], content)
        self.assertEqual(task["priority"], priority)
        self.assertEqual(task["due_date"], due_date)
        self.assertEqual(task["tags"], tags)
        self.assertEqual(task["done"], False)
        self.assertIn("created_at", task)
        self.assertIn("id", task)

    def test_add_task_auto_increment_id(self):
        """测试任务 ID 自动递增"""
        todo.add_task("任务 1")
        todo.add_task("任务 2")
        todo.add_task("任务 3")

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 3)

        for i, task in enumerate(tasks):
            self.assertEqual(task["id"], i + 1)

    def test_add_task_timestamp(self):
        """测试创建时间戳正确记录"""
        before_add = datetime.now().replace(microsecond=0)
        todo.add_task("带时间戳任务")
        after_add = datetime.now().replace(microsecond=0)

        tasks = todo.load_tasks()
        created_at = datetime.strptime(tasks[0]["created_at"], "%Y-%m-%d %H:%M:%S")

        self.assertGreaterEqual(created_at, before_add)
        self.assertLessEqual(created_at, after_add)


class TestAddTaskEdgeCases(unittest.TestCase):
    """测试添加任务的边界情况"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tasks_edge.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_task_empty_content(self):
        """测试添加空内容任务"""
        todo.add_task("")

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["content"], "")

    def test_add_task_special_characters(self):
        """测试添加包含特殊字符的任务"""
        special_content = "任务！@#$%^&*()_+-=[]{}|;':\",./<>？测试"
        todo.add_task(special_content)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["content"], special_content)

    def test_add_task_unicode_content(self):
        """测试添加包含 Unicode 字符的任务"""
        unicode_content = "🚀 任务测试 🎉 emoji 测试"
        todo.add_task(unicode_content)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["content"], unicode_content)

    def test_add_task_very_long_content(self):
        """测试添加超长内容任务"""
        long_content = "A" * 10000
        todo.add_task(long_content)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["content"], long_content)

    def test_add_task_empty_tags_list(self):
        """测试添加空标签列表的任务"""
        todo.add_task("空标签任务", "中", None, [])

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        # 空标签列表不会添加到任务中（与 None 行为一致）
        self.assertNotIn("tags", tasks[0])

    def test_add_task_none_tags(self):
        """测试添加 tags 为 None 的任务"""
        todo.add_task("None 标签任务", "中", None, None)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertNotIn("tags", tasks[0])

    def test_add_task_none_due_date(self):
        """测试添加 due_date 为 None 的任务"""
        todo.add_task("None 截止日期任务", "中", None)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertNotIn("due_date", tasks[0])

    def test_add_task_empty_due_date_string(self):
        """测试添加空字符串截止日期的任务"""
        todo.add_task("空截止日期任务", "中", "")

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertNotIn("due_date", tasks[0])


class TestAddTaskPersistence(unittest.TestCase):
    """测试添加任务的数据持久化"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tasks_persist.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_task_persists_to_file(self):
        """测试任务正确保存到文件"""
        todo.add_task("持久化任务", "高", "2026-12-31", ["测试"])

        with open(self.test_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["content"], "持久化任务")
        self.assertEqual(data[0]["priority"], "高")
        self.assertEqual(data[0]["due_date"], "2026-12-31")
        self.assertEqual(data[0]["tags"], ["测试"])

    def test_add_multiple_tasks_persistence(self):
        """测试添加多个任务后的持久化"""
        for i in range(10):
            todo.add_task(f"任务{i}")

        with open(self.test_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(len(data), 10)
        for i, task in enumerate(data):
            self.assertEqual(task["content"], f"任务{i}")
            self.assertEqual(task["id"], i + 1)

    def test_add_task_file_encoding(self):
        """测试任务文件的编码正确性（UTF-8）"""
        chinese_content = "中文任务测试"
        japanese_content = "日本語タスクテスト"
        emoji_content = "🎉🚀✨"

        todo.add_task(chinese_content)
        todo.add_task(japanese_content)
        todo.add_task(emoji_content)

        with open(self.test_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["content"], chinese_content)
        self.assertEqual(data[1]["content"], japanese_content)
        self.assertEqual(data[2]["content"], emoji_content)


class TestAddTaskOutput(unittest.TestCase):
    """测试添加任务的输出信息"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tasks_output.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_task_print_confirmation(self):
        """测试添加任务后打印确认信息"""
        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.add_task("测试输出任务")

        output = captured_output.getvalue()
        self.assertIn("✅", output)
        self.assertIn("已添加任务", output)
        self.assertIn("测试输出任务", output)

    def test_add_task_with_priority_output(self):
        """测试添加任务确认信息包含任务内容"""
        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.add_task("高优先级任务", "高")

        output = captured_output.getvalue()
        self.assertIn("✅", output)
        self.assertIn("高优先级任务", output)


class TestAddTaskBackwardCompatibility(unittest.TestCase):
    """测试添加任务的向后兼容性"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tasks_compat.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_task_to_existing_file(self):
        """测试向已有任务文件添加新任务"""
        old_tasks = [
            {"id": 1, "content": "旧任务 1", "done": False, "priority": "中"},
            {"id": 2, "content": "旧任务 2", "done": True, "priority": "高"},
        ]

        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(old_tasks, f, ensure_ascii=False, indent=2)

        todo.add_task("新任务", "低")

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 3)
        self.assertEqual(tasks[2]["content"], "新任务")
        self.assertEqual(tasks[2]["id"], 3)

    def test_add_task_maintains_old_tasks(self):
        """测试添加新任务不影响旧任务"""
        old_tasks = [
            {
                "id": 1,
                "content": "旧任务",
                "done": False,
                "priority": "中",
                "due_date": "2026-01-01",
                "tags": ["旧标签"],
            }
        ]

        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(old_tasks, f, ensure_ascii=False, indent=2)

        todo.add_task("新任务")

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["content"], "旧任务")
        self.assertEqual(tasks[0]["due_date"], "2026-01-01")
        self.assertEqual(tasks[0]["tags"], ["旧标签"])


class TestCLIAddCommand(unittest.TestCase):
    """测试 CLI add 命令"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tasks_cli.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_cli_add_basic(self):
        """测试 CLI 基本添加命令"""
        sys.argv = ["todo", "add", "CLI 测试任务"]

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.main()

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["content"], "CLI 测试任务")
        self.assertEqual(tasks[0]["priority"], "中")

    def test_cli_add_with_priority(self):
        """测试 CLI 添加带优先级的任务"""
        sys.argv = ["todo", "add", "高优先级任务", "--priority", "高"]

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.main()

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["priority"], "高")

    def test_cli_add_with_priority_short(self):
        """测试 CLI 添加带优先级短参数的任务"""
        sys.argv = ["todo", "add", "低优先级任务", "-p", "低"]

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.main()

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["priority"], "低")

    def test_cli_add_with_due_date(self):
        """测试 CLI 添加带截止日期的任务"""
        sys.argv = ["todo", "add", "带截止日期任务", "--due", "2026-12-31"]

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.main()

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["due_date"], "2026-12-31")

    def test_cli_add_with_due_date_short(self):
        """测试 CLI 添加带截止日期短参数的任务"""
        sys.argv = ["todo", "add", "任务", "-d", "2026-06-15"]

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.main()

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["due_date"], "2026-06-15")

    def test_cli_add_with_tags(self):
        """测试 CLI 添加带标签的任务"""
        sys.argv = ["todo", "add", "带标签任务", "--tags", "工作，紧急"]

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.main()

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["tags"], ["工作", "紧急"])

    def test_cli_add_with_tags_short(self):
        """测试 CLI 添加带标签短参数的任务"""
        sys.argv = ["todo", "add", "任务", "-t", "标签 1，标签 2"]

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.main()

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["tags"], ["标签 1", "标签 2"])

    def test_cli_add_with_all_options(self):
        """测试 CLI 添加带所有选项的任务"""
        sys.argv = [
            "todo",
            "add",
            "完整任务",
            "--priority",
            "高",
            "--due",
            "2026-12-31",
            "--tags",
            "工作，重要",
        ]

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.main()

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        task = tasks[0]
        self.assertEqual(task["content"], "完整任务")
        self.assertEqual(task["priority"], "高")
        self.assertEqual(task["due_date"], "2026-12-31")
        self.assertEqual(task["tags"], ["工作", "重要"])


if __name__ == "__main__":
    print("=" * 60)
    print("添加功能测试套件")
    print("=" * 60)
    unittest.main(verbosity=2)
