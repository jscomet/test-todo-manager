#!/usr/bin/env python3
"""
测试任务_1772562601 - Todo 管理器核心功能验证
验证 Todo 管理器的所有核心功能
"""

import json
import os
import subprocess
import sys
import unittest
from io import StringIO
from unittest.mock import patch

import todo


class TestTaskCreation(unittest.TestCase):
    """任务创建功能测试"""

    def setUp(self):
        """测试前准备：创建干净的测试环境"""
        self.test_file = "test_1772562601.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理：删除测试文件"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_basic_task(self):
        """测试添加基本任务"""
        todo.add_task("基本任务")
        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["content"], "基本任务")
        self.assertFalse(tasks[0]["done"])

    def test_add_task_with_priority(self):
        """测试添加不同优先级的任务"""
        todo.add_task("高优先级任务", "高")
        todo.add_task("中优先级任务", "中")
        todo.add_task("低优先级任务", "低")
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["priority"], "高")
        self.assertEqual(tasks[1]["priority"], "中")
        self.assertEqual(tasks[2]["priority"], "低")

    def test_add_task_with_due_date(self):
        """测试添加带截止日期的任务"""
        due_date = "2026-12-31"
        todo.add_task("带截止日期任务", "中", due_date)
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["due_date"], due_date)

    def test_add_task_with_tags(self):
        """测试添加带标签的任务"""
        tags = ["工作", "测试"]
        todo.add_task("带标签任务", "中", None, tags)
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["tags"], tags)

    def test_task_auto_increment_id(self):
        """测试任务 ID 自动递增"""
        todo.add_task("任务 1")
        todo.add_task("任务 2")
        todo.add_task("任务 3")
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["id"], 1)
        self.assertEqual(tasks[1]["id"], 2)
        self.assertEqual(tasks[2]["id"], 3)

    def test_task_timestamp_creation(self):
        """测试任务创建时自动生成时间戳"""
        todo.add_task("时间戳任务")
        tasks = todo.load_tasks()
        self.assertIn("created_at", tasks[0])
        self.assertIsNotNone(tasks[0]["created_at"])


class TestTaskListing(unittest.TestCase):
    """任务列表功能测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_list_1772562601.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_list_empty_tasks(self):
        """测试列出空任务列表"""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            todo.list_tasks()
            output = mock_stdout.getvalue()
            self.assertIn("暂无任务", output)

    def test_list_tasks_with_priority_sort(self):
        """测试按优先级排序列出任务"""
        todo.add_task("低优先级", "低")
        todo.add_task("高优先级", "高")
        todo.add_task("中优先级", "中")
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            todo.list_tasks(sort_by="priority")
            output = mock_stdout.getvalue()
            high_pos = output.find("高优先级")
            medium_pos = output.find("中优先级")
            low_pos = output.find("低优先级")
            self.assertLess(high_pos, medium_pos)
            self.assertLess(medium_pos, low_pos)

    def test_list_filter_by_priority(self):
        """测试按优先级过滤任务"""
        todo.add_task("高优先级任务", "高")
        todo.add_task("中优先级任务", "中")
        todo.add_task("低优先级任务", "低")
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            todo.list_tasks(priority_filter="高")
            output = mock_stdout.getvalue()
            self.assertIn("高优先级任务", output)
            self.assertNotIn("中优先级任务", output)
            self.assertNotIn("低优先级任务", output)

    def test_list_filter_by_tag(self):
        """测试按标签过滤任务"""
        todo.add_task("任务 1", "中", None, ["工作"])
        todo.add_task("任务 2", "中", None, ["测试"])
        todo.add_task("任务 3", "中", None, ["工作", "测试"])
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            todo.list_tasks(tag_filter="工作")
            output = mock_stdout.getvalue()
            self.assertIn("任务 1", output)
            self.assertIn("任务 3", output)
            self.assertNotIn("任务 2", output)


class TestTaskCompletion(unittest.TestCase):
    """任务完成功能测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_done_1772562601.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_mark_task_done(self):
        """测试标记任务完成"""
        todo.add_task("待完成任务")
        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            todo.done_task(task_id)
            output = mock_stdout.getvalue()
            self.assertIn("已完成", output)
        tasks = todo.load_tasks()
        self.assertTrue(tasks[0]["done"])

    def test_mark_nonexistent_task_done(self):
        """测试标记不存在的任务完成"""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            todo.done_task(999)
            output = mock_stdout.getvalue()
            self.assertIn("未找到任务", output)


class TestTaskDeletion(unittest.TestCase):
    """任务删除功能测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_delete_1772562601.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_delete_task(self):
        """测试删除任务"""
        todo.add_task("待删除任务")
        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            todo.delete_task(task_id)
            output = mock_stdout.getvalue()
            self.assertIn("已删除", output)
        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 0)

    def test_delete_task_renumbers(self):
        """测试删除任务后重新编号"""
        todo.add_task("任务 1")
        todo.add_task("任务 2")
        todo.add_task("任务 3")
        todo.delete_task(2)
        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["id"], 1)
        self.assertEqual(tasks[1]["id"], 2)

    def test_delete_nonexistent_task(self):
        """测试删除不存在的任务"""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            todo.delete_task(999)
            output = mock_stdout.getvalue()
            self.assertIn("未找到任务", output)


class TestTagManagement(unittest.TestCase):
    """标签管理功能测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tags_1772562601.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_tag(self):
        """测试添加标签"""
        todo.add_task("测试任务")
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            todo.add_tag(1, "工作")
            output = mock_stdout.getvalue()
            self.assertIn("添加标签", output)
        tasks = todo.load_tasks()
        self.assertIn("工作", tasks[0]["tags"])

    def test_remove_tag(self):
        """测试移除标签"""
        todo.add_task("测试任务", "中", None, ["工作", "测试"])
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            todo.remove_tag(1, "工作")
            output = mock_stdout.getvalue()
            self.assertIn("移除标签", output)
        tasks = todo.load_tasks()
        self.assertNotIn("工作", tasks[0]["tags"])
        self.assertIn("测试", tasks[0]["tags"])


class TestPriorityManagement(unittest.TestCase):
    """优先级管理功能测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_priority_1772562601.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_set_priority(self):
        """测试修改优先级"""
        todo.add_task("测试任务", "中")
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            todo.set_priority(1, "高")
            output = mock_stdout.getvalue()
            self.assertIn("优先级已修改", output)
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["priority"], "高")

    def test_set_priority_nonexistent_task(self):
        """测试修改不存在任务的优先级"""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            todo.set_priority(999, "高")
            output = mock_stdout.getvalue()
            self.assertIn("未找到任务", output)


class TestExport(unittest.TestCase):
    """导出功能测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_export_1772562601.json"
        todo.TASKS_FILE = self.test_file
        self.csv_file = "test_export_1772562601.csv"
        self.md_file = "test_export_1772562601.md"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(self.csv_file):
            os.remove(self.csv_file)
        if os.path.exists(self.md_file):
            os.remove(self.md_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(self.csv_file):
            os.remove(self.csv_file)
        if os.path.exists(self.md_file):
            os.remove(self.md_file)

    def test_export_csv(self):
        """测试 CSV 导出"""
        todo.add_task("CSV 测试任务", "高", "2026-12-31", ["测试"])
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            todo.export_csv(self.csv_file)
            output = mock_stdout.getvalue()
            self.assertIn("已导出", output)
        self.assertTrue(os.path.exists(self.csv_file))

    def test_export_markdown(self):
        """测试 Markdown 导出"""
        todo.add_task("Markdown 测试任务", "中")
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            todo.export_markdown(self.md_file)
            output = mock_stdout.getvalue()
            self.assertIn("已导出", output)
        self.assertTrue(os.path.exists(self.md_file))


class TestStats(unittest.TestCase):
    """统计功能测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_stats_1772562601.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_stats_empty(self):
        """测试空任务列表的统计"""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            todo.stats()
            output = mock_stdout.getvalue()
            self.assertIn("暂无任务", output)

    def test_stats_with_tasks(self):
        """测试有任务时的统计"""
        todo.add_task("高优先级任务", "高")
        todo.add_task("中优先级任务", "中")
        todo.add_task("低优先级任务", "低")
        todo.done_task(1)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            todo.stats()
            output = mock_stdout.getvalue()
            self.assertIn("总计", output)
            self.assertIn("高优先级", output)
            self.assertIn("中优先级", output)
            self.assertIn("低优先级", output)


class TestCLIIntegration(unittest.TestCase):
    """CLI 集成测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_cli_1772562601.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_cli_add(self):
        """测试 CLI add 命令"""
        with patch.object(sys, "argv", ["todo", "add", "CLI 测试任务"]):
            todo.main()
        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["content"], "CLI 测试任务")

    def test_cli_list(self):
        """测试 CLI list 命令"""
        todo.add_task("CLI 列表测试")
        output = StringIO()
        with patch.object(sys, "argv", ["todo", "list"]):
            with patch.object(sys, "stdout", output):
                todo.main()
        result = output.getvalue()
        self.assertIn("CLI 列表测试", result)

    def test_cli_done(self):
        """测试 CLI done 命令"""
        todo.add_task("CLI 完成测试")
        with patch.object(sys, "argv", ["todo", "done", "1"]):
            todo.main()
        tasks = todo.load_tasks()
        self.assertTrue(tasks[0]["done"])

    def test_cli_delete(self):
        """测试 CLI delete 命令"""
        todo.add_task("CLI 删除测试")
        with patch.object(sys, "argv", ["todo", "delete", "1"]):
            todo.main()
        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 0)

    def test_cli_stats(self):
        """测试 CLI stats 命令"""
        todo.add_task("统计测试", "高")
        output = StringIO()
        with patch.object(sys, "argv", ["todo", "stats"]):
            with patch.object(sys, "stdout", output):
                todo.main()
        result = output.getvalue()
        self.assertIn("任务统计", result)

    def test_cli_export_csv(self):
        """测试 CLI export csv 命令"""
        todo.add_task("导出测试")
        with patch.object(
            sys,
            "argv",
            [
                "todo",
                "export",
                "--format",
                "csv",
                "--output",
                self.test_file.replace(".json", ".csv"),
            ],
        ):
            todo.main()
        self.assertTrue(os.path.exists(self.test_file.replace(".json", ".csv")))


class TestLoadSaveTasks(unittest.TestCase):
    """任务加载保存功能测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_loadsave_1772562601.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_load_nonexistent_file(self):
        """测试加载不存在的文件"""
        tasks = todo.load_tasks()
        self.assertEqual(tasks, [])

    def test_save_and_load(self):
        """测试保存和加载"""
        test_tasks = [{"id": 1, "content": "测试任务", "done": False, "priority": "中"}]
        todo.save_tasks(test_tasks)
        loaded_tasks = todo.load_tasks()
        self.assertEqual(len(loaded_tasks), 1)
        self.assertEqual(loaded_tasks[0]["content"], "测试任务")

    def test_backward_compatibility(self):
        """测试向后兼容性：为旧任务添加默认优先级"""
        test_tasks = [{"id": 1, "content": "旧任务", "done": False}]
        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(test_tasks, f, ensure_ascii=False, indent=2)
        loaded_tasks = todo.load_tasks()
        self.assertEqual(loaded_tasks[0]["priority"], "中")


if __name__ == "__main__":
    unittest.main()
