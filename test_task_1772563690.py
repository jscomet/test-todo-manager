#!/usr/bin/env python3
"""
测试任务_1772563690 - 综合功能验证测试

此测试验证 Todo 管理器的核心功能：
- 任务添加
- 任务列表
- 任务完成
- 任务删除
- 标签管理
- 优先级管理
- 导出功能
- 统计功能
- 截止日期功能
"""

import json
import os
import subprocess
import unittest
from datetime import datetime, timedelta

TASKS_FILE = "tasks.json"


def run_cli(args):
    """运行 CLI 命令并返回输出"""
    result = subprocess.run(
        ["python3", "todo.py"] + args, capture_output=True, text=True
    )
    return result.stdout + result.stderr


def load_tasks():
    """加载任务"""
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def get_task_count():
    """获取任务总数"""
    return len(load_tasks())


class TestTaskManagement(unittest.TestCase):
    """测试任务管理基本功能"""

    def setUp(self):
        """保存当前任务状态"""
        self.initial_count = get_task_count()

    def test_add_task_basic(self):
        """测试基本任务添加"""
        initial = get_task_count()
        output = run_cli(["add", "测试任务_1772563690_基本添加"])
        self.assertIn("✅ 已添加任务", output)
        self.assertEqual(get_task_count(), initial + 1)

    def test_add_task_with_priority(self):
        """测试带优先级的任务添加"""
        for priority in ["高", "中", "低"]:
            output = run_cli(["add", f"测试优先级_{priority}", "--priority", priority])
            self.assertIn("✅ 已添加任务", output)

    def test_add_task_with_due_date(self):
        """测试带截止日期的任务添加"""
        due_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        output = run_cli(["add", "测试截止日期", "--due", due_date])
        self.assertIn("✅ 已添加任务", output)

        tasks = load_tasks()
        last_task = tasks[-1]
        self.assertEqual(last_task["due_date"], due_date)

    def test_add_task_with_tags(self):
        """测试带标签的任务添加"""
        output = run_cli(["add", "测试标签", "--tags", "测试，验证"])
        self.assertIn("✅ 已添加任务", output)

        tasks = load_tasks()
        last_task = tasks[-1]
        self.assertIn("测试", last_task.get("tags", []))
        self.assertIn("验证", last_task.get("tags", []))

    def test_list_tasks(self):
        """测试任务列表显示"""
        output = run_cli(["list"])
        self.assertIn("📋 任务列表", output)
        self.assertIn("总计", output)

    def test_list_tasks_filter_by_priority(self):
        """测试按优先级过滤"""
        for priority in ["高", "中", "低"]:
            output = run_cli(["list", "--priority", priority])
            self.assertIn("优先级", output)

    def test_list_tasks_filter_by_tag(self):
        """测试按标签过滤"""
        output = run_cli(["list", "--tag", "测试"])
        self.assertIn("标签", output)

    def test_list_tasks_sort_by_priority(self):
        """测试按优先级排序"""
        output = run_cli(["list", "--sort", "priority"])
        self.assertIn("任务列表", output)

    def test_list_tasks_no_sort(self):
        """测试不排序"""
        output = run_cli(["list", "--sort", "none"])
        self.assertIn("任务列表", output)


class TestTaskCompletion(unittest.TestCase):
    """测试任务完成功能"""

    def test_done_task(self):
        """测试标记任务完成"""
        output = run_cli(["done", "1"])
        self.assertIn("已完成", output)

        tasks = load_tasks()
        task_1 = next((t for t in tasks if t["id"] == 1), None)
        self.assertIsNotNone(task_1)
        self.assertTrue(task_1["done"])

    def test_done_nonexistent_task(self):
        """测试标记不存在的任务"""
        output = run_cli(["done", "99999"])
        self.assertIn("❌ 未找到任务", output)


class TestTaskDeletion(unittest.TestCase):
    """测试任务删除功能"""

    def test_delete_task(self):
        """测试删除任务"""
        initial = get_task_count()
        output = run_cli(["delete", "2"])
        self.assertIn("🗑️  已删除任务", output)
        self.assertEqual(get_task_count(), initial - 1)

    def test_delete_nonexistent_task(self):
        """测试删除不存在的任务"""
        output = run_cli(["delete", "99999"])
        self.assertIn("❌ 未找到任务", output)


class TestTagManagement(unittest.TestCase):
    """测试标签管理功能"""

    def test_add_tag(self):
        """测试添加标签到任务"""
        output = run_cli(["add-tag", "3", "新标签"])
        self.assertIn("✅ 已为任务", output)

        tasks = load_tasks()
        task_3 = next((t for t in tasks if t["id"] == 3), None)
        self.assertIsNotNone(task_3)
        self.assertIn("新标签", task_3.get("tags", []))

    def test_add_duplicate_tag(self):
        """测试添加重复标签"""
        run_cli(["add-tag", "3", "重复标签"])
        output = run_cli(["add-tag", "3", "重复标签"])
        self.assertIn("⚠️  标签", output)
        self.assertIn("已存在", output)

    def test_remove_tag(self):
        """测试移除标签"""
        run_cli(["add-tag", "3", "临时标签"])
        output = run_cli(["remove-tag", "3", "临时标签"])
        self.assertIn("✅ 已从任务", output)

        tasks = load_tasks()
        task_3 = next((t for t in tasks if t["id"] == 3), None)
        self.assertIsNotNone(task_3)
        self.assertNotIn("临时标签", task_3.get("tags", []))

    def test_remove_nonexistent_tag(self):
        """测试移除不存在的标签"""
        output = run_cli(["remove-tag", "3", "不存在的标签"])
        self.assertIn("⚠️  标签", output)
        self.assertIn("不存在", output)

    def test_add_tag_to_nonexistent_task(self):
        """测试给不存在的任务添加标签"""
        output = run_cli(["add-tag", "99999", "标签"])
        self.assertIn("❌ 未找到任务", output)

    def test_remove_tag_from_nonexistent_task(self):
        """测试从不存在的任务移除标签"""
        output = run_cli(["remove-tag", "99999", "标签"])
        self.assertIn("❌ 未找到任务", output)


class TestPriorityManagement(unittest.TestCase):
    """测试优先级管理功能"""

    def test_set_priority_high(self):
        """测试设置优先级为高"""
        output = run_cli(["set-priority", "4", "高"])
        self.assertIn("✅ 任务", output)
        self.assertIn("优先级已修改", output)

        tasks = load_tasks()
        task_4 = next((t for t in tasks if t["id"] == 4), None)
        self.assertIsNotNone(task_4)
        self.assertEqual(task_4["priority"], "高")

    def test_set_priority_medium(self):
        """测试设置优先级为中"""
        output = run_cli(["set-priority", "4", "中"])
        self.assertIn("✅ 任务", output)

        tasks = load_tasks()
        task_4 = next((t for t in tasks if t["id"] == 4), None)
        self.assertEqual(task_4["priority"], "中")

    def test_set_priority_low(self):
        """测试设置优先级为低"""
        output = run_cli(["set-priority", "4", "低"])
        self.assertIn("✅ 任务", output)

        tasks = load_tasks()
        task_4 = next((t for t in tasks if t["id"] == 4), None)
        self.assertEqual(task_4["priority"], "低")

    def test_set_priority_nonexistent_task(self):
        """测试设置不存在任务的优先级"""
        output = run_cli(["set-priority", "99999", "高"])
        self.assertIn("❌ 未找到任务", output)


class TestExportFunctionality(unittest.TestCase):
    """测试导出功能"""

    def test_export_csv(self):
        """测试导出为 CSV"""
        output = run_cli(
            ["export", "--format", "csv", "--output", "test_1772563690.csv"]
        )
        self.assertIn("✅ 已导出", output)
        self.assertTrue(os.path.exists("test_1772563690.csv"))

        with open("test_1772563690.csv", "r", encoding="utf-8-sig") as f:
            content = f.read()
            self.assertIn("ID", content)
            self.assertIn("内容", content)
            self.assertIn("状态", content)

        os.remove("test_1772563690.csv")

    def test_export_markdown(self):
        """测试导出为 Markdown"""
        output = run_cli(
            ["export", "--format", "markdown", "--output", "test_1772563690.md"]
        )
        self.assertIn("✅ 已导出", output)
        self.assertTrue(os.path.exists("test_1772563690.md"))

        with open("test_1772563690.md", "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("# 任务列表", content)
            self.assertIn("| ID |", content)

        os.remove("test_1772563690.md")


class TestStatisticsFunctionality(unittest.TestCase):
    """测试统计功能"""

    def test_stats_basic(self):
        """测试基本统计"""
        output = run_cli(["stats"])
        self.assertIn("📊 任务统计", output)
        self.assertIn("总体情况", output)
        self.assertIn("优先级分布", output)

    def test_stats_filter_by_priority(self):
        """测试按优先级过滤统计"""
        for priority in ["高", "中", "低"]:
            output = run_cli(["stats", "--priority", priority])
            self.assertIn("任务统计", output)

    def test_stats_filter_by_tag(self):
        """测试按标签过滤统计"""
        output = run_cli(["stats", "--tag", "测试"])
        self.assertIn("任务统计", output)


class TestDueDateFunctionality(unittest.TestCase):
    """测试截止日期功能"""

    def test_due_basic(self):
        """测试基本即将到期任务显示"""
        output = run_cli(["due"])
        self.assertIn("📅 即将到期的任务", output)

    def test_due_with_days_filter(self):
        """测试按天数过滤"""
        output = run_cli(["due", "--days", "30"])
        self.assertIn("即将到期的任务", output)
        self.assertIn("30 天内", output)

    def test_due_sort_by_priority(self):
        """测试按优先级排序"""
        output = run_cli(["due", "--sort", "priority"])
        self.assertIn("即将到期的任务", output)


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def test_full_workflow(self):
        """测试完整工作流程"""
        initial = get_task_count()

        output = run_cli(
            [
                "add",
                "集成测试任务",
                "--priority",
                "高",
                "--due",
                "2026-12-31",
                "--tags",
                "集成，测试",
            ]
        )
        self.assertIn("✅ 已添加任务", output)

        task_id = get_task_count()

        output = run_cli(["list"])
        self.assertIn("集成测试任务", output)

        output = run_cli(["set-priority", str(task_id), "中"])
        self.assertIn("✅ 任务", output)

        output = run_cli(["add-tag", str(task_id), "工作"])
        self.assertIn("✅ 已为任务", output)

        output = run_cli(["done", str(task_id)])
        self.assertIn("✅ 任务", output)

        tasks = load_tasks()
        task = next((t for t in tasks if t["id"] == task_id), None)
        self.assertIsNotNone(task)
        self.assertTrue(task["done"])
        self.assertEqual(task["priority"], "中")
        self.assertIn("工作", task.get("tags", []))

        output = run_cli(["delete", str(task_id)])
        self.assertIn("🗑️  已删除任务", output)

        self.assertEqual(get_task_count(), initial)

    def test_multiple_attributes_task(self):
        """测试多属性任务"""
        output = run_cli(
            [
                "add",
                "多属性测试",
                "--priority",
                "高",
                "--due",
                "2026-06-15",
                "--tags",
                "重要，紧急，工作",
            ]
        )
        self.assertIn("✅ 已添加任务", output)

        tasks = load_tasks()
        last_task = tasks[-1]
        self.assertEqual(last_task["priority"], "高")
        self.assertEqual(last_task["due_date"], "2026-06-15")
        self.assertIn("重要", last_task.get("tags", []))
        self.assertIn("紧急", last_task.get("tags", []))
        self.assertIn("工作", last_task.get("tags", []))


class TestEdgeCases(unittest.TestCase):
    """边界情况测试"""

    def test_empty_task_list_message(self):
        """测试空任务列表消息"""
        output = run_cli(["list", "--tag", "不存在的标签"])
        self.assertIn("📭", output)

    def test_help_command(self):
        """测试帮助命令"""
        output = run_cli(["--help"])
        self.assertIn("Simple Todo Manager", output)
        self.assertIn("可用命令", output)

    def test_add_task_special_characters(self):
        """测试特殊字符任务"""
        output = run_cli(["add", "测试特殊字符：@#$%&*()"])
        self.assertIn("✅ 已添加任务", output)

    def test_add_task_unicode(self):
        """测试 Unicode 字符"""
        output = run_cli(["add", "测试 Unicode：日本語，한국어，العربية"])
        self.assertIn("✅ 已添加任务", output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
