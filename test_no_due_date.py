#!/usr/bin/env python3
"""
无截止日期任务专项测试
测试 Todo 管理器中无截止日期任务的各项功能
"""

import json
import os
import unittest
from io import StringIO
from unittest.mock import patch

import todo


class TestNoDueDateTasks(unittest.TestCase):
    """无截止日期任务测试类"""

    def setUp(self):
        """测试前准备：创建干净的测试环境"""
        self.test_file = "test_no_due_date.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理：删除测试文件"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_task_without_due_date(self):
        """测试添加无截止日期任务"""
        todo.add_task("无截止日期任务", "中")

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["content"], "无截止日期任务")
        self.assertNotIn("due_date", tasks[0])
        self.assertFalse(tasks[0]["done"])

    def test_add_multiple_no_due_date_tasks(self):
        """测试添加多个无截止日期任务"""
        todo.add_task("任务 1", "高")
        todo.add_task("任务 2", "中")
        todo.add_task("任务 3", "低")

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 3)
        for task in tasks:
            self.assertNotIn("due_date", task)

    def test_mix_due_and_no_due_date_tasks(self):
        """测试混合带截止日期和无截止日期的任务"""
        todo.add_task("有截止日期", "高", "2026-12-31")
        todo.add_task("无截止日期 1", "中")
        todo.add_task("无截止日期 2", "低")
        todo.add_task("有截止日期 2", "中", "2026-06-15")

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 4)

        has_due = [t for t in tasks if "due_date" in t]
        no_due = [t for t in tasks if "due_date" not in t]

        self.assertEqual(len(has_due), 2)
        self.assertEqual(len(no_due), 2)

    def test_list_no_due_date_tasks(self):
        """测试列表显示无截止日期任务"""
        todo.add_task("无截止日期任务", "中")
        todo.add_task("另一个无截止日期任务", "高")

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.list_tasks()

        output = captured_output.getvalue()
        self.assertIn("无截止日期任务", output)
        self.assertIn("另一个无截止日期任务", output)
        self.assertNotIn("📅", output)

    def test_no_due_date_task_sorting_by_priority(self):
        """测试无截止日期任务按优先级排序"""
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

    def test_no_due_date_task_priority_filter(self):
        """测试无截止日期任务按优先级过滤"""
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

    def test_no_due_date_task_with_tags(self):
        """测试无截止日期任务带标签"""
        tags = ["工作", "测试"]
        todo.add_task("带标签无截止日期", "中", tags=tags)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertNotIn("due_date", tasks[0])
        self.assertEqual(tasks[0]["tags"], tags)

    def test_no_due_date_task_done(self):
        """测试标记无截止日期任务为完成"""
        todo.add_task("待完成任务", "中")

        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]
        todo.done_task(task_id)

        tasks = todo.load_tasks()
        self.assertTrue(tasks[0]["done"])
        self.assertNotIn("due_date", tasks[0])

    def test_no_due_date_task_delete(self):
        """测试删除无截止日期任务"""
        todo.add_task("待删除任务", "中")

        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]
        todo.delete_task(task_id)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 0)

    def test_no_due_date_task_modify_priority(self):
        """测试修改无截止日期任务的优先级"""
        todo.add_task("修改优先级任务", "中")

        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]
        todo.set_priority(task_id, "高")

        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["priority"], "高")
        self.assertNotIn("due_date", tasks[0])

    def test_no_due_date_export_csv(self):
        """测试无截止日期任务导出 CSV"""
        todo.add_task("无截止日期任务", "中")

        test_csv = "test_no_due.csv"
        todo.export_csv(test_csv)

        with open(test_csv, "r", encoding="utf-8-sig") as f:
            content = f.read()

        self.assertIn("无截止日期任务", content)
        self.assertIn("待完成", content)

        os.remove(test_csv)

    def test_no_due_date_export_markdown(self):
        """测试无截止日期任务导出 Markdown"""
        todo.add_task("无截止日期任务", "中")

        test_md = "test_no_due.md"
        todo.export_markdown(test_md)

        with open(test_md, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("无截止日期任务", content)
        self.assertIn("⭕", content)

        os.remove(test_md)

    def test_no_due_date_task_add_tag(self):
        """测试为无截止日期任务添加标签"""
        todo.add_task("添加标签任务", "中")

        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]
        todo.add_tag(task_id, "新标签")

        tasks = todo.load_tasks()
        self.assertIn("新标签", tasks[0]["tags"])
        self.assertNotIn("due_date", tasks[0])

    def test_no_due_date_task_remove_tag(self):
        """测试从无截止日期任务移除标签"""
        todo.add_task("移除标签任务", "中", tags=["标签 1", "标签 2"])

        tasks = todo.load_tasks()
        task_id = tasks[0]["id"]
        todo.remove_tag(task_id, "标签 1")

        tasks = todo.load_tasks()
        self.assertNotIn("标签 1", tasks[0]["tags"])
        self.assertIn("标签 2", tasks[0]["tags"])

    def test_backward_compatibility_old_tasks(self):
        """测试向后兼容性：加载旧格式任务（无 due_date 字段）"""
        old_tasks = [
            {"id": 1, "content": "旧任务 1", "done": False},
            {"id": 2, "content": "旧任务 2", "done": True, "priority": "高"},
        ]

        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(old_tasks, f, ensure_ascii=False, indent=2)

        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 2)
        for task in tasks:
            self.assertNotIn("due_date", task)
            self.assertIn("priority", task)

    def test_no_due_date_list_display_format(self):
        """测试无截止日期任务列表显示格式（不显示日期图标）"""
        todo.add_task("无截止日期", "中")
        todo.add_task("有截止日期", "中", "2026-12-31")

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.list_tasks()

        output = captured_output.getvalue()
        self.assertIn("无截止日期", output)
        self.assertIn("有截止日期", output)
        lines = output.split("\n")
        no_due_line = [l for l in lines if "无截止日期" in l][0]
        has_due_line = [l for l in lines if "有截止日期" in l][0]
        self.assertNotIn("📅", no_due_line)
        self.assertIn("📅", has_due_line)


if __name__ == "__main__":
    print("=" * 60)
    print("无截止日期任务专项测试")
    print("=" * 60)
    unittest.main(verbosity=2)
