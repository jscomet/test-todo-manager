#!/usr/bin/env python3
"""
截止日期 CLI 命令测试套件
测试 Todo 管理器的 due 命令功能
"""

import json
import os
import sys
import unittest
from datetime import datetime, timedelta
from io import StringIO
from unittest.mock import patch

import todo


class TestDueCLICommands(unittest.TestCase):
    """测试 due CLI 命令的单元测试类"""

    def setUp(self):
        """测试前准备：创建干净的测试环境"""
        self.test_file = "test_tasks_due.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理：删除测试文件"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_due_empty(self):
        """测试 due 命令 - 无任务"""
        output = StringIO()
        with patch.object(sys, "argv", ["todo", "due"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("暂无任务", result)

    def test_due_no_due_dates(self):
        """测试 due 命令 - 任务无截止日期"""
        todo.add_task("无截止日期任务")
        todo.add_task("另一个任务")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "due"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("没有带截止日期的任务", result)

    def test_due_with_tasks(self):
        """测试 due 命令 - 有带截止日期的任务"""
        today = datetime.now().date()
        due_date = (today + timedelta(days=5)).strftime("%Y-%m-%d")

        todo.add_task("即将到期任务", "高", due_date)

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "due"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("即将到期的任务", result)
        self.assertIn("即将到期任务", result)
        self.assertIn(due_date, result)

    def test_due_days_filter(self):
        """测试 due 命令 - 按天数过滤"""
        today = datetime.now().date()
        due_soon = (today + timedelta(days=3)).strftime("%Y-%m-%d")
        due_later = (today + timedelta(days=30)).strftime("%Y-%m-%d")

        todo.add_task("近期任务", "高", due_soon)
        todo.add_task("远期任务", "低", due_later)

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "due", "--days", "7"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("近期任务", result)
        self.assertNotIn("远期任务", result)
        self.assertIn("7 天内", result)

    def test_due_sort_by_date(self):
        """测试 due 命令 - 按日期排序"""
        today = datetime.now().date()
        due_1 = (today + timedelta(days=10)).strftime("%Y-%m-%d")
        due_2 = (today + timedelta(days=5)).strftime("%Y-%m-%d")
        due_3 = (today + timedelta(days=15)).strftime("%Y-%m-%d")

        todo.add_task("任务 1", "中", due_1)
        todo.add_task("任务 2", "中", due_2)
        todo.add_task("任务 3", "中", due_3)

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "due", "--sort", "date"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        lines = [l for l in result.split("\n") if "任务" in l]

        self.assertLess(lines[0].find("任务 2"), 0)
        task2_idx = -1
        task1_idx = -1
        task3_idx = -1
        for i, line in enumerate(lines):
            if "任务 2" in line:
                task2_idx = i
            elif "任务 1" in line:
                task1_idx = i
            elif "任务 3" in line:
                task3_idx = i

        self.assertLess(task2_idx, task1_idx)
        self.assertLess(task1_idx, task3_idx)

    def test_due_sort_by_priority(self):
        """测试 due 命令 - 按优先级排序"""
        today = datetime.now().date()
        due_date = (today + timedelta(days=10)).strftime("%Y-%m-%d")

        todo.add_task("低优先级任务", "低", due_date)
        todo.add_task("高优先级任务", "高", due_date)
        todo.add_task("中优先级任务", "中", due_date)

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "due", "--sort", "priority"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        lines = [l for l in result.split("\n") if "任务" in l]

        priority_order = {"高": 0, "中": 1, "低": 2}
        last_priority_idx = -1
        for line in lines:
            for priority in ["高", "中", "低"]:
                if priority in line:
                    current_idx = priority_order[priority]
                    self.assertGreaterEqual(current_idx, last_priority_idx)
                    last_priority_idx = current_idx
                    break

    def test_due_overdue_task(self):
        """测试 due 命令 - 过期任务"""
        today = datetime.now().date()
        past_date = (today - timedelta(days=5)).strftime("%Y-%m-%d")

        todo.add_task("过期任务", "高", past_date)

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "due"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("过期任务", result)
        self.assertIn("已过期", result)
        self.assertIn("5 天", result)

    def test_due_today(self):
        """测试 due 命令 - 今天到期"""
        today = datetime.now().date()
        today_str = today.strftime("%Y-%m-%d")

        todo.add_task("今天到期任务", "高", today_str)

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "due"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("今天到期", result)
        self.assertIn("⚠️", result)

    def test_due_tomorrow(self):
        """测试 due 命令 - 明天到期"""
        today = datetime.now().date()
        tomorrow_str = (today + timedelta(days=1)).strftime("%Y-%m-%d")

        todo.add_task("明天到期任务", "高", tomorrow_str)

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "due"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("明天到期", result)
        self.assertIn("⚠️", result)

    def test_due_with_completed_task(self):
        """测试 due 命令 - 包含已完成任务"""
        today = datetime.now().date()
        due_date = (today + timedelta(days=5)).strftime("%Y-%m-%d")

        todo.add_task("待完成任务", "高", due_date)
        todo.add_task("已完成任务", "中", due_date)

        tasks = todo.load_tasks()
        todo.done_task(tasks[1]["id"])

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "due"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("待完成任务", result)
        self.assertIn("已完成任务", result)
        self.assertIn("✅", result)

    def test_due_days_zero(self):
        """测试 due 命令 - 0 天内（仅今天）"""
        today = datetime.now().date()
        today_str = today.strftime("%Y-%m-%d")
        tomorrow_str = (today + timedelta(days=1)).strftime("%Y-%m-%d")

        todo.add_task("今天任务", "高", today_str)
        todo.add_task("明天任务", "中", tomorrow_str)

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "due", "--days", "0"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("今天任务", result)
        self.assertNotIn("明天任务", result)

    def test_due_mixed_dates(self):
        """测试 due 命令 - 混合各种日期状态"""
        today = datetime.now().date()
        past = (today - timedelta(days=3)).strftime("%Y-%m-%d")
        today_str = today.strftime("%Y-%m-%d")
        future = (today + timedelta(days=10)).strftime("%Y-%m-%d")

        todo.add_task("过期任务", "高", past)
        todo.add_task("今天任务", "中", today_str)
        todo.add_task("未来任务", "低", future)

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "due"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("过期任务", result)
        self.assertIn("已过期", result)
        self.assertIn("今天任务", result)
        self.assertIn("今天到期", result)
        self.assertIn("未来任务", result)
        self.assertIn("剩余", result)


class TestDueCLIEdgeCases(unittest.TestCase):
    """测试边界情况"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tasks_due_edge.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_due_invalid_date_format(self):
        """测试 due 命令 - 无效日期格式（应该被跳过）"""
        tasks = [
            {
                "id": 1,
                "content": "有效日期任务",
                "done": False,
                "priority": "高",
                "due_date": "2026-12-31",
            },
            {
                "id": 2,
                "content": "无效日期任务",
                "done": False,
                "priority": "中",
                "due_date": "invalid-date",
            },
        ]

        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "due"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("有效日期任务", result)
        self.assertNotIn("无效日期任务", result)

    def test_due_shortcut_d(self):
        """测试 due 命令 - -d 简写"""
        today = datetime.now().date()
        due_date = (today + timedelta(days=3)).strftime("%Y-%m-%d")

        todo.add_task("测试任务", "高", due_date)

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "due", "-d", "7"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("测试任务", result)

    def test_due_shortcut_s(self):
        """测试 due 命令 - -s 简写"""
        today = datetime.now().date()
        due_date = (today + timedelta(days=10)).strftime("%Y-%m-%d")

        todo.add_task("高优先级任务", "高", due_date)
        todo.add_task("低优先级任务", "低", due_date)

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "due", "-s", "priority"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("高优先级任务", result)
        self.assertIn("低优先级任务", result)


if __name__ == "__main__":
    print("=" * 60)
    print("截止日期 CLI 命令测试套件")
    print("=" * 60)
    unittest.main(verbosity=2)
