#!/usr/bin/env python3
"""
测试任务_1772559141 - 综合功能测试
测试 Todo 管理器的核心功能
"""

import json
import os
import unittest
from io import StringIO
from unittest.mock import patch

import todo


class TestCoreFunctionality(unittest.TestCase):
    """核心功能测试类"""

    def setUp(self):
        """测试前准备：创建干净的测试环境"""
        self.test_file = "test_1772559141.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理：删除测试文件"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_task_basic(self):
        """测试基本添加任务功能"""
        todo.add_task("基本测试任务", "中")
        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["content"], "基本测试任务")
        self.assertFalse(tasks[0]["done"])

    def test_add_task_with_all_fields(self):
        """测试添加完整字段任务"""
        todo.add_task("完整字段任务", "高", "2026-12-31", ["工作", "紧急"])
        tasks = todo.load_tasks()
        task = tasks[0]
        self.assertEqual(task["content"], "完整字段任务")
        self.assertEqual(task["priority"], "高")
        self.assertEqual(task["due_date"], "2026-12-31")
        self.assertEqual(task["tags"], ["工作", "紧急"])

    def test_list_tasks_empty(self):
        """测试空任务列表显示"""
        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.list_tasks()
        output = captured_output.getvalue()
        self.assertIn("暂无任务", output)

    def test_list_tasks_with_items(self):
        """测试有任务时的列表显示"""
        todo.add_task("任务 1", "高")
        todo.add_task("任务 2", "中")
        todo.add_task("任务 3", "低")

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.list_tasks()
        output = captured_output.getvalue()
        self.assertIn("任务 1", output)
        self.assertIn("任务 2", output)
        self.assertIn("任务 3", output)

    def test_done_task(self):
        """测试标记任务完成"""
        todo.add_task("待完成任务", "中")
        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]

        todo.done_task(task_id)
        tasks = todo.load_tasks()
        self.assertTrue(tasks[0]["done"])

    def test_done_nonexistent_task(self):
        """测试标记不存在的任务"""
        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.done_task(999)
        output = captured_output.getvalue()
        self.assertIn("未找到任务", output)

    def test_delete_task(self):
        """测试删除任务"""
        todo.add_task("待删除任务", "中")
        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]

        todo.delete_task(task_id)
        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 0)

    def test_delete_nonexistent_task(self):
        """测试删除不存在的任务"""
        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.delete_task(999)
        output = captured_output.getvalue()
        self.assertIn("未找到任务", output)

    def test_add_tag(self):
        """测试添加标签"""
        todo.add_task("标签测试任务", "中")
        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]

        todo.add_tag(task_id, "测试")
        tasks = todo.load_tasks()
        self.assertIn("测试", tasks[0]["tags"])

    def test_remove_tag(self):
        """测试移除标签"""
        todo.add_task("标签移除任务", "中", tags=["标签 1", "标签 2"])
        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]

        todo.remove_tag(task_id, "标签 1")
        tasks = todo.load_tasks()
        self.assertNotIn("标签 1", tasks[0]["tags"])
        self.assertIn("标签 2", tasks[0]["tags"])

    def test_set_priority(self):
        """测试修改优先级"""
        todo.add_task("优先级修改任务", "中")
        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]

        todo.set_priority(task_id, "高")
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["priority"], "高")

    def test_list_filter_by_priority(self):
        """测试按优先级过滤列表"""
        todo.add_task("高优先任务", "高")
        todo.add_task("中优先任务", "中")
        todo.add_task("低优先任务", "低")

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.list_tasks(priority_filter="高")
        output = captured_output.getvalue()
        self.assertIn("高优先任务", output)
        self.assertNotIn("中优先任务", output)
        self.assertNotIn("低优先任务", output)

    def test_list_filter_by_tag(self):
        """测试按标签过滤列表"""
        todo.add_task("任务 1", "中", tags=["工作"])
        todo.add_task("任务 2", "中", tags=["生活"])
        todo.add_task("任务 3", "中", tags=["工作", "紧急"])

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.list_tasks(tag_filter="工作")
        output = captured_output.getvalue()
        self.assertIn("任务 1", output)
        self.assertIn("任务 3", output)
        self.assertNotIn("任务 2", output)

    def test_sort_by_priority(self):
        """测试按优先级排序"""
        todo.add_task("低优先", "低")
        todo.add_task("高优先", "高")
        todo.add_task("中优先", "中")

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.list_tasks(sort_by="priority")
        output = captured_output.getvalue()

        high_pos = output.find("高优先")
        mid_pos = output.find("中优先")
        low_pos = output.find("低优先")

        self.assertLess(high_pos, mid_pos)
        self.assertLess(mid_pos, low_pos)

    def test_export_csv(self):
        """测试 CSV 导出"""
        todo.add_task("CSV 测试任务", "高", "2026-12-31", ["测试"])

        test_csv = "test_1772559141_export.csv"
        todo.export_csv(test_csv)

        with open(test_csv, "r", encoding="utf-8-sig") as f:
            content = f.read()

        self.assertIn("CSV 测试任务", content)
        self.assertIn("高", content)
        self.assertIn("2026-12-31", content)
        self.assertIn("测试", content)

        os.remove(test_csv)

    def test_export_markdown(self):
        """测试 Markdown 导出"""
        todo.add_task("MD 测试任务", "中")

        test_md = "test_1772559141_export.md"
        todo.export_markdown(test_md)

        with open(test_md, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("MD 测试任务", content)
        self.assertIn("⭕", content)

        os.remove(test_md)

    def test_backward_compatibility(self):
        """测试向后兼容性"""
        old_tasks = [
            {"id": 1, "content": "旧任务", "done": False},
            {"id": 2, "content": "旧任务 2", "done": True, "priority": "高"},
        ]

        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(old_tasks, f, ensure_ascii=False, indent=2)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["priority"], "中")
        self.assertEqual(tasks[1]["priority"], "高")

    def test_duplicate_tag_prevention(self):
        """测试防止重复添加标签"""
        todo.add_task("重复标签测试", "中", tags=["测试"])
        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.add_tag(task_id, "测试")
        output = captured_output.getvalue()
        self.assertIn("已存在", output)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks[0]["tags"]), 1)

    def test_id_renumber_after_delete(self):
        """测试删除后 ID 重新编号"""
        todo.add_task("任务 1", "中")
        todo.add_task("任务 2", "中")
        todo.add_task("任务 3", "中")

        todo.delete_task(2)
        tasks = todo.load_tasks()

        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["id"], 1)
        self.assertEqual(tasks[1]["id"], 2)


class TestCommandLineInterface(unittest.TestCase):
    """命令行接口测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_cli_1772559141.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_help_command(self):
        """测试帮助命令"""
        import subprocess

        result = subprocess.run(
            ["python3", "todo.py", "--help"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )
        self.assertIn("add", result.stdout)
        self.assertIn("list", result.stdout)
        self.assertIn("done", result.stdout)

    def test_add_via_cli(self):
        """测试通过 CLI 添加任务"""
        import subprocess

        result = subprocess.run(
            ["python3", "todo.py", "add", "--help"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )
        self.assertIn("--priority", result.stdout)
        self.assertIn("--due", result.stdout)
        self.assertIn("--tags", result.stdout)


if __name__ == "__main__":
    print("=" * 60)
    print("测试任务_1772559141 - 综合功能测试")
    print("=" * 60)
    unittest.main(verbosity=2)
