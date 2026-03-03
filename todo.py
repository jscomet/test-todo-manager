#!/usr/bin/env python3
"""
Simple Todo Manager - 简单任务管理器
一个基于 BabyAGI 思想开发的 CLI 工具
"""

import argparse
import json
import os
from pathlib import Path
from datetime import datetime

from commands.task_commands import (
    AddCommand,
    DoneCommand,
    DeleteCommand,
    SetPriorityCommand,
    AddTagCommand,
    RemoveTagCommand,
    CleanupCommand,
)
from commands.query_commands import ListCommand, StatsCommand, DueCommand
from commands.export_commands import ExportCommand
from commands.base import Command
from core.models import Task, Priority
from core.storage import JSONStorage


COMMANDS = [
    AddCommand(),
    ListCommand(),
    DoneCommand(),
    DeleteCommand(),
    AddTagCommand(),
    RemoveTagCommand(),
    SetPriorityCommand(),
    ExportCommand(),
    StatsCommand(),
    DueCommand(),
    CleanupCommand(),
]


class CoverageCommand(Command):
    """生成测试覆盖率报告"""

    name = "coverage"
    help = "生成测试覆盖率报告"

    def add_arguments(self, parser):
        parser.add_argument(
            "--format",
            "-f",
            choices=["html", "xml", "json", "term", "all"],
            default="html",
            help="报告格式 (默认：html)",
        )
        parser.add_argument(
            "--output-dir",
            "-o",
            type=str,
            default="tests/coverage",
            help="输出目录 (默认：tests/coverage)",
        )
        parser.add_argument(
            "--threshold", type=int, default=80, help="覆盖率阈值 (默认：80)"
        )
        parser.add_argument("--branch", action="store_true", help="启用分支覆盖率")
        parser.add_argument("--quiet", "-q", action="store_true", help="安静模式")

    def execute(self, args):
        import subprocess
        import sys
        import glob

        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "tests/",
        ]

        test_files = glob.glob("test_*.py")
        cmd.extend(test_files)

        cmd.extend([f"--cov=.", "--cov-report=term-missing"])

        if args.branch:
            cmd.append("--cov-branch")

        cmd.append(f"--cov-report=html:{output_dir}/html")
        cmd.append(f"--cov-report=xml:{output_dir}/coverage.xml")
        cmd.append(f"--cov-report=json:{output_dir}/coverage.json")

        if not args.quiet:
            print(f"生成测试覆盖率报告...")
            print(f"输出目录：{output_dir}")
            print("-" * 60)

        result = subprocess.run(cmd)

        if not args.quiet:
            print("\n" + "=" * 60)
            print("覆盖率报告生成完成！")
            print("=" * 60)
            print(
                f"HTML 报告：file://{(output_dir / 'html' / 'index.html').absolute()}"
            )
            print(f"XML 报告：{output_dir}/coverage.xml")
            print(f"JSON 报告：{output_dir}/coverage.json")
            print("=" * 60)


COMMANDS.append(CoverageCommand())

TASKS_FILE = "data/tasks.json"


def _get_storage():
    """获取存储实例（支持测试覆盖）"""
    import sys

    test_data_dir = getattr(sys.modules[__name__], "_test_data_dir", None)
    if test_data_dir:
        return JSONStorage(Path(test_data_dir))
    return JSONStorage()


def load_tasks(include_test=False):
    """加载任务列表（向后兼容函数）"""
    storage = _get_storage()
    tasks = storage.load(include_test=include_test)
    return [task.to_dict() for task in tasks]


def save_tasks(tasks):
    """保存任务列表（向后兼容函数）"""
    storage = _get_storage()
    task_objects = [Task.from_dict(t) for t in tasks]
    storage.save(task_objects)


def add_task(content, priority="中", due_date=None, tags=None):
    """添加任务（向后兼容函数）"""
    storage = _get_storage()
    task = Task(
        id=storage.get_next_id(),
        content=content,
        priority=Priority.from_string(priority),
        due_date=due_date,
        tags=tags or [],
    )
    storage.add_task(task)
    return task


def delete_task(task_id):
    """删除任务（向后兼容函数）"""
    storage = _get_storage()
    return storage.delete_task(task_id)


def complete_task(task_id):
    """标记任务完成（向后兼容函数）"""
    storage = _get_storage()
    tasks = storage.load(include_test=True)
    for task in tasks:
        if task.id == task_id:
            task.mark_done()
            storage.update_task(task)
            return True
    return False


def add_tag_to_task(task_id, tag):
    """给任务添加标签（向后兼容函数）"""
    storage = _get_storage()
    tasks = storage.load(include_test=True)
    for task in tasks:
        if task.id == task_id:
            task.add_tag(tag)
            storage.update_task(task)
            return True
    return False


def remove_tag_from_task(task_id, tag):
    """从任务移除标签（向后兼容函数）"""
    storage = _get_storage()
    tasks = storage.load(include_test=True)
    for task in tasks:
        if task.id == task_id:
            task.remove_tag(tag)
            storage.update_task(task)
            return True
    return False


def set_task_priority(task_id, priority):
    """设置任务优先级（向后兼容函数）"""
    storage = _get_storage()
    tasks = storage.load(include_test=True)
    for task in tasks:
        if task.id == task_id:
            task.set_priority(Priority.from_string(priority))
            storage.update_task(task)
            return True
    return False


def main():
    """程序主入口函数"""
    parser = argparse.ArgumentParser(
        description="Simple Todo Manager - 简单任务管理器", prog="todo"
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    for cmd in COMMANDS:
        cmd.register(subparsers)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
