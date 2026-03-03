#!/usr/bin/env python3
"""
CLI 命令测试套件
测试 Todo 管理器的命令行接口功能
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


class TestCLICommands(unittest.TestCase):
    """测试 CLI 命令的单元测试类"""

    def setUp(self):
        """测试前准备：创建干净的测试环境"""
        self.test_file = "test_tasks_cli.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理：删除测试文件"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_cli_add_basic(self):
        """测试 CLI add 命令 - 基本功能"""
        with patch.object(sys, "argv", ["todo", "add", "测试任务 CLI"]):
            todo.main()

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["content"], "测试任务 CLI")
        self.assertEqual(tasks[0]["priority"], "中")

    def test_cli_add_with_priority(self):
        """测试 CLI add 命令 - 带优先级"""
        with patch.object(
            sys, "argv", ["todo", "add", "高优先级任务", "--priority", "高"]
        ):
            todo.main()

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["priority"], "高")

    def test_cli_add_with_due_date(self):
        """测试 CLI add 命令 - 带截止日期"""
        with patch.object(
            sys, "argv", ["todo", "add", "带截止日期任务", "--due", "2026-12-31"]
        ):
            todo.main()

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["due_date"], "2026-12-31")

    def test_cli_add_with_tags(self):
        """测试 CLI add 命令 - 带标签"""
        with patch.object(
            sys, "argv", ["todo", "add", "带标签任务", "--tags", "工作，紧急"]
        ):
            todo.main()

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["tags"], ["工作", "紧急"])

    def test_cli_list_empty(self):
        """测试 CLI list 命令 - 空任务列表"""
        output = StringIO()
        with patch.object(sys, "argv", ["todo", "list"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("暂无任务", result)

    def test_cli_list_with_tasks(self):
        """测试 CLI list 命令 - 有任务"""
        todo.add_task("任务 1")
        todo.add_task("任务 2", "高")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "list"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("任务 1", result)
        self.assertIn("任务 2", result)

    def test_cli_list_filter_by_priority(self):
        """测试 CLI list 命令 - 按优先级过滤"""
        todo.add_task("高优先级任务", "高")
        todo.add_task("低优先级任务", "低")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "list", "--priority", "高"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("高优先级任务", result)
        self.assertNotIn("低优先级任务", result)

    def test_cli_list_filter_by_tag(self):
        """测试 CLI list 命令 - 按标签过滤"""
        todo.add_task("工作任务", "中", None, ["工作"])
        todo.add_task("个人任务", "中", None, ["个人"])

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "list", "--tag", "工作"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("工作任务", result)
        self.assertNotIn("个人任务", result)

    def test_cli_done(self):
        """测试 CLI done 命令"""
        todo.add_task("待完成任务")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "done", "1"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("已完成", result)

        tasks = todo.load_tasks()
        self.assertTrue(tasks[0]["done"])

    def test_cli_delete(self):
        """测试 CLI delete 命令"""
        todo.add_task("待删除任务")
        todo.add_task("保留任务")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "delete", "1"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("已删除任务", result)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["content"], "保留任务")

    def test_cli_add_tag(self):
        """测试 CLI add-tag 命令"""
        todo.add_task("需要标签的任务")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "add-tag", "1", "新标签"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("添加标签", result)

        tasks = todo.load_tasks()
        self.assertIn("新标签", tasks[0]["tags"])

    def test_cli_remove_tag(self):
        """测试 CLI remove-tag 命令"""
        todo.add_task("带标签任务", "中", None, ["标签 1", "标签 2"])

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "remove-tag", "1", "标签 1"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("移除标签", result)

        tasks = todo.load_tasks()
        self.assertNotIn("标签 1", tasks[0]["tags"])
        self.assertIn("标签 2", tasks[0]["tags"])

    def test_cli_set_priority(self):
        """测试 CLI set-priority 命令"""
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

    def test_cli_export_csv(self):
        """测试 CLI export 命令 - CSV 格式"""
        todo.add_task("导出任务 1", "高")
        todo.add_task("导出任务 2", "低")

        output = StringIO()
        with patch.object(
            sys,
            "argv",
            ["todo", "export", "--format", "csv", "--output", "test_export_cli.csv"],
        ):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("已导出", result)

        self.assertTrue(os.path.exists("test_export_cli.csv"))
        os.remove("test_export_cli.csv")

    def test_cli_export_markdown(self):
        """测试 CLI export 命令 - Markdown 格式"""
        todo.add_task("MD 导出任务 1")

        output = StringIO()
        with patch.object(
            sys,
            "argv",
            [
                "todo",
                "export",
                "--format",
                "markdown",
                "--output",
                "test_export_cli.md",
            ],
        ):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("已导出", result)

        self.assertTrue(os.path.exists("test_export_cli.md"))
        os.remove("test_export_cli.md")

    def test_cli_stats(self):
        """测试 CLI stats 命令"""
        todo.add_task("高优先级统计任务", "高")
        todo.add_task("中优先级统计任务", "中")
        todo.add_task("低优先级统计任务", "低")
        todo.done_task(1)

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "stats"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("任务统计", result)
        self.assertIn("总体情况", result)
        self.assertIn("优先级分布", result)

    def test_cli_stats_filter_by_priority(self):
        """测试 CLI stats 命令 - 按优先级过滤"""
        todo.add_task("高优先级 1", "高")
        todo.add_task("高优先级 2", "高")
        todo.add_task("低优先级", "低")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "stats", "--priority", "高"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("任务统计", result)
        self.assertIn("高优先级：2 个", result)
        self.assertNotIn("低优先级", result)

    def test_cli_stats_filter_by_tag(self):
        """测试 CLI stats 命令 - 按标签过滤"""
        todo.add_task("工作任务", "中", None, ["工作"])
        todo.add_task("个人任务", "中", None, ["个人"])

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "stats", "--tag", "工作"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("任务统计", result)

    def test_cli_help(self):
        """测试 CLI help 显示"""
        output = StringIO()
        with patch.object(sys, "argv", ["todo", "--help"]):
            with patch.object(sys, "stdout", output):
                with self.assertRaises(SystemExit):
                    todo.main()

        result = output.getvalue()
        self.assertIn("usage", result)
        self.assertIn("add", result)
        self.assertIn("list", result)
        self.assertIn("done", result)
        self.assertIn("delete", result)

    def test_cli_list_sort_priority(self):
        """测试 CLI list 命令 - 按优先级排序"""
        todo.add_task("低优先级任务", "低")
        todo.add_task("高优先级任务", "高")
        todo.add_task("中优先级任务", "中")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "list", "--sort", "priority"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        lines = result.split("\n")
        task_lines = [l for l in lines if "任务" in l]

        priority_order = {"高": 0, "中": 1, "低": 2}
        last_priority_idx = -1
        for line in task_lines:
            for priority in ["高", "中", "低"]:
                if priority in line:
                    current_idx = priority_order[priority]
                    self.assertGreaterEqual(current_idx, last_priority_idx)
                    last_priority_idx = current_idx
                    break

    def test_cli_list_sort_none(self):
        """测试 CLI list 命令 - 不排序"""
        todo.add_task("任务 1", "低")
        todo.add_task("任务 2", "高")
        todo.add_task("任务 3", "中")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "list", "--sort", "none"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("任务 1", result)
        self.assertIn("任务 2", result)
        self.assertIn("任务 3", result)

    def test_cli_done_nonexistent_task(self):
        """测试 CLI done 命令 - 不存在的任务"""
        output = StringIO()
        with patch.object(sys, "argv", ["todo", "done", "999"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("未找到任务", result)

    def test_cli_delete_nonexistent_task(self):
        """测试 CLI delete 命令 - 不存在的任务"""
        output = StringIO()
        with patch.object(sys, "argv", ["todo", "delete", "999"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("未找到任务", result)

    def test_cli_add_tag_nonexistent_task(self):
        """测试 CLI add-tag 命令 - 不存在的任务"""
        output = StringIO()
        with patch.object(sys, "argv", ["todo", "add-tag", "999", "标签"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("未找到任务", result)

    def test_cli_remove_tag_nonexistent_task(self):
        """测试 CLI remove-tag 命令 - 不存在的任务"""
        output = StringIO()
        with patch.object(sys, "argv", ["todo", "remove-tag", "999", "标签"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("未找到任务", result)

    def test_cli_set_priority_nonexistent_task(self):
        """测试 CLI set-priority 命令 - 不存在的任务"""
        output = StringIO()
        with patch.object(sys, "argv", ["todo", "set-priority", "999", "高"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("未找到任务", result)


class TestCLIWorkflow(unittest.TestCase):
    """测试 CLI 完整工作流程"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tasks_workflow.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_complete_workflow(self):
        """测试完整的任务管理工作流程"""
        # 1. 添加多个任务
        with patch.object(
            sys,
            "argv",
            [
                "todo",
                "add",
                "任务 1",
                "--priority",
                "高",
                "--due",
                "2026-12-31",
                "--tags",
                "工作，重要",
            ],
        ):
            todo.main()

        with patch.object(sys, "argv", ["todo", "add", "任务 2", "--priority", "中"]):
            todo.main()

        with patch.object(sys, "argv", ["todo", "add", "任务 3", "--priority", "低"]):
            todo.main()

        # 2. 列出所有任务
        output = StringIO()
        with patch.object(sys, "argv", ["todo", "list"]):
            with patch.object(sys, "stdout", output):
                todo.main()
        result = output.getvalue()
        self.assertIn("任务 1", result)
        self.assertIn("任务 2", result)
        self.assertIn("任务 3", result)

        # 3. 修改任务 2 的优先级
        with patch.object(sys, "argv", ["todo", "set-priority", "2", "高"]):
            todo.main()

        # 4. 为任务 3 添加标签
        with patch.object(sys, "argv", ["todo", "add-tag", "3", "个人"]):
            todo.main()

        # 5. 完成任务 1
        with patch.object(sys, "argv", ["todo", "done", "1"]):
            todo.main()

        # 6. 查看统计
        output = StringIO()
        with patch.object(sys, "argv", ["todo", "stats"]):
            with patch.object(sys, "stdout", output):
                todo.main()
        result = output.getvalue()
        self.assertIn("已完成：1", result)

        # 7. 导出任务
        with patch.object(
            sys,
            "argv",
            ["todo", "export", "--format", "csv", "--output", "test_workflow.csv"],
        ):
            todo.main()
        self.assertTrue(os.path.exists("test_workflow.csv"))
        os.remove("test_workflow.csv")

        # 8. 删除任务 3
        with patch.object(sys, "argv", ["todo", "delete", "3"]):
            todo.main()

        # 验证最终状态
        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertTrue(tasks[0]["done"])
        self.assertEqual(tasks[1]["content"], "任务 2")


if __name__ == "__main__":
    unittest.main()
