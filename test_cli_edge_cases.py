#!/usr/bin/env python3
"""
CLI 边缘情况测试套件
测试 Todo 管理器的 CLI 边缘情况和错误处理
"""

import json
import os
import sys
import unittest
from io import StringIO
from unittest.mock import patch

import todo


class TestCLIEdgeCases(unittest.TestCase):
    """测试 CLI 边缘情况的单元测试类"""

    def setUp(self):
        """测试前准备：创建干净的测试环境"""
        self.test_file = "test_tasks_edge.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理：删除测试文件"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_cli_list_filter_tag_no_results(self):
        """测试 CLI list 命令 - 按标签过滤无结果"""
        todo.add_task("无标签任务")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "list", "--tag", "不存在的标签"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("没有找到带标签", result)
        self.assertIn("不存在的标签", result)

    def test_cli_list_filter_priority_no_results(self):
        """测试 CLI list 命令 - 按优先级过滤无结果"""
        todo.add_task("中优先级任务", "中")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "list", "--priority", "高"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("没有找到优先级为", result)
        self.assertIn("高", result)

    def test_cli_add_tag_duplicate(self):
        """测试 CLI add-tag 命令 - 标签已存在"""
        todo.add_task("带标签任务", "中", None, ["工作"])

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "add-tag", "1", "工作"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("标签", result)
        self.assertIn("已存在", result)

    def test_cli_remove_tag_not_exists(self):
        """测试 CLI remove-tag 命令 - 标签不存在"""
        todo.add_task("带标签任务", "中", None, ["工作"])

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "remove-tag", "1", "不存在的标签"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("标签", result)
        self.assertIn("不存在", result)

    def test_cli_export_csv_empty(self):
        """测试 CLI export 命令 - CSV 空任务列表"""
        output = StringIO()
        with patch.object(
            sys,
            "argv",
            ["todo", "export", "--format", "csv", "--output", "test_empty.csv"],
        ):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("暂无任务可导出", result)

        # 确保没有创建文件
        self.assertFalse(os.path.exists("test_empty.csv"))

    def test_cli_export_markdown_empty(self):
        """测试 CLI export 命令 - Markdown 空任务列表"""
        output = StringIO()
        with patch.object(
            sys,
            "argv",
            ["todo", "export", "--format", "markdown", "--output", "test_empty.md"],
        ):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("暂无任务可导出", result)

        # 确保没有创建文件
        self.assertFalse(os.path.exists("test_empty.md"))

    def test_cli_due_days_no_results(self):
        """测试 CLI due 命令 - 指定天数内无任务"""
        # 添加一个 30 天后的任务
        todo.add_task("远期任务", "低", "2026-12-31")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "due", "--days", "1"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("没有", result)
        self.assertIn("天内到期的任务", result)

    def test_cli_stats_filter_tag_no_results(self):
        """测试 CLI stats 命令 - 按标签过滤无结果"""
        todo.add_task("无标签任务", "中")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "stats", "--tag", "不存在的标签"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("没有找到带标签", result)
        self.assertIn("不存在的标签", result)

    def test_cli_stats_filter_priority_no_results(self):
        """测试 CLI stats 命令 - 按优先级过滤无结果"""
        todo.add_task("中优先级任务", "中")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "stats", "--priority", "高"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("没有找到优先级为", result)
        self.assertIn("高", result)

    def test_cli_stats_empty_no_filter(self):
        """测试 CLI stats 命令 - 无任务且无过滤器"""
        output = StringIO()
        with patch.object(sys, "argv", ["todo", "stats"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("暂无任务", result)

    def test_cli_no_command_shows_help(self):
        """测试 CLI 无命令时显示帮助"""
        output = StringIO()
        with patch.object(sys, "argv", ["todo"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("usage", result)
        self.assertIn("add", result)
        self.assertIn("list", result)

    def test_cli_export_default_filename(self):
        """测试 CLI export 命令 - 默认文件名"""
        todo.add_task("导出任务")

        # 测试 CSV 默认文件名
        with patch.object(sys, "argv", ["todo", "export", "--format", "csv"]):
            todo.main()

        self.assertTrue(os.path.exists("tasks_export.csv"))
        os.remove("tasks_export.csv")

        # 添加另一个任务用于 MD 测试
        todo.add_task("导出任务 2")

        # 测试 Markdown 默认文件名
        with patch.object(sys, "argv", ["todo", "export", "--format", "markdown"]):
            todo.main()

        self.assertTrue(os.path.exists("tasks_export.md"))
        os.remove("tasks_export.md")


class TestCLIBackwardCompatibility(unittest.TestCase):
    """测试 CLI 向后兼容性"""

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

    def test_load_tasks_missing_priority(self):
        """测试加载任务 - 缺失优先级字段（向后兼容）"""
        # 手动创建没有 priority 字段的任务
        tasks = [
            {
                "id": 1,
                "content": "旧格式任务",
                "done": False,
                "created_at": "2026-01-01 00:00:00",
            }
        ]

        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False)

        # 加载任务应该自动添加默认优先级
        loaded_tasks = todo.load_tasks()
        self.assertEqual(loaded_tasks[0]["priority"], "中")

    def test_cli_list_with_old_task(self):
        """测试 CLI list 命令 - 显示旧格式任务"""
        # 手动创建没有 priority 字段的任务
        tasks = [
            {
                "id": 1,
                "content": "旧格式任务",
                "done": False,
                "created_at": "2026-01-01 00:00:00",
            }
        ]

        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False)

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "list"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("旧格式任务", result)


class TestCLIInvalidInput(unittest.TestCase):
    """测试 CLI 无效输入处理"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tasks_invalid.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_cli_done_invalid_id(self):
        """测试 CLI done 命令 - 无效 ID"""
        output = StringIO()
        with patch.object(sys, "argv", ["todo", "done", "abc"]):
            with patch.object(sys, "stdout", output):
                with self.assertRaises(SystemExit):
                    todo.main()

    def test_cli_delete_invalid_id(self):
        """测试 CLI delete 命令 - 无效 ID"""
        output = StringIO()
        with patch.object(sys, "argv", ["todo", "delete", "abc"]):
            with patch.object(sys, "stdout", output):
                with self.assertRaises(SystemExit):
                    todo.main()


if __name__ == "__main__":
    print("=" * 60)
    print("CLI 边缘情况测试套件")
    print("=" * 60)
    unittest.main(verbosity=2)
