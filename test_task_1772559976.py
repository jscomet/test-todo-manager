#!/usr/bin/env python3
"""
测试任务_1772559976 - Todo 管理器全面功能验证
验证 Todo 管理器的所有核心功能和 CLI 交互
"""

import json
import os
import subprocess
import unittest
from io import StringIO
from unittest.mock import patch

import todo


class TestTaskAddition(unittest.TestCase):
    """任务添加功能测试"""

    def setUp(self):
        """测试前准备：创建干净的测试环境"""
        self.test_file = "test_1772559976.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理：删除测试文件"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_task_default_priority(self):
        """测试添加任务时默认优先级为中"""
        todo.add_task("默认优先级任务")
        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["priority"], "中")

    def test_add_task_with_high_priority(self):
        """测试添加高优先级任务"""
        todo.add_task("高优先级任务", "高")
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["priority"], "高")

    def test_add_task_with_low_priority(self):
        """测试添加低优先级任务"""
        todo.add_task("低优先级任务", "低")
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["priority"], "低")

    def test_add_task_with_due_date(self):
        """测试添加带截止日期的任务"""
        due_date = "2026-12-31"
        todo.add_task("带截止日期任务", "中", due_date)
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["due_date"], due_date)

    def test_add_task_without_due_date(self):
        """测试添加不带截止日期的任务"""
        todo.add_task("无截止日期任务")
        tasks = todo.load_tasks()
        self.assertNotIn("due_date", tasks[0])

    def test_add_task_with_tags(self):
        """测试添加带标签的任务"""
        tags = ["工作", "紧急"]
        todo.add_task("带标签任务", "中", None, tags)
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["tags"], tags)

    def test_add_task_without_tags(self):
        """测试添加不带标签的任务"""
        todo.add_task("无标签任务")
        tasks = todo.load_tasks()
        self.assertNotIn("tags", tasks[0])

    def test_add_task_creates_timestamp(self):
        """测试添加任务时自动创建时间戳"""
        todo.add_task("时间戳任务")
        tasks = todo.load_tasks()
        self.assertIn("created_at", tasks[0])
        self.assertIsNotNone(tasks[0]["created_at"])

    def test_add_task_auto_increment_id(self):
        """测试任务 ID 自动递增"""
        todo.add_task("任务 1")
        todo.add_task("任务 2")
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["id"], 1)
        self.assertEqual(tasks[1]["id"], 2)


class TestTaskListing(unittest.TestCase):
    """任务列表功能测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_list_1772559976.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_list_empty_tasks(self):
        """测试空任务列表显示"""
        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.list_tasks()
        output = captured_output.getvalue()
        self.assertIn("暂无任务", output)

    def test_list_with_tasks(self):
        """测试有任务时的列表显示"""
        todo.add_task("任务 A", "高")
        todo.add_task("任务 B", "中")
        todo.add_task("任务 C", "低")

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.list_tasks(sort_by="none")
        output = captured_output.getvalue()

        self.assertIn("任务 A", output)
        self.assertIn("任务 B", output)
        self.assertIn("任务 C", output)
        self.assertIn("🔴", output)
        self.assertIn("🟡", output)
        self.assertIn("🟢", output)

    def test_list_priority_sorting(self):
        """测试按优先级排序"""
        todo.add_task("低优先级", "低")
        todo.add_task("高优先级", "高")
        todo.add_task("中优先级", "中")

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.list_tasks(sort_by="priority")
        output = captured_output.getvalue()

        high_pos = output.find("高优先级")
        mid_pos = output.find("中优先级")
        low_pos = output.find("低优先级")

        self.assertLess(high_pos, mid_pos)
        self.assertLess(mid_pos, low_pos)

    def test_list_filter_by_priority(self):
        """测试按优先级过滤"""
        todo.add_task("高优 1", "高")
        todo.add_task("中优 1", "中")
        todo.add_task("高优 2", "高")

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.list_tasks(priority_filter="高")
        output = captured_output.getvalue()

        self.assertIn("高优 1", output)
        self.assertIn("高优 2", output)
        self.assertNotIn("中优 1", output)

    def test_list_filter_by_tag(self):
        """测试按标签过滤"""
        todo.add_task("工作 1", tags=["工作"])
        todo.add_task("生活 1", tags=["生活"])
        todo.add_task("工作 2", tags=["工作", "紧急"])

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.list_tasks(tag_filter="工作")
        output = captured_output.getvalue()

        self.assertIn("工作 1", output)
        self.assertIn("工作 2", output)
        self.assertNotIn("生活 1", output)

    def test_list_empty_with_filter(self):
        """测试过滤后无结果的提示"""
        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.list_tasks(priority_filter="高")
        output = captured_output.getvalue()
        self.assertIn("没有找到优先级为 '高' 的任务", output)

    def test_list_shows_due_date(self):
        """测试列表显示截止日期"""
        todo.add_task("带截止日期任务", due_date="2026-03-10")
        
        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.list_tasks()
        output = captured_output.getvalue()
        
        self.assertIn("📅 2026-03-10", output)

    def test_list_shows_tags(self):
        """测试列表显示标签"""
        todo.add_task("带标签任务", tags=["测试", "验证"])
        
        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.list_tasks()
        output = captured_output.getvalue()
        
        self.assertIn("#测试", output)
        self.assertIn("#验证", output)


class TestTaskCompletion(unittest.TestCase):
    """任务完成功能测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_done_1772559976.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_done_task_basic(self):
        """测试基本标记完成功能"""
        todo.add_task("待完成任务")
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

    def test_done_task_message(self):
        """测试完成任务的提示信息"""
        todo.add_task("具体任务内容")
        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.done_task(task_id)
        output = captured_output.getvalue()
        self.assertIn("具体任务内容", output)


class TestTaskDeletion(unittest.TestCase):
    """任务删除功能测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_delete_1772559976.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_delete_task_basic(self):
        """测试基本删除功能"""
        todo.add_task("待删除任务")
        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]

        todo.delete_task(task_id)
        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 0)

    def test_delete_renumbers_ids(self):
        """测试删除后 ID 重新编号"""
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
        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.delete_task(999)
        output = captured_output.getvalue()
        self.assertIn("未找到任务", output)


class TestTagManagement(unittest.TestCase):
    """标签管理功能测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tags_1772559976.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_tag_basic(self):
        """测试基本添加标签"""
        todo.add_task("标签测试任务")
        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]

        todo.add_tag(task_id, "测试标签")
        tasks = todo.load_tasks()
        self.assertIn("测试标签", tasks[0]["tags"])

    def test_add_tag_prevents_duplicates(self):
        """测试防止重复添加标签"""
        todo.add_task("重复标签测试", tags=["已有标签"])
        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.add_tag(task_id, "已有标签")
        output = captured_output.getvalue()
        self.assertIn("已存在", output)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks[0]["tags"]), 1)

    def test_remove_tag_basic(self):
        """测试基本移除标签"""
        todo.add_task("标签移除测试", tags=["标签 1", "标签 2"])
        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]

        todo.remove_tag(task_id, "标签 1")
        tasks = todo.load_tasks()
        self.assertNotIn("标签 1", tasks[0]["tags"])
        self.assertIn("标签 2", tasks[0]["tags"])

    def test_remove_nonexistent_tag(self):
        """测试移除不存在的标签"""
        todo.add_task("标签测试", tags=["标签 1"])
        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.remove_tag(task_id, "不存在的标签")
        output = captured_output.getvalue()
        self.assertIn("不存在", output)

    def test_add_tag_to_nonexistent_task(self):
        """测试给不存在的任务添加标签"""
        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.add_tag(999, "标签")
        output = captured_output.getvalue()
        self.assertIn("未找到任务", output)

    def test_remove_tag_from_nonexistent_task(self):
        """测试从不存在的任务移除标签"""
        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.remove_tag(999, "标签")
        output = captured_output.getvalue()
        self.assertIn("未找到任务", output)


class TestPriorityManagement(unittest.TestCase):
    """优先级管理功能测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_priority_1772559976.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_set_priority_basic(self):
        """测试基本修改优先级"""
        todo.add_task("优先级修改任务", "中")
        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]

        todo.set_priority(task_id, "高")
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["priority"], "高")

    def test_set_priority_all_levels(self):
        """测试设置所有优先级级别"""
        todo.add_task("测试任务", "中")
        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]

        for priority in ["高", "中", "低"]:
            todo.set_priority(task_id, priority)
            tasks = todo.load_tasks()
            self.assertEqual(tasks[0]["priority"], priority)

    def test_set_priority_nonexistent_task(self):
        """测试修改不存在的任务优先级"""
        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.set_priority(999, "高")
        output = captured_output.getvalue()
        self.assertIn("未找到任务", output)

    def test_set_priority_message(self):
        """测试修改优先级的提示信息"""
        todo.add_task("优先级测试内容", "中")
        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.set_priority(task_id, "高")
        output = captured_output.getvalue()
        
        self.assertIn("中 → 高", output)
        self.assertIn("优先级测试内容", output)


class TestExportFunctionality(unittest.TestCase):
    """导出功能测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_export_1772559976.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        for f in ["test_export.csv", "test_export.md"]:
            if os.path.exists(f):
                os.remove(f)

    def test_export_csv_basic(self):
        """测试基本 CSV 导出"""
        todo.add_task("CSV 导出测试", "高", "2026-12-31", ["测试"])
        todo.add_task("CSV 测试 2", "中")

        todo.export_csv("test_export.csv")
        self.assertTrue(os.path.exists("test_export.csv"))

        with open("test_export.csv", "r", encoding="utf-8-sig") as f:
            content = f.read()

        self.assertIn("CSV 导出测试", content)
        self.assertIn("高", content)
        self.assertIn("2026-12-31", content)
        self.assertIn("测试", content)

    def test_export_markdown_basic(self):
        """测试基本 Markdown 导出"""
        todo.add_task("MD 导出测试", "中")
        todo.done_task(1)

        todo.export_markdown("test_export.md")
        self.assertTrue(os.path.exists("test_export.md"))

        with open("test_export.md", "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("MD 导出测试", content)
        self.assertIn("✅", content)
        self.assertIn("统计信息", content)

    def test_export_empty_tasks(self):
        """测试导出空任务列表"""
        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.export_csv()
        output = captured_output.getvalue()
        self.assertIn("暂无任务可导出", output)

    def test_export_default_filename(self):
        """测试默认导出文件名"""
        todo.add_task("测试任务")

        todo.export_csv()
        self.assertTrue(os.path.exists("tasks_export.csv"))
        os.remove("tasks_export.csv")

        todo.export_markdown()
        self.assertTrue(os.path.exists("tasks_export.md"))
        os.remove("tasks_export.md")

    def test_export_csv_headers(self):
        """测试 CSV 导出包含正确的表头"""
        todo.add_task("表头测试")
        
        todo.export_csv("test_export.csv")
        
        with open("test_export.csv", "r", encoding="utf-8-sig") as f:
            header = f.readline().strip()
        
        self.assertIn("ID", header)
        self.assertIn("内容", header)
        self.assertIn("状态", header)
        self.assertIn("优先级", header)

    def test_export_markdown_statistics(self):
        """测试 Markdown 导出包含统计信息"""
        todo.add_task("任务 1", "高")
        todo.add_task("任务 2", "中")
        todo.done_task(1)
        
        todo.export_markdown("test_export.md")
        
        with open("test_export.md", "r", encoding="utf-8") as f:
            content = f.read()
        
        self.assertIn("总计", content)
        self.assertIn("已完成", content)
        self.assertIn("待完成", content)


class TestStatistics(unittest.TestCase):
    """统计功能测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_stats_1772559976.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_stats_basic(self):
        """测试基本统计功能"""
        todo.add_task("高优任务", "高")
        todo.add_task("中优任务", "中")
        todo.add_task("低优任务", "低")

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.stats()
        output = captured_output.getvalue()

        self.assertIn("任务统计", output)
        self.assertIn("总计：3 个任务", output)
        self.assertIn("🔴 高优先级", output)
        self.assertIn("🟡 中优先级", output)
        self.assertIn("🟢 低优先级", output)

    def test_stats_with_completion(self):
        """测试带完成情况的统计"""
        todo.add_task("任务 1", "高")
        todo.add_task("任务 2", "高")
        todo.done_task(1)

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.stats()
        output = captured_output.getvalue()

        self.assertIn("✅ 已完成：1", output)
        self.assertIn("⭕ 待完成：1", output)

    def test_stats_empty(self):
        """测试空任务统计"""
        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.stats()
        output = captured_output.getvalue()
        self.assertIn("暂无任务", output)

    def test_stats_filter_by_tag(self):
        """测试按标签过滤统计"""
        todo.add_task("工作 1", tags=["工作"])
        todo.add_task("工作 2", tags=["工作"])
        todo.add_task("生活 1", tags=["生活"])

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.stats(tag_filter="工作")
        output = captured_output.getvalue()

        self.assertIn("总计：2 个任务", output)
        self.assertNotIn("生活 1", output)

    def test_stats_filter_by_priority(self):
        """测试按优先级过滤统计"""
        todo.add_task("高优 1", "高")
        todo.add_task("高优 2", "高")
        todo.add_task("中优 1", "中")

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.stats(priority_filter="高")
        output = captured_output.getvalue()

        self.assertIn("总计：2 个任务", output)
        self.assertIn("🔴 高优先级", output)


class TestBackwardCompatibility(unittest.TestCase):
    """向后兼容性测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_compat_1772559976.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_old_tasks_get_default_priority(self):
        """测试旧任务自动获取默认优先级"""
        old_tasks = [
            {"id": 1, "content": "旧任务 1", "done": False},
            {"id": 2, "content": "旧任务 2", "done": True, "priority": "高"},
            {"id": 3, "content": "旧任务 3", "done": False},
        ]

        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(old_tasks, f, ensure_ascii=False, indent=2)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 3)
        self.assertEqual(tasks[0]["priority"], "中")
        self.assertEqual(tasks[1]["priority"], "高")
        self.assertEqual(tasks[2]["priority"], "中")

    def test_old_tasks_without_tags_field(self):
        """测试旧任务没有 tags 字段时正常加载"""
        old_tasks = [
            {"id": 1, "content": "无标签旧任务", "done": False},
        ]

        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(old_tasks, f, ensure_ascii=False, indent=2)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertNotIn("tags", tasks[0])


class TestCLIIntegration(unittest.TestCase):
    """CLI 集成测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_cli_1772559976.json"
        self.cwd = os.path.dirname(os.path.abspath(__file__))

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_cli_add_task(self):
        """测试 CLI 添加任务"""
        env = os.environ.copy()
        env["TASKS_FILE"] = self.test_file
        
        result = subprocess.run(
            [
                "python3",
                "todo.py",
                "add",
                "CLI 测试任务",
                "--priority",
                "高",
                "--due",
                "2026-12-31",
                "--tags",
                "测试，CLI",
            ],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            env=env,
        )
        self.assertIn("已添加任务", result.stdout)

    def test_cli_list_help(self):
        """测试 CLI list 帮助"""
        result = subprocess.run(
            ["python3", "todo.py", "list", "--help"],
            capture_output=True,
            text=True,
            cwd=self.cwd,
        )
        self.assertIn("--priority", result.stdout)
        self.assertIn("--sort", result.stdout)

    def test_cli_help(self):
        """测试 CLI 帮助"""
        result = subprocess.run(
            ["python3", "todo.py", "--help"],
            capture_output=True,
            text=True,
            cwd=self.cwd,
        )
        self.assertIn("add", result.stdout)
        self.assertIn("list", result.stdout)
        self.assertIn("done", result.stdout)
        self.assertIn("delete", result.stdout)

    def test_cli_done_task(self):
        """测试 CLI 完成任务"""
        env = os.environ.copy()
        env["TASKS_FILE"] = self.test_file
        
        # 先添加任务
        subprocess.run(
            ["python3", "todo.py", "add", "CLI 完成测试"],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            env=env,
        )
        
        # 完成任务
        result = subprocess.run(
            ["python3", "todo.py", "done", "1"],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            env=env,
        )
        self.assertIn("已完成", result.stdout)

    def test_cli_delete_task(self):
        """测试 CLI 删除任务"""
        env = os.environ.copy()
        env["TASKS_FILE"] = self.test_file
        
        # 先添加任务
        subprocess.run(
            ["python3", "todo.py", "add", "CLI 删除测试"],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            env=env,
        )
        
        # 删除任务
        result = subprocess.run(
            ["python3", "todo.py", "delete", "1"],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            env=env,
        )
        self.assertIn("已删除", result.stdout)

    def test_cli_stats(self):
        """测试 CLI 统计"""
        env = os.environ.copy()
        env["TASKS_FILE"] = self.test_file
        
        # 添加任务
        subprocess.run(
            ["python3", "todo.py", "add", "统计测试", "--priority", "高"],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            env=env,
        )
        
        result = subprocess.run(
            ["python3", "todo.py", "stats"],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            env=env,
        )
        self.assertIn("任务统计", result.stdout)

    def test_cli_export_csv(self):
        """测试 CLI 导出 CSV"""
        env = os.environ.copy()
        env["TASKS_FILE"] = self.test_file
        
        subprocess.run(
            ["python3", "todo.py", "add", "导出测试"],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            env=env,
        )
        
        result = subprocess.run(
            ["python3", "todo.py", "export", "-f", "csv", "-o", "cli_test.csv"],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            env=env,
        )
        self.assertIn("已导出", result.stdout)
        
        if os.path.exists("cli_test.csv"):
            os.remove("cli_test.csv")

    def test_cli_set_priority(self):
        """测试 CLI 设置优先级"""
        env = os.environ.copy()
        env["TASKS_FILE"] = self.test_file
        
        subprocess.run(
            ["python3", "todo.py", "add", "优先级测试"],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            env=env,
        )
        
        result = subprocess.run(
            ["python3", "todo.py", "set-priority", "1", "高"],
            capture_output=True,
            text=True,
            cwd=self.cwd,
            env=env,
        )
        self.assertIn("优先级已修改", result.stdout)


class TestEdgeCases(unittest.TestCase):
    """边界情况测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_edge_1772559976.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_task_with_empty_content(self):
        """测试添加空内容任务"""
        todo.add_task("")
        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["content"], "")

    def test_add_task_with_special_characters(self):
        """测试添加包含特殊字符的任务"""
        content = "任务 & 测试 <tag> @mention #hashtag"
        todo.add_task(content)
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["content"], content)

    def test_add_task_with_chinese_commas(self):
        """测试使用中文逗号分割标签"""
        tags_list = [t.strip() for t in "工作，紧急，重要".replace("，", ",").split(",")]
        todo.add_task("标签测试", tags=tags_list)
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["tags"], ["工作", "紧急", "重要"])

    def test_load_tasks_from_nonexistent_file(self):
        """测试从不存在的文件加载任务"""
        tasks = todo.load_tasks()
        self.assertEqual(tasks, [])

    def test_save_and_load_tasks(self):
        """测试保存和加载任务的一致性"""
        todo.add_task("持久化测试", "高", "2026-12-31", ["测试"])
        
        # 重新加载任务
        loaded_tasks = todo.load_tasks()
        self.assertEqual(len(loaded_tasks), 1)
        self.assertEqual(loaded_tasks[0]["content"], "持久化测试")
        self.assertEqual(loaded_tasks[0]["priority"], "高")
        self.assertEqual(loaded_tasks[0]["due_date"], "2026-12-31")
        self.assertEqual(loaded_tasks[0]["tags"], ["测试"])


if __name__ == "__main__":
    print("=" * 60)
    print("测试任务_1772559976 - Todo 管理器全面功能验证")
    print("=" * 60)
    unittest.main(verbosity=2)
