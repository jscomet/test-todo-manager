#!/usr/bin/env python3
"""
统计测试套件
测试 Todo 管理器的统计功能
"""

import json
import os
import sys
import unittest
from datetime import datetime
from io import StringIO
from unittest.mock import patch

import todo


class TestStatsBasic(unittest.TestCase):
    """测试统计基本功能"""

    def setUp(self):
        """测试前准备：创建干净的测试环境"""
        self.test_file = "test_tasks_stats.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理：删除测试文件"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_stats_empty_tasks(self):
        """测试空任务列表的统计"""
        output = StringIO()
        sys.stdout = output
        try:
            todo.stats()
        finally:
            sys.stdout = sys.__stdout__

        result = output.getvalue()
        self.assertIn("暂无任务", result)

    def test_stats_single_task(self):
        """测试单个任务的统计"""
        todo.add_task("测试任务")

        output = StringIO()
        sys.stdout = output
        try:
            todo.stats()
        finally:
            sys.stdout = sys.__stdout__

        result = output.getvalue()
        self.assertIn("总计：1 个任务", result)
        self.assertIn("优先级分布", result)

    def test_stats_multiple_tasks(self):
        """测试多个任务的统计"""
        todo.add_task("任务 1", "高")
        todo.add_task("任务 2", "中")
        todo.add_task("任务 3", "低")

        output = StringIO()
        sys.stdout = output
        try:
            todo.stats()
        finally:
            sys.stdout = sys.__stdout__

        result = output.getvalue()
        self.assertIn("总计：3 个任务", result)
        self.assertIn("高优先级：1 个", result)
        self.assertIn("中优先级：1 个", result)
        self.assertIn("低优先级：1 个", result)

    def test_stats_completion_percentage(self):
        """测试完成百分比计算"""
        todo.add_task("任务 1", "高")
        todo.add_task("任务 2", "高")
        todo.done_task(1)

        output = StringIO()
        sys.stdout = output
        try:
            todo.stats()
        finally:
            sys.stdout = sys.__stdout__

        result = output.getvalue()
        self.assertIn("已完成：1 (50%)", result)
        self.assertIn("待完成：1 (50%)", result)


class TestStatsByPriority(unittest.TestCase):
    """测试按优先级统计"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tasks_stats_priority.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_stats_filter_by_high_priority(self):
        """测试按高优先级过滤统计"""
        todo.add_task("高优先级任务 1", "高")
        todo.add_task("高优先级任务 2", "高")
        todo.add_task("中优先级任务", "中")
        todo.add_task("低优先级任务", "低")

        output = StringIO()
        sys.stdout = output
        try:
            todo.stats(priority_filter="高")
        finally:
            sys.stdout = sys.__stdout__

        result = output.getvalue()
        self.assertIn("总计：2 个任务", result)
        self.assertIn("优先级：高", result)
        self.assertNotIn("中优先级", result)
        self.assertNotIn("低优先级", result)

    def test_stats_filter_by_medium_priority(self):
        """测试按中优先级过滤统计"""
        todo.add_task("高优先级任务", "高")
        todo.add_task("中优先级任务 1", "中")
        todo.add_task("中优先级任务 2", "中")
        todo.add_task("低优先级任务", "低")

        output = StringIO()
        sys.stdout = output
        try:
            todo.stats(priority_filter="中")
        finally:
            sys.stdout = sys.__stdout__

        result = output.getvalue()
        self.assertIn("总计：2 个任务", result)
        self.assertIn("优先级：中", result)

    def test_stats_filter_by_low_priority(self):
        """测试按低优先级过滤统计"""
        todo.add_task("高优先级任务", "高")
        todo.add_task("中优先级任务", "中")
        todo.add_task("低优先级任务 1", "低")
        todo.add_task("低优先级任务 2", "低")
        todo.add_task("低优先级任务 3", "低")

        output = StringIO()
        sys.stdout = output
        try:
            todo.stats(priority_filter="低")
        finally:
            sys.stdout = sys.__stdout__

        result = output.getvalue()
        self.assertIn("总计：3 个任务", result)
        self.assertIn("优先级：低", result)

    def test_stats_no_matching_priority(self):
        """测试没有匹配优先级的统计"""
        todo.add_task("中优先级任务", "中")

        output = StringIO()
        sys.stdout = output
        try:
            todo.stats(priority_filter="高")
        finally:
            sys.stdout = sys.__stdout__

        result = output.getvalue()
        self.assertIn("没有找到优先级为 '高' 的任务", result)


class TestStatsByTag(unittest.TestCase):
    """测试按标签统计"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tasks_stats_tag.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_stats_filter_by_tag(self):
        """测试按标签过滤统计"""
        todo.add_task("工作任务 1", "高", tags=["工作"])
        todo.add_task("工作任务 2", "中", tags=["工作"])
        todo.add_task("个人任务", "低", tags=["个人"])

        output = StringIO()
        sys.stdout = output
        try:
            todo.stats(tag_filter="工作")
        finally:
            sys.stdout = sys.__stdout__

        result = output.getvalue()
        self.assertIn("总计：2 个任务", result)
        self.assertIn("标签：#工作", result)

    def test_stats_filter_by_tag_with_completion(self):
        """测试按标签过滤统计包含完成情况"""
        todo.add_task("工作任务 1", "高", tags=["工作"])
        todo.add_task("工作任务 2", "中", tags=["工作"])
        todo.add_task("个人任务", "低", tags=["个人"])
        todo.done_task(1)

        output = StringIO()
        sys.stdout = output
        try:
            todo.stats(tag_filter="工作")
        finally:
            sys.stdout = sys.__stdout__

        result = output.getvalue()
        self.assertIn("总计：2 个任务", result)
        self.assertIn("已完成：1 (50%)", result)

    def test_stats_no_matching_tag(self):
        """测试没有匹配标签的统计"""
        todo.add_task("任务 1", tags=["工作"])

        output = StringIO()
        sys.stdout = output
        try:
            todo.stats(tag_filter="不存在的标签")
        finally:
            sys.stdout = sys.__stdout__

        result = output.getvalue()
        self.assertIn("没有找到带标签 '不存在的标签' 的任务", result)


class TestStatsMixed(unittest.TestCase):
    """测试混合场景的统计"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tasks_stats_mixed.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_stats_with_all_priority_levels(self):
        """测试包含所有优先级级别的统计"""
        for _ in range(3):
            todo.add_task("高优先级任务", "高")
        for _ in range(5):
            todo.add_task("中优先级任务", "中")
        for _ in range(2):
            todo.add_task("低优先级任务", "低")

        output = StringIO()
        sys.stdout = output
        try:
            todo.stats()
        finally:
            sys.stdout = sys.__stdout__

        result = output.getvalue()
        self.assertIn("总计：10 个任务", result)
        self.assertIn("高优先级：3 个", result)
        self.assertIn("中优先级：5 个", result)
        self.assertIn("低优先级：2 个", result)

    def test_stats_with_completed_and_pending(self):
        """测试包含已完成和待完成的统计"""
        todo.add_task("任务 1", "高")
        todo.add_task("任务 2", "高")
        todo.add_task("任务 3", "高")
        todo.done_task(1)
        todo.done_task(2)

        output = StringIO()
        sys.stdout = output
        try:
            todo.stats(priority_filter="高")
        finally:
            sys.stdout = sys.__stdout__

        result = output.getvalue()
        self.assertIn("总计：3 个任务", result)
        self.assertIn("已完成：2 (66%)", result)
        self.assertIn("待完成：1 (33%)", result)
        self.assertIn("高优先级：3 个 (完成：2/3)", result)

    def test_stats_with_tags_and_priorities(self):
        """测试包含标签和优先级的混合统计"""
        todo.add_task("重要工作", "高", tags=["工作", "重要"])
        todo.add_task("日常工作", "中", tags=["工作"])
        todo.add_task("个人事务", "低", tags=["个人"])

        output = StringIO()
        sys.stdout = output
        try:
            todo.stats(tag_filter="工作")
        finally:
            sys.stdout = sys.__stdout__

        result = output.getvalue()
        self.assertIn("总计：2 个任务", result)
        self.assertIn("高优先级：1 个", result)
        self.assertIn("中优先级：1 个", result)


class TestStatsCLI(unittest.TestCase):
    """测试 stats 命令行接口"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tasks_stats_cli.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_stats_cli_basic(self):
        """测试 stats 命令基本功能"""
        todo.add_task("任务 1", "高")
        todo.add_task("任务 2", "中")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "stats"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("任务统计", result)
        self.assertIn("总计：2 个任务", result)

    def test_stats_cli_with_priority_filter(self):
        """测试 stats 命令带优先级过滤"""
        todo.add_task("高优先级任务", "高")
        todo.add_task("中优先级任务", "中")

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "stats", "--priority", "高"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("优先级：高", result)
        self.assertIn("总计：1 个任务", result)

    def test_stats_cli_with_tag_filter(self):
        """测试 stats 命令带标签过滤"""
        todo.add_task("工作任务", "高", tags=["工作"])
        todo.add_task("个人任务", "中", tags=["个人"])

        output = StringIO()
        with patch.object(sys, "argv", ["todo", "stats", "--tag", "工作"]):
            with patch.object(sys, "stdout", output):
                todo.main()

        result = output.getvalue()
        self.assertIn("标签：#工作", result)
        self.assertIn("总计：1 个任务", result)


class TestStatsEdgeCases(unittest.TestCase):
    """测试边界情况"""

    def setUp(self):
        """测试前准备"""
        self.test_file = "test_tasks_stats_edge.json"
        todo.TASKS_FILE = self.test_file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_stats_with_default_priority(self):
        """测试默认优先级的统计"""
        todo.add_task("任务 1")
        todo.add_task("任务 2")

        output = StringIO()
        sys.stdout = output
        try:
            todo.stats()
        finally:
            sys.stdout = sys.__stdout__

        result = output.getvalue()
        self.assertIn("中优先级：2 个", result)

    def test_stats_with_all_completed(self):
        """测试全部完成的统计"""
        todo.add_task("任务 1")
        todo.add_task("任务 2")
        todo.done_task(1)
        todo.done_task(2)

        output = StringIO()
        sys.stdout = output
        try:
            todo.stats()
        finally:
            sys.stdout = sys.__stdout__

        result = output.getvalue()
        self.assertIn("已完成：2 (100%)", result)
        self.assertIn("待完成：0 (0%)", result)

    def test_stats_with_none_completed(self):
        """测试全部未完成的统计"""
        todo.add_task("任务 1")
        todo.add_task("任务 2")

        output = StringIO()
        sys.stdout = output
        try:
            todo.stats()
        finally:
            sys.stdout = sys.__stdout__

        result = output.getvalue()
        self.assertIn("已完成：0 (0%)", result)
        self.assertIn("待完成：2 (100%)", result)


if __name__ == "__main__":
    unittest.main()
