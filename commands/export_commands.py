"""导出命令模块

实现任务导出相关的命令。
符合 SPEC.md 第 4.1 节 CLI 命令接口规范。
"""

from typing import Optional
import csv
from argparse import ArgumentParser, Namespace
from datetime import datetime

from .base import Command
from core.storage import JSONStorage
from core.models import Priority


class ExportCommand(Command):
    """导出任务命令"""

    name = "export"
    help = "导出任务列表"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--format",
            "-f",
            type=str,
            default="csv",
            choices=["csv", "markdown"],
            help="导出格式",
        )
        parser.add_argument("--output", "-o", type=str, default=None, help="输出文件名")

    def execute(self, args: Namespace) -> None:
        storage = JSONStorage()
        tasks = storage.load(include_test=True)

        if not tasks:
            print("📭 暂无任务可导出")
            return

        if args.format == "csv":
            self._export_csv(tasks, args.output)
        else:
            self._export_markdown(tasks, args.output)

    def _export_csv(self, tasks, filename: Optional[str] = None) -> None:
        """导出为 CSV 格式"""
        if filename is None:
            filename = "tasks_export.csv"

        with open(filename, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["ID", "内容", "状态", "优先级", "创建时间", "截止日期", "标签"]
            )
            for task in tasks:
                status = "已完成" if task.done else "待完成"
                tags = ", ".join(task.tags)
                writer.writerow(
                    [
                        task.id,
                        task.content,
                        status,
                        task.priority.value,
                        task.created_at,
                        task.due_date or "",
                        tags,
                    ]
                )
        print(f"✅ 已导出 {len(tasks)} 个任务到：{filename}")

    def _export_markdown(self, tasks, filename: Optional[str] = None) -> None:
        """导出为 Markdown 格式"""
        if filename is None:
            filename = "tasks_export.md"

        completed = sum(1 for t in tasks if t.done)
        pending = len(tasks) - completed

        with open(filename, "w", encoding="utf-8") as f:
            f.write("# 任务列表\n\n")
            f.write(
                f"**总计**: {len(tasks)} 个任务 | **已完成**: {completed} | **待完成**: {pending}\n\n"
            )
            f.write("## 任务详情\n\n")
            f.write("| ID | 状态 | 优先级 | 内容 | 截止日期 | 标签 |\n")
            f.write("|---|---|---|---|---|---|\n")
            for task in tasks:
                status = "✅" if task.done else "⭕"
                due = task.due_date or "-"
                tags = " ".join([f"#{t}" for t in task.tags]) or "-"
                content = task.content.replace("|", "\\|")
                f.write(
                    f"| {task.id} | {status} | {task.priority.value} | {content} | {due} | {tags} |\n"
                )
            f.write("\n## 统计信息\n\n")
            f.write(
                f"- 完成进度：{completed}/{len(tasks)} ({completed * 100 // len(tasks) if len(tasks) > 0 else 0}%)\n"
            )
            f.write(f"- 导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        print(f"✅ 已导出 {len(tasks)} 个任务到：{filename}")
