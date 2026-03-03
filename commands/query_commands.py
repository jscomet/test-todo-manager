"""查询命令模块

实现任务列表显示、统计、截止日期相关的命令。
符合 SPEC.md 第 4.1 节 CLI 命令接口规范。
"""

from argparse import ArgumentParser, Namespace
from datetime import datetime, timedelta

from .base import Command
from core.storage import JSONStorage
from core.models import Priority


class ListCommand(Command):
    """列出任务命令"""

    name = "list"
    help = "列出所有任务"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--tag", type=str, default=None, help="按标签过滤")
        parser.add_argument(
            "--priority",
            "-p",
            type=str,
            default=None,
            choices=["高", "中", "低"],
            help="按优先级过滤",
        )
        parser.add_argument(
            "--sort",
            "-s",
            type=str,
            default="priority",
            choices=["priority", "created", "none"],
            help="排序方式",
        )

    def execute(self, args: Namespace) -> None:
        storage = JSONStorage()
        tasks = storage.load(include_test=True)

        # 按标签过滤
        if args.tag:
            tasks = [t for t in tasks if args.tag in t.tags]

        # 按优先级过滤
        if args.priority:
            priority = Priority.from_string(args.priority)
            tasks = [t for t in tasks if t.priority == priority]

        if not tasks:
            if args.tag:
                print(f"📭 没有找到带标签 '{args.tag}' 的任务")
            elif args.priority:
                print(f"📭 没有找到优先级为 '{args.priority}' 的任务")
            else:
                print("📭 暂无任务")
            return

        # 按优先级排序
        if args.sort == "priority":
            priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
            tasks = sorted(tasks, key=lambda t: priority_order.get(t.priority, 1))

        priority_icons = {
            Priority.HIGH: "🔴",
            Priority.MEDIUM: "🟡",
            Priority.LOW: "🟢",
        }

        print("\n📋 任务列表:")
        if args.tag:
            print(f"标签：#{args.tag}")
        if args.priority:
            print(f"优先级：{args.priority}")
        print("-" * 50)
        for task in tasks:
            status = "✅" if task.done else "⭕"
            priority_icon = priority_icons.get(task.priority, "🟡")
            due_str = f" 📅 {task.due_date}" if task.due_date else ""
            tags_str = (
                f" 🔖 {' '.join([f'#{t}' for t in task.tags])}" if task.tags else ""
            )
            print(
                f"{status} [{task.id}] {priority_icon} {task.content}{due_str}{tags_str}"
            )
        print("-" * 50)
        print(f"总计：{len(tasks)} 个任务\n")


class StatsCommand(Command):
    """统计任务命令"""

    name = "stats"
    help = "显示任务优先级统计"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--tag", type=str, default=None, help="按标签过滤统计")
        parser.add_argument(
            "--priority",
            "-p",
            type=str,
            default=None,
            choices=["高", "中", "低"],
            help="按优先级过滤统计",
        )

    def execute(self, args: Namespace) -> None:
        storage = JSONStorage()
        tasks = storage.load(include_test=True)

        # 按标签过滤
        if args.tag:
            tasks = [t for t in tasks if args.tag in t.tags]

        # 按优先级过滤
        if args.priority:
            priority = Priority.from_string(args.priority)
            tasks = [t for t in tasks if t.priority == priority]

        if not tasks:
            if args.tag:
                print(f"📭 没有找到带标签 '{args.tag}' 的任务")
            elif args.priority:
                print(f"📭 没有找到优先级为 '{args.priority}' 的任务")
            else:
                print("📭 暂无任务")
            return

        total = len(tasks)
        completed = sum(1 for t in tasks if t.done)
        pending = total - completed

        high_priority = [t for t in tasks if t.priority == Priority.HIGH]
        medium_priority = [t for t in tasks if t.priority == Priority.MEDIUM]
        low_priority = [t for t in tasks if t.priority == Priority.LOW]

        high_completed = sum(1 for t in high_priority if t.done)
        medium_completed = sum(1 for t in medium_priority if t.done)
        low_completed = sum(1 for t in low_priority if t.done)

        print("\n📊 任务统计")
        if args.tag:
            print(f"标签：#{args.tag}")
        if args.priority:
            print(f"优先级：{args.priority}")
        print("-" * 50)

        print(f"\n📌 总体情况:")
        print(f"   总计：{total} 个任务")
        print(f"   ✅ 已完成：{completed} ({completed * 100 // total}%)")
        print(f"   ⭕ 待完成：{pending} ({pending * 100 // total}%)")

        print(f"\n📌 优先级分布:")
        if high_priority:
            print(
                f"   🔴 高优先级：{len(high_priority)} 个 (完成：{high_completed}/{len(high_priority)})"
            )
        if medium_priority:
            print(
                f"   🟡 中优先级：{len(medium_priority)} 个 (完成：{medium_completed}/{len(medium_priority)})"
            )
        if low_priority:
            print(
                f"   🟢 低优先级：{len(low_priority)} 个 (完成：{low_completed}/{len(low_priority)})"
            )

        print()


class DueCommand(Command):
    """显示即将到期任务命令"""

    name = "due"
    help = "显示即将到期的任务"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--days", "-d", type=int, default=None, help="显示多少天内到期的任务"
        )
        parser.add_argument(
            "--sort",
            "-s",
            type=str,
            default="date",
            choices=["date", "priority"],
            help="排序方式",
        )

    def execute(self, args: Namespace) -> None:
        storage = JSONStorage()
        tasks = storage.load(include_test=True)

        if not tasks:
            print("📭 暂无任务")
            return

        today = datetime.now().date()

        due_tasks = []
        for task in tasks:
            if task.due_date:
                try:
                    due_date = datetime.strptime(task.due_date, "%Y-%m-%d").date()
                    if args.days is not None:
                        end_date = today + timedelta(days=args.days)
                        if due_date <= end_date:
                            days_left = (due_date - today).days
                            due_tasks.append((task, due_date, days_left))
                    else:
                        days_left = (due_date - today).days
                        due_tasks.append((task, due_date, days_left))
                except ValueError:
                    continue

        if not due_tasks:
            if args.days is not None:
                print(f"📭 没有 {args.days} 天内到期的任务")
            else:
                print("📭 没有带截止日期的任务")
            return

        if args.sort == "priority":
            priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
            due_tasks.sort(key=lambda x: (x[2], priority_order.get(x[0].priority, 1)))
        else:
            due_tasks.sort(key=lambda x: x[2])

        print("\n📅 即将到期的任务")
        if args.days is not None:
            print(f"时间范围：{args.days} 天内")
        print("-" * 60)

        priority_icons = {
            Priority.HIGH: "🔴",
            Priority.MEDIUM: "🟡",
            Priority.LOW: "🟢",
        }
        overdue_count = 0

        for task, due_date, days_left in due_tasks:
            status = "✅" if task.done else "⭕"
            priority_icon = priority_icons.get(task.priority, "🟡")

            if days_left < 0:
                due_str = f"已过期 {abs(days_left)} 天"
                overdue_count += 1
            elif days_left == 0:
                due_str = "今天到期 ⚠️"
            elif days_left == 1:
                due_str = "明天到期 ⚠️"
            else:
                due_str = f"剩余 {days_left} 天"

            print(
                f"{status} [{task.id}] {priority_icon} {task.content} 📅 {task.due_date} ({due_str})"
            )

        print("-" * 60)
        print(f"总计：{len(due_tasks)} 个任务", end="")
        if overdue_count > 0:
            print(f" | ⚠️ 已过期：{overdue_count} 个", end="")
        print()
