#!/usr/bin/env python3
"""
测试删除任务功能
"""

import json
import os
import sys
import unittest
from io import StringIO
from unittest.mock import patch

import todo


class TestDeleteTask(unittest.TestCase):
    """测试 delete_task 函数"""

    def setUp(self):
        """设置测试环境"""
        self.test_file = "test_delete_tasks.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """清理测试文件"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_delete_single_task(self):
        """测试删除单个任务"""
        todo.add_task("测试任务 1")
        todo.add_task("测试任务 2")

        todo.delete_task(1)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["content"], "测试任务 2")

    def test_delete_task_renumbers_ids(self):
        """测试删除任务后重新编号"""
        todo.add_task("任务 1")
        todo.add_task("任务 2")
        todo.add_task("任务 3")

        todo.delete_task(2)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["id"], 1)
        self.assertEqual(tasks[0]["content"], "任务 1")
        self.assertEqual(tasks[1]["id"], 2)
        self.assertEqual(tasks[1]["content"], "任务 3")

    def test_delete_nonexistent_task(self):
        """测试删除不存在的任务"""
        todo.add_task("测试任务")

        with patch("sys.stdout", new=StringIO()) as fake_out:
            todo.delete_task(999)
            output = fake_out.getvalue()
            self.assertIn("未找到任务", output)

    def test_delete_last_task(self):
        """测试删除最后一个任务"""
        todo.add_task("任务 1")
        todo.add_task("任务 2")
        todo.add_task("任务 3")

        todo.delete_task(3)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["content"], "任务 1")
        self.assertEqual(tasks[1]["content"], "任务 2")

    def test_delete_first_task(self):
        """测试删除第一个任务"""
        todo.add_task("任务 1")
        todo.add_task("任务 2")
        todo.add_task("任务 3")

        todo.delete_task(1)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["id"], 1)
        self.assertEqual(tasks[0]["content"], "任务 2")
        self.assertEqual(tasks[1]["id"], 2)
        self.assertEqual(tasks[1]["content"], "任务 3")

    def test_delete_task_with_tags(self):
        """测试删除带标签的任务"""
        todo.add_task("带标签任务", tags=["工作", "紧急"])

        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]
        todo.delete_task(task_id)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 0)

    def test_delete_task_with_due_date(self):
        """测试删除带截止日期的任务"""
        todo.add_task("截止日期任务", due_date="2026-12-31")

        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]
        todo.delete_task(task_id)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 0)

    def test_delete_task_with_priority(self):
        """测试删除不同优先级的任务"""
        todo.add_task("高优先级", priority="高")
        todo.add_task("中优先级", priority="中")
        todo.add_task("低优先级", priority="低")

        todo.delete_task(2)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 2)
        priorities = [t["priority"] for t in tasks]
        self.assertIn("高", priorities)
        self.assertIn("低", priorities)
        self.assertNotIn("中", priorities)

    def test_delete_all_tasks(self):
        """测试删除所有任务"""
        todo.add_task("任务 1")
        todo.add_task("任务 2")

        todo.delete_task(1)
        todo.delete_task(1)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 0)

    def test_delete_from_empty_list(self):
        """测试从空列表删除"""
        with patch("sys.stdout", new=StringIO()) as fake_out:
            todo.delete_task(1)
            output = fake_out.getvalue()
            self.assertIn("未找到任务", output)

    def test_delete_preserves_task_data(self):
        """测试删除操作不影响其他任务数据"""
        todo.add_task("任务 1", priority="高", due_date="2026-12-31", tags=["测试"])
        todo.add_task("任务 2", priority="中")
        todo.add_task("任务 3", priority="低", due_date="2026-11-30", tags=["工作"])

        todo.delete_task(2)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 2)

        task1 = next(t for t in tasks if t["content"] == "任务 1")
        self.assertEqual(task1["priority"], "高")
        self.assertEqual(task1["due_date"], "2026-12-31")
        self.assertIn("测试", task1["tags"])

        task3 = next(t for t in tasks if t["content"] == "任务 3")
        self.assertEqual(task3["priority"], "低")
        self.assertEqual(task3["due_date"], "2026-11-30")
        self.assertIn("工作", task3["tags"])


class TestDeleteCLI(unittest.TestCase):
    """测试 CLI delete 命令"""

    def setUp(self):
        """设置测试环境"""
        self.test_file = "test_delete_cli.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """清理测试文件"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_cli_delete(self):
        """测试 CLI delete 命令"""
        todo.add_task("CLI 测试任务")

        with patch.object(sys, "argv", ["todo", "delete", "1"]):
            with patch("sys.stdout", new=StringIO()) as fake_out:
                todo.main()
                output = fake_out.getvalue()
                self.assertIn("已删除任务", output)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 0)

    def test_cli_delete_nonexistent(self):
        """测试 CLI delete 不存在的任务"""
        todo.add_task("测试任务")

        with patch.object(sys, "argv", ["todo", "delete", "999"]):
            with patch("sys.stdout", new=StringIO()) as fake_out:
                todo.main()
                output = fake_out.getvalue()
                self.assertIn("未找到任务", output)

    def test_cli_delete_multiple_sequential(self):
        """测试 CLI 顺序删除多个任务"""
        todo.add_task("任务 1")
        todo.add_task("任务 2")
        todo.add_task("任务 3")

        with patch.object(sys, "argv", ["todo", "delete", "1"]):
            with patch("sys.stdout", new=StringIO()):
                todo.main()

        with patch.object(sys, "argv", ["todo", "delete", "1"]):
            with patch("sys.stdout", new=StringIO()):
                todo.main()

        with patch.object(sys, "argv", ["todo", "delete", "1"]):
            with patch("sys.stdout", new=StringIO()):
                todo.main()

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 0)

    def test_cli_delete_with_list(self):
        """测试删除后列表显示正确"""
        todo.add_task("任务 1", priority="高")
        todo.add_task("任务 2", priority="中")
        todo.add_task("任务 3", priority="低")

        with patch.object(sys, "argv", ["todo", "delete", "2"]):
            with patch("sys.stdout", new=StringIO()):
                todo.main()

        with patch.object(sys, "argv", ["todo", "list"]):
            with patch("sys.stdout", new=StringIO()) as fake_out:
                todo.main()
                output = fake_out.getvalue()
                self.assertIn("任务 1", output)
                self.assertIn("任务 3", output)
                self.assertNotIn("任务 2", output)


class TestDeleteEdgeCases(unittest.TestCase):
    """测试删除功能的边界情况"""

    def setUp(self):
        """设置测试环境"""
        self.test_file = "test_delete_edge.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """清理测试文件"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_delete_with_negative_id(self):
        """测试删除负数 ID"""
        todo.add_task("测试任务")

        with patch("sys.stdout", new=StringIO()) as fake_out:
            todo.delete_task(-1)
            output = fake_out.getvalue()
            self.assertIn("未找到任务", output)

    def test_delete_with_zero_id(self):
        """测试删除 ID 为 0"""
        todo.add_task("测试任务")

        with patch("sys.stdout", new=StringIO()) as fake_out:
            todo.delete_task(0)
            output = fake_out.getvalue()
            self.assertIn("未找到任务", output)

    def test_delete_with_very_large_id(self):
        """测试删除非常大的 ID"""
        todo.add_task("测试任务")

        with patch("sys.stdout", new=StringIO()) as fake_out:
            todo.delete_task(999999999)
            output = fake_out.getvalue()
            self.assertIn("未找到任务", output)

    def test_delete_maintains_json_structure(self):
        """测试删除后 JSON 结构正确"""
        todo.add_task("任务 1", priority="高", due_date="2026-12-31", tags=["测试"])
        todo.add_task("任务 2", priority="中")

        todo.delete_task(1)

        with open(self.test_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertIsInstance(data, list)
            self.assertEqual(len(data), 1)
            self.assertIn("id", data[0])
            self.assertIn("content", data[0])
            self.assertIn("done", data[0])
            self.assertIn("priority", data[0])

    def test_delete_completed_task(self):
        """测试删除已完成的任务"""
        todo.add_task("任务 1")
        todo.done_task(1)
        todo.add_task("任务 2")

        todo.delete_task(1)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["content"], "任务 2")

    def test_delete_renumbers_after_multiple_deletes(self):
        """测试多次删除后编号正确"""
        for i in range(1, 6):
            todo.add_task(f"任务 {i}")

        todo.delete_task(3)
        todo.delete_task(1)
        todo.delete_task(2)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 2)
        for i, task in enumerate(tasks):
            self.assertEqual(task["id"], i + 1)


if __name__ == "__main__":
    unittest.main()
