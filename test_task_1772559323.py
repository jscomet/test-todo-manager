#!/usr/bin/env python3
"""
测试任务_1772559323 - Todo 管理器功能测试
验证 Todo 管理器的各项功能
"""

import json
import os
import unittest
from io import StringIO
from unittest.mock import patch

import todo


class TestAddTask(unittest.TestCase):
    """添加任务功能测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_1772559323.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_simple_task(self):
        """测试添加简单任务"""
        todo.add_task("简单任务", "中")
        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["content"], "简单任务")
        self.assertEqual(tasks[0]["priority"], "中")
        self.assertFalse(tasks[0]["done"])

    def test_add_task_with_priority(self):
        """测试添加不同优先级任务"""
        todo.add_task("高优先任务", "高")
        todo.add_task("中优先任务", "中")
        todo.add_task("低优先任务", "低")

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 3)
        self.assertEqual(tasks[0]["priority"], "高")
        self.assertEqual(tasks[1]["priority"], "中")
        self.assertEqual(tasks[2]["priority"], "低")

    def test_add_task_with_due_date(self):
        """测试添加带截止日期任务"""
        todo.add_task("有截止日期的任务", "中", due_date="2026-12-31")
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["due_date"], "2026-12-31")

    def test_add_task_with_tags(self):
        """测试添加带标签任务"""
        todo.add_task("有标签的任务", "中", tags=["工作", "紧急"])
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["tags"], ["工作", "紧急"])

    def test_add_task_with_all_fields(self):
        """测试添加完整字段任务"""
        todo.add_task("完整任务", "高", due_date="2026-06-30", tags=["测试", "验证"])
        tasks = todo.load_tasks()
        task = tasks[0]
        self.assertEqual(task["content"], "完整任务")
        self.assertEqual(task["priority"], "高")
        self.assertEqual(task["due_date"], "2026-06-30")
        self.assertEqual(task["tags"], ["测试", "验证"])
        self.assertFalse(task["done"])
        self.assertIn("created_at", task)


class TestListTasks(unittest.TestCase):
    """列表任务功能测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_list_1772559323.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_list_empty_tasks(self):
        """测试空列表"""
        captured = StringIO()
        with patch("sys.stdout", captured):
            todo.list_tasks()
        output = captured.getvalue()
        self.assertIn("暂无任务", output)

    def test_list_with_tasks(self):
        """测试有任务时列表"""
        todo.add_task("任务 1", "高")
        todo.add_task("任务 2", "中")

        captured = StringIO()
        with patch("sys.stdout", captured):
            todo.list_tasks()
        output = captured.getvalue()
        self.assertIn("任务 1", output)
        self.assertIn("任务 2", output)

    def test_list_filter_by_priority(self):
        """测试按优先级过滤"""
        todo.add_task("高优先", "高")
        todo.add_task("中优先", "中")
        todo.add_task("低优先", "低")

        captured = StringIO()
        with patch("sys.stdout", captured):
            todo.list_tasks(priority_filter="高")
        output = captured.getvalue()
        self.assertIn("高优先", output)
        self.assertNotIn("中优先", output)
        self.assertNotIn("低优先", output)

    def test_list_filter_by_tag(self):
        """测试按标签过滤"""
        todo.add_task("工作任务", "中", tags=["工作"])
        todo.add_task("生活任务", "中", tags=["生活"])

        captured = StringIO()
        with patch("sys.stdout", captured):
            todo.list_tasks(tag_filter="工作")
        output = captured.getvalue()
        self.assertIn("工作任务", output)
        self.assertNotIn("生活任务", output)

    def test_list_sort_by_priority(self):
        """测试按优先级排序"""
        todo.add_task("低优先", "低")
        todo.add_task("高优先", "高")
        todo.add_task("中优先", "中")

        captured = StringIO()
        with patch("sys.stdout", captured):
            todo.list_tasks(sort_by="priority")
        output = captured.getvalue()

        high_pos = output.find("高优先")
        mid_pos = output.find("中优先")
        low_pos = output.find("低优先")

        self.assertLess(high_pos, mid_pos)
        self.assertLess(mid_pos, low_pos)


class TestMarkDone(unittest.TestCase):
    """标记完成任务测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_done_1772559323.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_mark_task_done(self):
        """测试标记任务完成"""
        todo.add_task("待完成任务", "中")
        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]

        todo.done_task(task_id)
        tasks = todo.load_tasks()
        self.assertTrue(tasks[0]["done"])

    def test_mark_nonexistent_task(self):
        """测试标记不存在任务"""
        captured = StringIO()
        with patch("sys.stdout", captured):
            todo.done_task(999)
        output = captured.getvalue()
        self.assertIn("未找到任务", output)


class TestDeleteTask(unittest.TestCase):
    """删除任务功能测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_delete_1772559323.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_delete_task(self):
        """测试删除任务"""
        todo.add_task("待删除任务", "中")
        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]

        todo.delete_task(task_id)
        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 0)

    def test_delete_renumbers_ids(self):
        """测试删除后 ID 重新编号"""
        todo.add_task("任务 1", "中")
        todo.add_task("任务 2", "中")
        todo.add_task("任务 3", "中")

        todo.delete_task(2)
        tasks = todo.load_tasks()

        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["id"], 1)
        self.assertEqual(tasks[1]["id"], 2)

    def test_delete_nonexistent(self):
        """测试删除不存在任务"""
        captured = StringIO()
        with patch("sys.stdout", captured):
            todo.delete_task(999)
        output = captured.getvalue()
        self.assertIn("未找到任务", output)


class TestTags(unittest.TestCase):
    """标签功能测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tags_1772559323.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_tag(self):
        """测试添加标签"""
        todo.add_task("标签测试", "中")
        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]

        todo.add_tag(task_id, "测试")
        tasks = todo.load_tasks()
        self.assertIn("测试", tasks[0]["tags"])

    def test_add_duplicate_tag(self):
        """测试防止重复标签"""
        todo.add_task("重复标签", "中", tags=["测试"])
        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]

        captured = StringIO()
        with patch("sys.stdout", captured):
            todo.add_tag(task_id, "测试")
        output = captured.getvalue()
        self.assertIn("已存在", output)

    def test_remove_tag(self):
        """测试移除标签"""
        todo.add_task("移除标签", "中", tags=["标签 1", "标签 2"])
        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]

        todo.remove_tag(task_id, "标签 1")
        tasks = todo.load_tasks()
        self.assertNotIn("标签 1", tasks[0]["tags"])
        self.assertIn("标签 2", tasks[0]["tags"])

    def test_remove_nonexistent_tag(self):
        """测试移除不存在标签"""
        todo.add_task("无此标签", "中", tags=["现有"])
        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]

        captured = StringIO()
        with patch("sys.stdout", captured):
            todo.remove_tag(task_id, "不存在")
        output = captured.getvalue()
        self.assertIn("不存在", output)


class TestPriority(unittest.TestCase):
    """优先级功能测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_priority_1772559323.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_set_priority(self):
        """测试修改优先级"""
        todo.add_task("优先级修改", "中")
        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]

        todo.set_priority(task_id, "高")
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["priority"], "高")

    def test_set_priority_nonexistent(self):
        """测试修改不存在任务优先级"""
        captured = StringIO()
        with patch("sys.stdout", captured):
            todo.set_priority(999, "高")
        output = captured.getvalue()
        self.assertIn("未找到任务", output)


class TestExport(unittest.TestCase):
    """导出功能测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_export_1772559323.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_export_csv(self):
        """测试 CSV 导出"""
        todo.add_task("CSV 任务", "高", "2026-12-31", ["测试"])

        csv_file = "test_1772559323.csv"
        todo.export_csv(csv_file)

        with open(csv_file, "r", encoding="utf-8-sig") as f:
            content = f.read()

        self.assertIn("CSV 任务", content)
        self.assertIn("高", content)
        self.assertIn("2026-12-31", content)
        self.assertIn("测试", content)

        os.remove(csv_file)

    def test_export_markdown(self):
        """测试 Markdown 导出"""
        todo.add_task("MD 任务", "中")

        md_file = "test_1772559323.md"
        todo.export_markdown(md_file)

        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("MD 任务", content)
        self.assertIn("⭕", content)
        self.assertIn("总计", content)

        os.remove(md_file)

    def test_export_empty(self):
        """测试导出空任务"""
        captured = StringIO()
        with patch("sys.stdout", captured):
            todo.export_csv()
        output = captured.getvalue()
        self.assertIn("暂无任务", output)


class TestBackwardCompatibility(unittest.TestCase):
    """向后兼容性测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_compat_1772559323.json"
        todo.TASKS_FILE = self.test_file

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_old_tasks_get_default_priority(self):
        """测试旧任务自动获取默认优先级"""
        old_tasks = [
            {"id": 1, "content": "旧任务 1", "done": False},
            {"id": 2, "content": "旧任务 2", "done": True, "priority": "高"},
        ]

        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(old_tasks, f, ensure_ascii=False, indent=2)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["priority"], "中")
        self.assertEqual(tasks[1]["priority"], "高")


class TestEdgeCases(unittest.TestCase):
    """边界情况测试"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_edge_1772559323.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_chinese_comma_in_tags(self):
        """测试中文逗号标签分割"""
        todo.add_task("中文逗号测试", "中", tags=["工作，紧急"])
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["tags"], ["工作，紧急"])

    def test_empty_tags_list(self):
        """测试空标签列表（不保存 tags 字段）"""
        todo.add_task("空标签", "中", tags=[])
        tasks = todo.load_tasks()
        self.assertNotIn("tags", tasks[0])

    def test_special_characters_in_content(self):
        """测试特殊字符内容"""
        todo.add_task("特殊字符测试：@#$%", "中")
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["content"], "特殊字符测试：@#$%")


if __name__ == "__main__":
    print("=" * 60)
    print("测试任务_1772559323 - Todo 管理器功能测试")
    print("=" * 60)
    unittest.main(verbosity=2)
