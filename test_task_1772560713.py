#!/usr/bin/env python3
"""
测试任务_1772560713 - Todo 管理器核心功能验证
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
        self.test_file = "test_1772560713.json"
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
        self.test_file = "test_list_1772560713.json"
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


class TestTaskCompletion(unittest.TestCase):
    """任务完成功能测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_done_1772560713.json"
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
        todo.done_task(task_id)
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
        self.test_file = "test_delete_1772560713.json"
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
        todo.delete_task(task_id)
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


class TestTagManagement(unittest.TestCase):
    """标签管理功能测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tags_1772560713.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_tag(self):
        """测试添加标签"""
        todo.add_task("带标签任务")
        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]
        todo.add_tag(task_id, "测试")
        tasks = todo.load_tasks()
        self.assertIn("测试", tasks[0]["tags"])

    def test_remove_tag(self):
        """测试移除标签"""
        todo.add_task("带标签任务", "中", None, ["测试", "工作"])
        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]
        todo.remove_tag(task_id, "工作")
        tasks = todo.load_tasks()
        self.assertIn("测试", tasks[0]["tags"])
        self.assertNotIn("工作", tasks[0]["tags"])


class TestPriorityManagement(unittest.TestCase):
    """优先级管理功能测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_priority_1772560713.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_set_priority(self):
        """测试设置任务优先级"""
        todo.add_task("中优先级任务", "中")
        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]
        todo.set_priority(task_id, "高")
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["priority"], "高")


class TestStatistics(unittest.TestCase):
    """统计功能测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_stats_1772560713.json"
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
            self.assertIn("总计：3 个任务", output)
            self.assertIn("高优先级", output)


class TestExport(unittest.TestCase):
    """导出功能测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_export_1772560713.json"
        self.csv_file = "test_export_1772560713.csv"
        self.md_file = "test_export_1772560713.md"
        todo.TASKS_FILE = self.test_file
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
        """测试导出 CSV 格式"""
        todo.add_task("测试任务", "高")
        todo.export_csv(self.csv_file)
        self.assertTrue(os.path.exists(self.csv_file))
        with open(self.csv_file, "r", encoding="utf-8-sig") as f:
            content = f.read()
            self.assertIn("测试任务", content)

    def test_export_markdown(self):
        """测试导出 Markdown 格式"""
        todo.add_task("测试任务", "高")
        todo.export_markdown(self.md_file)
        self.assertTrue(os.path.exists(self.md_file))
        with open(self.md_file, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("测试任务", content)


class TestCLIBackwardCompatibility(unittest.TestCase):
    """向后兼容性测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_compat_1772560713.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_load_tasks_without_priority(self):
        """测试加载没有优先级字段的老任务"""
        old_task = {
            "id": 1,
            "content": "老任务",
            "done": False,
            "created_at": "2026-01-01 00:00:00",
        }
        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump([old_task], f, ensure_ascii=False, indent=2)
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["priority"], "中")


if __name__ == "__main__":
    unittest.main()
