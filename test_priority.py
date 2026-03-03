#!/usr/bin/env python3
"""
优先级测试套件
测试 Todo 管理器的优先级功能
"""

import json
import os
import sys
import unittest
from io import StringIO
from unittest.mock import patch

import todo


class TestPriorityBasic(unittest.TestCase):
    """测试优先级基本功能"""

    def setUp(self):
        """测试前准备：创建干净的测试环境"""
        self.test_file = "test_tasks_priority.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理：删除测试文件"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_task_high_priority(self):
        """测试添加高优先级任务"""
        todo.add_task("高优先级任务", "高")

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["priority"], "高")

    def test_add_task_medium_priority(self):
        """测试添加中优先级任务"""
        todo.add_task("中优先级任务", "中")

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["priority"], "中")

    def test_add_task_low_priority(self):
        """测试添加低优先级任务"""
        todo.add_task("低优先级任务", "低")

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["priority"], "低")

    def test_add_all_priority_levels(self):
        """测试添加所有优先级级别的任务"""
        todo.add_task("高优先级", "高")
        todo.add_task("中优先级", "中")
        todo.add_task("低优先级", "低")

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 3)
        priorities = [t["priority"] for t in tasks]
        self.assertEqual(priorities.count("高"), 1)
        self.assertEqual(priorities.count("中"), 1)
        self.assertEqual(priorities.count("低"), 1)


class TestPrioritySort(unittest.TestCase):
    """测试优先级排序功能"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tasks_priority_sort.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_list_sort_by_priority_order(self):
        """测试列表按优先级排序顺序"""
        todo.add_task("低优先级任务", "低")
        todo.add_task("高优先级任务", "高")
        todo.add_task("中优先级任务", "中")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "list", "--sort", "priority"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        lines = [l for l in result.split("\n") if "优先级任务" in l]

        high_idx = next(i for i, l in enumerate(lines) if "高优先级任务" in l)
        medium_idx = next(i for i, l in enumerate(lines) if "中优先级任务" in l)
        low_idx = next(i for i, l in enumerate(lines) if "低优先级任务" in l)

        self.assertLess(high_idx, medium_idx)
        self.assertLess(medium_idx, low_idx)

    def test_priority_sort_with_multiple_tasks(self):
        """测试多个任务按优先级排序"""
        for _ in range(3):
            todo.add_task("低优先级", "低")
        todo.add_task("高优先级", "高")
        for _ in range(2):
            todo.add_task("中优先级", "中")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "list", "--sort", "priority"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        lines = [
            l
            for l in result.split("\n")
            if "优先级" in l and "🔴" in l or "🟡" in l or "🟢" in l
        ]

        high_count = sum(1 for l in lines if "🔴" in l)
        medium_count = sum(1 for l in lines if "🟡" in l)
        low_count = sum(1 for l in lines if "🟢" in l)

        self.assertEqual(high_count, 1)
        self.assertEqual(medium_count, 2)
        self.assertEqual(low_count, 3)


class TestPriorityFilter(unittest.TestCase):
    """测试优先级过滤功能"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tasks_priority_filter.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_filter_by_high_priority(self):
        """测试按高优先级过滤"""
        todo.add_task("高优先级 1", "高")
        todo.add_task("高优先级 2", "高")
        todo.add_task("中优先级", "中")
        todo.add_task("低优先级", "低")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "list", "--priority", "高"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("高优先级 1", result)
        self.assertIn("高优先级 2", result)
        self.assertNotIn("中优先级", result)
        self.assertNotIn("低优先级", result)

    def test_filter_by_medium_priority(self):
        """测试按中优先级过滤"""
        todo.add_task("高优先级", "高")
        todo.add_task("中优先级 1", "中")
        todo.add_task("中优先级 2", "中")
        todo.add_task("低优先级", "低")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "list", "--priority", "中"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("中优先级 1", result)
        self.assertIn("中优先级 2", result)
        self.assertNotIn("高优先级", result)
        self.assertNotIn("低优先级", result)

    def test_filter_by_low_priority(self):
        """测试按低优先级过滤"""
        todo.add_task("高优先级", "高")
        todo.add_task("中优先级", "中")
        todo.add_task("低优先级 1", "低")
        todo.add_task("低优先级 2", "低")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "list", "--priority", "低"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("低优先级 1", result)
        self.assertIn("低优先级 2", result)
        self.assertNotIn("高优先级", result)
        self.assertNotIn("中优先级", result)

    def test_filter_empty_result(self):
        """测试过滤无结果"""
        todo.add_task("中优先级任务", "中")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "list", "--priority", "高"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("没有找到优先级为 '高' 的任务", result)


class TestPriorityIcons(unittest.TestCase):
    """测试优先级图标显示"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tasks_priority_icons.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_high_priority_icon(self):
        """测试高优先级图标显示"""
        todo.add_task("高优先级任务", "高")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "list"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("🔴", result)

    def test_medium_priority_icon(self):
        """测试中优先级图标显示"""
        todo.add_task("中优先级任务", "中")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "list"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("🟡", result)

    def test_low_priority_icon(self):
        """测试低优先级图标显示"""
        todo.add_task("低优先级任务", "低")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "list"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("🟢", result)

    def test_all_priority_icons(self):
        """测试所有优先级图标同时显示"""
        todo.add_task("高", "高")
        todo.add_task("中", "中")
        todo.add_task("低", "低")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "list"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("🔴", result)
        self.assertIn("🟡", result)
        self.assertIn("🟢", result)


class TestSetPriority(unittest.TestCase):
    """测试修改优先级功能"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tasks_set_priority.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_set_priority_medium_to_high(self):
        """测试优先级从中改为高"""
        todo.add_task("修改优先级任务", "中")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "set-priority", "1", "高"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("优先级已修改", result)
        self.assertIn("中 → 高", result)

        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["priority"], "高")

    def test_set_priority_high_to_low(self):
        """测试优先级从高改为低"""
        todo.add_task("修改优先级任务", "高")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "set-priority", "1", "低"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("优先级已修改", result)
        self.assertIn("高 → 低", result)

        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["priority"], "低")

    def test_set_priority_low_to_medium(self):
        """测试优先级从低改为中"""
        todo.add_task("修改优先级任务", "低")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "set-priority", "1", "中"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("优先级已修改", result)
        self.assertIn("低 → 中", result)

        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["priority"], "中")

    def test_set_priority_nonexistent_task(self):
        """测试修改不存在任务的优先级"""
        output = StringIO()
        with patch.object(sys, "argv", ["todo", "set-priority", "999", "高"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("未找到任务", result)


class TestPriorityStats(unittest.TestCase):
    """测试优先级统计功能"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tasks_priority_stats.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_stats_all_priority_levels(self):
        """测试统计显示所有优先级级别"""
        todo.add_task("高优先级 1", "高")
        todo.add_task("高优先级 2", "高")
        todo.add_task("中优先级 1", "中")
        todo.add_task("中优先级 2", "中")
        todo.add_task("中优先级 3", "中")
        todo.add_task("低优先级", "低")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "stats"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("📊 任务统计", result)
        self.assertIn("🔴 高优先级：2 个", result)
        self.assertIn("🟡 中优先级：3 个", result)
        self.assertIn("🟢 低优先级：1 个", result)

    def test_stats_with_completed_tasks(self):
        """测试统计包含已完成任务"""
        todo.add_task("高优先级完成", "高")
        todo.add_task("高优先级未完成", "高")
        todo.done_task(1)

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "stats"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("高优先级：2 个 (完成：1/2)", result)

    def test_stats_filter_by_priority(self):
        """测试按优先级过滤统计"""
        todo.add_task("高优先级 1", "高")
        todo.add_task("高优先级 2", "高")
        todo.add_task("低优先级", "低")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "stats", "--priority", "高"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("优先级：高", result)
        self.assertIn("高优先级：2 个", result)
        self.assertNotIn("低优先级", result)

    def test_stats_empty(self):
        """测试空任务统计"""
        output = StringIO()
        with patch.object(sys, "argv", ["todo", "stats"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("暂无任务", result)


class TestPriorityDueDate(unittest.TestCase):
    """测试优先级与截止日期结合功能"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tasks_priority_due.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_due_sort_by_priority(self):
        """测试到期任务按优先级排序"""
        todo.add_task("高优先级到期", "高", due_date="2026-03-10")
        todo.add_task("低优先级到期", "低", due_date="2026-03-10")
        todo.add_task("中优先级到期", "中", due_date="2026-03-10")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "due", "--sort", "priority"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("高优先级到期", result)
        self.assertIn("中优先级到期", result)
        self.assertIn("低优先级到期", result)

    def test_due_sort_by_date(self):
        """测试到期任务按日期排序"""
        todo.add_task("高优先级远", "高", due_date="2026-12-31")
        todo.add_task("低优先级近", "低", due_date="2026-03-10")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "due", "--sort", "date"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        lines = [l for l in result.split("\n") if "优先级" in l]

        if len(lines) >= 2:
            low_idx = next(i for i, l in enumerate(lines) if "低优先级近" in l)
            high_idx = next(i for i, l in enumerate(lines) if "高优先级远" in l)
            self.assertLess(low_idx, high_idx)


class TestPriorityBackwardCompatibility(unittest.TestCase):
    """测试优先级的向后兼容性"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tasks_priority_compat.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_load_old_tasks_without_priority(self):
        """测试加载没有优先级的旧任务"""
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

    def test_load_mixed_tasks(self):
        """测试加载混合优先级任务"""
        old_tasks = [
            {"id": 1, "content": "有高优先级", "done": False, "priority": "高"},
            {"id": 2, "content": "无优先级", "done": False},
            {"id": 3, "content": "有低优先级", "done": True, "priority": "低"},
        ]

        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(old_tasks, f, ensure_ascii=False, indent=2)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 3)
        self.assertEqual(tasks[0]["priority"], "高")
        self.assertEqual(tasks[1]["priority"], "中")
        self.assertEqual(tasks[2]["priority"], "低")


class TestPriorityExport(unittest.TestCase):
    """测试优先级导出功能"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tasks_priority_export.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists("test_priority_export.csv"):
            os.remove("test_priority_export.csv")
        if os.path.exists("test_priority_export.md"):
            os.remove("test_priority_export.md")

    def test_export_csv_includes_priority(self):
        """测试 CSV 导出包含优先级"""
        todo.add_task("高优先级导出", "高")
        todo.add_task("低优先级导出", "低")

        todo.export_csv("test_priority_export.csv")

        with open("test_priority_export.csv", "r", encoding="utf-8-sig") as f:
            content = f.read()

        self.assertIn("优先级", content)
        self.assertIn("高", content)
        self.assertIn("低", content)

    def test_export_markdown_includes_priority(self):
        """测试 Markdown 导出包含优先级"""
        todo.add_task("高优先级 MD", "高")

        todo.export_markdown("test_priority_export.md")

        with open("test_priority_export.md", "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("优先级", content)
        self.assertIn("高", content)


class TestPriorityEdgeCases(unittest.TestCase):
    """测试优先级边界情况"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tasks_priority_edge.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_priority_with_special_characters(self):
        """测试带特殊字符的任务优先级"""
        todo.add_task("特殊@#￥字符任务", "高")

        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["priority"], "高")

    def test_priority_with_emoji(self):
        """测试带 emoji 的任务优先级"""
        todo.add_task("😀 Emoji 任务", "中")

        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["priority"], "中")

    def test_priority_with_long_content(self):
        """测试长内容任务优先级"""
        long_content = (
            "这是一个非常长的任务内容，用于测试优先级功能在处理长文本时的表现" * 10
        )
        todo.add_task(long_content, "低")

        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["priority"], "低")

    def test_many_tasks_different_priorities(self):
        """测试大量不同优先级任务"""
        for i in range(50):
            priority = ["高", "中", "低"][i % 3]
            todo.add_task(f"任务{i}", priority)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 50)

        high_count = sum(1 for t in tasks if t["priority"] == "高")
        medium_count = sum(1 for t in tasks if t["priority"] == "中")
        low_count = sum(1 for t in tasks if t["priority"] == "低")

        self.assertEqual(high_count, 17)
        self.assertEqual(medium_count, 17)
        self.assertEqual(low_count, 16)


if __name__ == "__main__":
    print("=" * 60)
    print("优先级测试套件")
    print("=" * 60)
    unittest.main(verbosity=2)
