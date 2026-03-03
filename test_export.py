#!/usr/bin/env python3
"""
测试导出功能 - 单元测试
测试 Todo 管理器的 CSV 和 Markdown 导出功能
"""

import csv
import json
import os
import unittest
from io import StringIO
from unittest.mock import patch

import todo


class TestExportCSV(unittest.TestCase):
    """CSV 导出功能测试类"""

    def setUp(self):
        """测试前准备：创建干净的测试环境"""
        self.test_file = "test_export.json"
        self.csv_file = "test_export.csv"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(self.csv_file):
            os.remove(self.csv_file)

    def tearDown(self):
        """测试后清理：删除测试文件"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(self.csv_file):
            os.remove(self.csv_file)

    def test_export_csv_empty_tasks(self):
        """测试空任务列表时的 CSV 导出"""
        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.export_csv(self.csv_file)
        output = captured_output.getvalue()
        self.assertIn("暂无任务可导出", output)
        self.assertFalse(os.path.exists(self.csv_file))

    def test_export_csv_default_filename(self):
        """测试默认文件名的 CSV 导出"""
        todo.add_task("CSV 测试任务", "中")

        with patch("sys.stdout", StringIO()):
            todo.export_csv()

        self.assertTrue(os.path.exists("tasks_export.csv"))
        os.remove("tasks_export.csv")

    def test_export_csv_with_custom_filename(self):
        """测试自定义文件名的 CSV 导出"""
        todo.add_task("CSV 测试任务", "中")

        with patch("sys.stdout", StringIO()):
            todo.export_csv("custom_export.csv")

        self.assertTrue(os.path.exists("custom_export.csv"))
        os.remove("custom_export.csv")

    def test_export_csv_headers(self):
        """测试 CSV 文件头"""
        todo.add_task("测试任务", "中")

        with patch("sys.stdout", StringIO()):
            todo.export_csv(self.csv_file)

        with open(self.csv_file, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            headers = next(reader)

        expected_headers = [
            "ID",
            "内容",
            "状态",
            "优先级",
            "创建时间",
            "截止日期",
            "标签",
        ]
        self.assertEqual(headers, expected_headers)

    def test_export_csv_single_task(self):
        """测试单个任务的 CSV 导出"""
        todo.add_task("单个任务", "高", "2026-12-31", ["测试", "工作"])

        with patch("sys.stdout", StringIO()):
            todo.export_csv(self.csv_file)

        with open(self.csv_file, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            next(reader)
            row = next(reader)

        self.assertEqual(row[0], "1")
        self.assertEqual(row[1], "单个任务")
        self.assertEqual(row[2], "待完成")
        self.assertEqual(row[3], "高")
        self.assertEqual(row[5], "2026-12-31")
        self.assertIn("测试", row[6])
        self.assertIn("工作", row[6])

    def test_export_csv_completed_task(self):
        """测试已完成任务的 CSV 导出"""
        todo.add_task("完成任务", "中")
        tasks = todo.load_tasks()
        todo.done_task(tasks[0]["id"])

        with patch("sys.stdout", StringIO()):
            todo.export_csv(self.csv_file)

        with open(self.csv_file, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            next(reader)
            row = next(reader)

        self.assertEqual(row[2], "已完成")

    def test_export_csv_multiple_tasks(self):
        """测试多个任务的 CSV 导出"""
        todo.add_task("任务 1", "高")
        todo.add_task("任务 2", "中")
        todo.add_task("任务 3", "低")

        with patch("sys.stdout", StringIO()):
            todo.export_csv(self.csv_file)

        with open(self.csv_file, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            next(reader)
            rows = list(reader)

        self.assertEqual(len(rows), 3)

    def test_export_csv_special_characters(self):
        """测试包含特殊字符的任务导出"""
        todo.add_task("任务，带逗号", "中")
        todo.add_task('任务"带引号"', "中")
        todo.add_task("任务\n带换行", "中")

        with patch("sys.stdout", StringIO()):
            todo.export_csv(self.csv_file)

        with open(self.csv_file, "r", encoding="utf-8-sig") as f:
            content = f.read()

        self.assertIn("任务，带逗号", content)
        self.assertIn('""带引号""', content)

    def test_export_csv_task_without_due_date(self):
        """测试无截止日期任务的 CSV 导出"""
        todo.add_task("无截止日期任务", "中")

        with patch("sys.stdout", StringIO()):
            todo.export_csv(self.csv_file)

        with open(self.csv_file, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            next(reader)
            row = next(reader)

        self.assertEqual(row[5], "")

    def test_export_csv_task_without_tags(self):
        """测试无标签任务的 CSV 导出"""
        todo.add_task("无标签任务", "中")

        with patch("sys.stdout", StringIO()):
            todo.export_csv(self.csv_file)

        with open(self.csv_file, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            next(reader)
            row = next(reader)

        self.assertEqual(row[6], "")

    def test_export_csv_encoding(self):
        """测试 CSV 文件的 UTF-8 编码"""
        todo.add_task("中文任务内容", "中")
        todo.add_task("English Task", "中")

        with patch("sys.stdout", StringIO()):
            todo.export_csv(self.csv_file)

        with open(self.csv_file, "r", encoding="utf-8-sig") as f:
            content = f.read()

        self.assertIn("中文任务内容", content)
        self.assertIn("English Task", content)


class TestExportMarkdown(unittest.TestCase):
    """Markdown 导出功能测试类"""

    def setUp(self):
        """测试前准备：创建干净的测试环境"""
        self.test_file = "test_export.json"
        self.md_file = "test_export.md"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(self.md_file):
            os.remove(self.md_file)

    def tearDown(self):
        """测试后清理：删除测试文件"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(self.md_file):
            os.remove(self.md_file)

    def test_export_markdown_empty_tasks(self):
        """测试空任务列表时的 Markdown 导出"""
        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            todo.export_markdown(self.md_file)
        output = captured_output.getvalue()
        self.assertIn("暂无任务可导出", output)
        self.assertFalse(os.path.exists(self.md_file))

    def test_export_markdown_default_filename(self):
        """测试默认文件名的 Markdown 导出"""
        todo.add_task("MD 测试任务", "中")

        with patch("sys.stdout", StringIO()):
            todo.export_markdown()

        self.assertTrue(os.path.exists("tasks_export.md"))
        os.remove("tasks_export.md")

    def test_export_markdown_custom_filename(self):
        """测试自定义文件名的 Markdown 导出"""
        todo.add_task("MD 测试任务", "中")

        with patch("sys.stdout", StringIO()):
            todo.export_markdown("custom_export.md")

        self.assertTrue(os.path.exists("custom_export.md"))
        os.remove("custom_export.md")

    def test_export_markdown_title(self):
        """测试 Markdown 文件标题"""
        todo.add_task("测试任务", "中")

        with patch("sys.stdout", StringIO()):
            todo.export_markdown(self.md_file)

        with open(self.md_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("# 任务列表", content)

    def test_export_markdown_summary(self):
        """测试 Markdown 统计信息"""
        todo.add_task("任务 1", "中")
        todo.add_task("任务 2", "中")
        todo.done_task(1)

        with patch("sys.stdout", StringIO()):
            todo.export_markdown(self.md_file)

        with open(self.md_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("**总计**: 2 个任务", content)
        self.assertIn("**已完成**: 1", content)
        self.assertIn("**待完成**: 1", content)

    def test_export_markdown_table_headers(self):
        """测试 Markdown 表格头"""
        todo.add_task("测试任务", "中")

        with patch("sys.stdout", StringIO()):
            todo.export_markdown(self.md_file)

        with open(self.md_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("| ID | 状态 | 优先级 | 内容 | 截止日期 | 标签 |", content)

    def test_export_markdown_table_row(self):
        """测试 Markdown 表格行"""
        todo.add_task("表格行测试", "高", "2026-12-31", ["测试"])

        with patch("sys.stdout", StringIO()):
            todo.export_markdown(self.md_file)

        with open(self.md_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("⭕", content)
        self.assertIn("高", content)
        self.assertIn("表格行测试", content)
        self.assertIn("2026-12-31", content)
        self.assertIn("#测试", content)

    def test_export_markdown_completed_task_icon(self):
        """测试已完成任务的图标"""
        todo.add_task("完成任务", "中")
        tasks = todo.load_tasks()
        todo.done_task(tasks[0]["id"])

        with patch("sys.stdout", StringIO()):
            todo.export_markdown(self.md_file)

        with open(self.md_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("✅", content)

    def test_export_markdown_statistics_section(self):
        """测试统计信息部分"""
        todo.add_task("任务 1", "中")
        todo.add_task("任务 2", "中")

        with patch("sys.stdout", StringIO()):
            todo.export_markdown(self.md_file)

        with open(self.md_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("## 统计信息", content)
        self.assertIn("完成进度", content)
        self.assertIn("导出时间", content)

    def test_export_markdown_pipe_character_escaping(self):
        """测试管道符转义"""
        todo.add_task("任务 | 带管道符", "中")

        with patch("sys.stdout", StringIO()):
            todo.export_markdown(self.md_file)

        with open(self.md_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("\\|", content)

    def test_export_markdown_multiple_tasks(self):
        """测试多个任务的 Markdown 导出"""
        todo.add_task("任务 1", "高")
        todo.add_task("任务 2", "中")
        todo.add_task("任务 3", "低")
        todo.done_task(2)

        with patch("sys.stdout", StringIO()):
            todo.export_markdown(self.md_file)

        with open(self.md_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("任务 1", content)
        self.assertIn("任务 2", content)
        self.assertIn("任务 3", content)
        self.assertEqual(content.count("✅"), 1)
        self.assertEqual(content.count("⭕"), 2)

    def test_export_markdown_encoding(self):
        """测试 Markdown 文件的 UTF-8 编码"""
        todo.add_task("中文任务", "中")
        todo.add_task("English Task", "中")

        with patch("sys.stdout", StringIO()):
            todo.export_markdown(self.md_file)

        with open(self.md_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("中文任务", content)
        self.assertIn("English Task", content)


class TestExportEdgeCases(unittest.TestCase):
    """导出功能边界情况测试类"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_export.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        for f in ["tasks_export.csv", "tasks_export.md"]:
            if os.path.exists(f):
                os.remove(f)

    def test_export_with_all_fields_populated(self):
        """测试所有字段都填充的任务导出"""
        todo.add_task("完整字段任务", "高", "2026-12-31", ["工作", "紧急", "重要"])
        tasks = todo.load_tasks()
        todo.done_task(tasks[0]["id"])

        csv_file = "test_complete.csv"
        md_file = "test_complete.md"

        with patch("sys.stdout", StringIO()):
            todo.export_csv(csv_file)
            todo.export_markdown(md_file)

        self.assertTrue(os.path.exists(csv_file))
        self.assertTrue(os.path.exists(md_file))

        with open(csv_file, "r", encoding="utf-8-sig") as f:
            csv_content = f.read()
        with open(md_file, "r", encoding="utf-8") as f:
            md_content = f.read()

        self.assertIn("完整字段任务", csv_content)
        self.assertIn("完整字段任务", md_content)
        self.assertIn("已完成", csv_content)
        self.assertIn("✅", md_content)

        os.remove(csv_file)
        os.remove(md_file)

    def test_export_mixed_completed_and_pending(self):
        """测试混合已完成和待完成任务的导出"""
        todo.add_task("待完成 1", "高")
        todo.add_task("待完成 2", "中")
        todo.add_task("已完成 1", "低")

        tasks = todo.load_tasks()
        todo.done_task(tasks[2]["id"])

        md_file = "test_mixed.md"
        with patch("sys.stdout", StringIO()):
            todo.export_markdown(md_file)

        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("**总计**: 3 个任务", content)
        self.assertIn("**已完成**: 1", content)
        self.assertIn("**待完成**: 2", content)

        os.remove(md_file)


if __name__ == "__main__":
    print("=" * 60)
    print("测试导出功能 - 单元测试")
    print("=" * 60)
    unittest.main(verbosity=2)
