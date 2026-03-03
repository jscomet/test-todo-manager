#!/usr/bin/env python3
"""
截止日期功能测试套件
测试 Todo 管理器中的截止日期相关功能
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


class TestDueDateFunctionality(unittest.TestCase):
    """测试截止日期功能的单元测试类"""

    def setUp(self):
        """测试前准备：创建干净的测试环境"""
        self.test_file = "test_tasks.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理：删除测试文件"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_task_with_due_date(self):
        """测试添加带截止日期的任务"""
        due_date = "2026-12-31"
        todo.add_task("测试任务", "高", due_date)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["content"], "测试任务")
        self.assertEqual(tasks[0]["due_date"], due_date)
        self.assertEqual(tasks[0]["priority"], "高")

    def test_add_task_without_due_date(self):
        """测试添加不带截止日期的任务"""
        todo.add_task("无截止日期任务", "中")

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["content"], "无截止日期任务")
        self.assertNotIn("due_date", tasks[0])

    def test_add_task_with_due_date_and_tags(self):
        """测试添加带截止日期和标签的任务"""
        due_date = "2026-06-15"
        tags = ["工作", "紧急"]
        todo.add_task("综合测试任务", "高", due_date, tags)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        task = tasks[0]
        self.assertEqual(task["due_date"], due_date)
        self.assertEqual(task["tags"], tags)
        self.assertEqual(task["priority"], "高")

    def test_due_date_format_validation(self):
        """测试截止日期格式（YYYY-MM-DD）"""
        valid_dates = [
            "2026-01-01",
            "2026-12-31",
            "2027-06-15",
        ]

        for date in valid_dates:
            todo.add_task(f"测试 {date}", "中", date)

        tasks = todo.load_tasks()
        for i, date in enumerate(valid_dates):
            self.assertEqual(tasks[i]["due_date"], date)

    def test_list_tasks_shows_due_date(self):
        """测试列表显示时包含截止日期"""
        todo.add_task("有截止日期的任务", "高", "2026-03-10")
        todo.add_task("无截止日期的任务", "低")

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.list_tasks()

        output = captured_output.getvalue()
        self.assertIn("2026-03-10", output)
        self.assertIn("有截止日期的任务", output)
        self.assertIn("无截止日期的任务", output)

    def test_export_csv_includes_due_date(self):
        """测试 CSV 导出包含截止日期列"""
        todo.add_task("任务 1", "高", "2026-03-10")
        todo.add_task("任务 2", "中")

        test_csv = "test_export.csv"
        todo.export_csv(test_csv)

        with open(test_csv, "r", encoding="utf-8-sig") as f:
            content = f.read()

        self.assertIn("截止日期", content)
        self.assertIn("2026-03-10", content)

        os.remove(test_csv)

    def test_export_markdown_includes_due_date(self):
        """测试 Markdown 导出包含截止日期列"""
        todo.add_task("任务 1", "高", "2026-03-10")
        todo.add_task("任务 2", "中")

        test_md = "test_export.md"
        todo.export_markdown(test_md)

        with open(test_md, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("截止日期", content)
        self.assertIn("2026-03-10", content)

        os.remove(test_md)

    def test_due_date_with_completed_task(self):
        """测试已完成任务保留截止日期"""
        todo.add_task("待完成任务", "高", "2026-03-10")

        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]
        todo.done_task(task_id)

        tasks = todo.load_tasks()
        self.assertTrue(tasks[0]["done"])
        self.assertEqual(tasks[0]["due_date"], "2026-03-10")

    def test_multiple_tasks_with_different_due_dates(self):
        """测试多个任务有不同的截止日期"""
        tasks_data = [
            ("任务 1", "2026-01-15"),
            ("任务 2", "2026-06-20"),
            ("任务 3", "2026-12-25"),
        ]

        for content, due_date in tasks_data:
            todo.add_task(content, "中", due_date)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 3)

        for i, (content, due_date) in enumerate(tasks_data):
            self.assertEqual(tasks[i]["content"], content)
            self.assertEqual(tasks[i]["due_date"], due_date)


class TestDueDateEdgeCases(unittest.TestCase):
    """测试边界情况"""

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

    def test_empty_due_date_string(self):
        """测试空字符串截止日期"""
        todo.add_task("测试任务", "中", "")

        tasks = todo.load_tasks()
        task = tasks[0]
        self.assertNotIn("due_date", task)

    def test_due_date_in_past(self):
        """测试过去日期作为截止日期"""
        past_date = "2020-01-01"
        todo.add_task("过期任务", "低", past_date)

        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["due_date"], past_date)

    def test_load_tasks_with_missing_due_date(self):
        """测试加载缺少截止日期的旧任务"""
        old_tasks = [{"id": 1, "content": "旧任务", "done": False, "priority": "中"}]

        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(old_tasks, f, ensure_ascii=False, indent=2)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertNotIn("due_date", tasks[0])


if __name__ == "__main__":
    print("=" * 60)
    print("截止日期功能测试套件")
    print("=" * 60)
    unittest.main(verbosity=2)
