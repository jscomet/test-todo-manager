#!/usr/bin/env python3
"""
Simple Todo Manager - 简单任务管理器
一个基于 BabyAGI 思想开发的 CLI 工具
"""

import argparse
import json
import os
from datetime import datetime

# 任务存储文件
TASKS_FILE = "tasks.json"


def load_tasks():
    """
    从 JSON 文件加载任务列表

    Returns:
        list: 任务列表，每个任务为字典格式
              如果文件不存在则返回空列表
    """
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            tasks = json.load(f)
            # 向后兼容：为现有任务添加默认优先级
            for task in tasks:
                if "priority" not in task:
                    task["priority"] = "中"
            return tasks
    return []


def save_tasks(tasks):
    """
    保存任务列表到 JSON 文件

    Args:
        tasks (list): 任务列表，每个任务为字典格式

    Returns:
        None

    Raises:
        IOError: 当文件写入失败时抛出异常
    """
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def add_task(content, priority="中", due_date=None, tags=None):
    """
    添加新任务到任务列表

    Args:
        content (str): 任务内容描述
        priority (str): 任务优先级，可选值：高/中/低，默认为"中"
        due_date (str): 任务截止日期，格式：YYYY-MM-DD，可选
        tags (list): 任务标签列表，可选

    Returns:
        None

    Note:
        新任务会自动分配 ID，并设置 created_at 时间戳
    """
    tasks = load_tasks()
    task = {
        "id": len(tasks) + 1,
        "content": content,
        "done": False,
        "priority": priority,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    if due_date:
        task["due_date"] = due_date
    if tags:
        task["tags"] = tags
    tasks.append(task)
    save_tasks(tasks)
    print(f"✅ 已添加任务：{content}")


def list_tasks(tag_filter=None, sort_by="priority", priority_filter=None):
    """
    列出所有任务及其状态

    按顺序显示所有任务的 ID、状态、优先级和内容
    任务状态用图标表示：✅ 已完成，⭕ 待完成
    优先级用图标表示：🔴 高，🟡 中，🟢 低

    Args:
        tag_filter (str): 可选，只显示包含此标签的任务
        sort_by (str): 排序方式，可选值：priority（优先级）/ created（创建时间）/ none（不排序）
                      默认为 priority
        priority_filter (str): 可选，只显示指定优先级的任务（高/中/低）

    Returns:
        None

    Note:
        如果没有任务，会显示提示信息
    """
    tasks = load_tasks()

    # 按标签过滤
    if tag_filter:
        tasks = [t for t in tasks if tag_filter in t.get("tags", [])]

    # 按优先级过滤
    if priority_filter:
        tasks = [t for t in tasks if t.get("priority", "中") == priority_filter]

    if not tasks:
        if tag_filter:
            print(f"📭 没有找到带标签 '{tag_filter}' 的任务")
        elif priority_filter:
            print(f"📭 没有找到优先级为 '{priority_filter}' 的任务")
        else:
            print("📭 暂无任务")
        return

    # 按优先级排序
    if sort_by == "priority":
        priority_order = {"高": 0, "中": 1, "低": 2}
        tasks = sorted(
            tasks, key=lambda t: priority_order.get(t.get("priority", "中"), 1)
        )

    priority_icons = {"高": "🔴", "中": "🟡", "低": "🟢"}

    print("\n📋 任务列表:")
    if tag_filter:
        print(f"标签：#{tag_filter}")
    if priority_filter:
        print(f"优先级：{priority_filter}")
    print("-" * 50)
    for task in tasks:
        status = "✅" if task["done"] else "⭕"
        priority = task.get("priority", "中")
        priority_icon = priority_icons.get(priority, "🟡")
        due_date = task.get("due_date")
        due_str = f" 📅 {due_date}" if due_date else ""
        tags = task.get("tags", [])
        tags_str = f" 🔖 {' '.join([f'#{t}' for t in tags])}" if tags else ""
        print(
            f"{status} [{task['id']}] {priority_icon} {task['content']}{due_str}{tags_str}"
        )
    print("-" * 50)
    print(f"总计：{len(tasks)} 个任务\n")


def done_task(task_id):
    """
    标记指定 ID 的任务为已完成

    Args:
        task_id (int): 要标记完成的任务 ID

    Returns:
        None

    Note:
        如果任务不存在，会打印错误提示
    """
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
            save_tasks(tasks)
            print(f"✅ 任务 {task_id} 已完成: {task['content']}")
            return
    print(f"❌ 未找到任务 {task_id}")


def delete_task(task_id):
    """
    删除指定 ID 的任务

    Args:
        task_id (int): 要删除的任务 ID

    Returns:
        None

    Note:
        删除后会自动重新编号剩余任务的 ID
        如果任务不存在，会打印错误提示
    """
    tasks = load_tasks()
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            deleted = tasks.pop(i)
            # 重新编号
            for j, t in enumerate(tasks):
                t["id"] = j + 1
            save_tasks(tasks)
            print(f"🗑️  已删除任务：{deleted['content']}")
            return
    print(f"❌ 未找到任务 {task_id}")


def add_tag(task_id, tag):
    """
    为指定任务添加标签

    Args:
        task_id (int): 任务 ID
        tag (str): 要添加的标签

    Returns:
        None

    Note:
        如果任务不存在，会打印错误提示
        如果标签已存在，不会重复添加
    """
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            if "tags" not in task:
                task["tags"] = []
            if tag not in task["tags"]:
                task["tags"].append(tag)
                save_tasks(tasks)
                print(f"✅ 已为任务 {task_id} 添加标签：#{tag}")
            else:
                print(f"⚠️  标签 #{tag} 已存在")
            return
    print(f"❌ 未找到任务 {task_id}")


def remove_tag(task_id, tag):
    """
    从指定任务移除标签

    Args:
        task_id (int): 任务 ID
        tag (str): 要移除的标签

    Returns:
        None

    Note:
        如果任务不存在，会打印错误提示
        如果标签不存在，会打印提示信息
    """
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            tags = task.get("tags", [])
            if tag in tags:
                tags.remove(tag)
                save_tasks(tasks)
                print(f"✅ 已从任务 {task_id} 移除标签：#{tag}")
            else:
                print(f"⚠️  标签 #{tag} 不存在")
            return
    print(f"❌ 未找到任务 {task_id}")


def set_priority(task_id, new_priority):
    """
    修改指定任务的优先级

    Args:
        task_id (int): 任务 ID
        new_priority (str): 新的优先级，可选值：高/中/低

    Returns:
        None

    Note:
        如果任务不存在，会打印错误提示
    """
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            old_priority = task.get("priority", "中")
            task["priority"] = new_priority
            save_tasks(tasks)
            print(f"✅ 任务 {task_id} 优先级已修改：{old_priority} → {new_priority}")
            print(f"   内容：{task['content']}")
            return
    print(f"❌ 未找到任务 {task_id}")


def export_csv(filename=None):
    """
    导出任务列表为 CSV 格式

    Args:
        filename (str): 输出文件名，默认为 tasks_export.csv

    Returns:
        None

    Note:
        CSV 包含列：ID, 内容，状态，优先级，创建时间，截止日期，标签
    """
    import csv

    tasks = load_tasks()
    if not tasks:
        print("📭 暂无任务可导出")
        return

    if filename is None:
        filename = "tasks_export.csv"

    with open(filename, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["ID", "内容", "状态", "优先级", "创建时间", "截止日期", "标签"]
        )
        for task in tasks:
            status = "已完成" if task["done"] else "待完成"
            tags = ", ".join(task.get("tags", []))
            writer.writerow(
                [
                    task["id"],
                    task["content"],
                    status,
                    task.get("priority", "中"),
                    task.get("created_at", ""),
                    task.get("due_date", ""),
                    tags,
                ]
            )
    print(f"✅ 已导出 {len(tasks)} 个任务到：{filename}")


def export_markdown(filename=None):
    """
    导出任务列表为 Markdown 格式

    Args:
        filename (str): 输出文件名，默认为 tasks_export.md

    Returns:
        None

    Note:
        Markdown 包含任务表格和统计信息
    """
    tasks = load_tasks()
    if not tasks:
        print("📭 暂无任务可导出")
        return

    if filename is None:
        filename = "tasks_export.md"

    completed = sum(1 for t in tasks if t["done"])
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
            status = "✅" if task["done"] else "⭕"
            due = task.get("due_date", "-")
            tags = " ".join([f"#{t}" for t in task.get("tags", [])]) or "-"
            content = task["content"].replace("|", "\\|")
            f.write(
                f"| {task['id']} | {status} | {task.get('priority', '中')} | {content} | {due} | {tags} |\n"
            )
        f.write("\n## 统计信息\n\n")
        f.write(
            f"- 完成进度：{completed}/{len(tasks)} ({completed * 100 // len(tasks) if len(tasks) > 0 else 0}%)\n"
        )
        f.write(f"- 导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    print(f"✅ 已导出 {len(tasks)} 个任务到：{filename}")


def stats(tag_filter=None, priority_filter=None):
    """
    显示任务优先级统计信息

    Args:
        tag_filter (str): 可选，只显示包含此标签的任务统计
        priority_filter (str): 可选，只显示指定优先级的统计

    Returns:
        None

    Note:
        显示各优先级任务数量、完成情况和百分比
    """
    tasks = load_tasks()

    if tag_filter:
        tasks = [t for t in tasks if tag_filter in t.get("tags", [])]

    if priority_filter:
        tasks = [t for t in tasks if t.get("priority", "中") == priority_filter]

    if not tasks:
        if tag_filter:
            print(f"📭 没有找到带标签 '{tag_filter}' 的任务")
        elif priority_filter:
            print(f"📭 没有找到优先级为 '{priority_filter}' 的任务")
        else:
            print("📭 暂无任务")
        return

    total = len(tasks)
    completed = sum(1 for t in tasks if t["done"])
    pending = total - completed

    high_priority = [t for t in tasks if t.get("priority", "中") == "高"]
    medium_priority = [t for t in tasks if t.get("priority", "中") == "中"]
    low_priority = [t for t in tasks if t.get("priority", "中") == "低"]

    high_completed = sum(1 for t in high_priority if t["done"])
    medium_completed = sum(1 for t in medium_priority if t["done"])
    low_completed = sum(1 for t in low_priority if t["done"])

    print("\n📊 任务统计")
    if tag_filter:
        print(f"标签：#{tag_filter}")
    if priority_filter:
        print(f"优先级：{priority_filter}")
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


def main():
    """
    程序主入口函数

    解析命令行参数并执行相应的命令：
    - add: 添加新任务
    - list: 列出所有任务
    - done: 标记任务完成
    - delete: 删除任务

    Returns:
        None

    Note:
        不带参数时会显示帮助信息
    """
    parser = argparse.ArgumentParser(
        description="Simple Todo Manager - 简单任务管理器", prog="todo"
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # add 命令
    add_parser = subparsers.add_parser("add", help="添加任务")
    add_parser.add_argument("content", help="任务内容")
    add_parser.add_argument(
        "--priority",
        "-p",
        choices=["高", "中", "低"],
        default="中",
        help="任务优先级（高/中/低），默认为中",
    )
    add_parser.add_argument(
        "--due",
        "-d",
        help="任务截止日期（格式：YYYY-MM-DD）",
    )
    add_parser.add_argument(
        "--tags",
        "-t",
        help="任务标签（逗号分隔，如：工作，紧急）",
    )

    # list 命令
    list_parser = subparsers.add_parser("list", help="列出所有任务")
    list_parser.add_argument(
        "--tag",
        help="按标签过滤",
    )
    list_parser.add_argument(
        "--priority",
        "-p",
        choices=["高", "中", "低"],
        help="按优先级过滤（高/中/低）",
    )
    list_parser.add_argument(
        "--sort",
        "-s",
        choices=["priority", "created", "none"],
        default="priority",
        help="排序方式（priority/created/none），默认为 priority",
    )

    # done 命令
    done_parser = subparsers.add_parser("done", help="标记任务完成")
    done_parser.add_argument("id", type=int, help="任务ID")

    # delete 命令
    delete_parser = subparsers.add_parser("delete", help="删除任务")
    delete_parser.add_argument("id", type=int, help="任务ID")

    # add-tag 命令
    add_tag_parser = subparsers.add_parser("add-tag", help="为任务添加标签")
    add_tag_parser.add_argument("id", type=int, help="任务 ID")
    add_tag_parser.add_argument("tag", help="标签名称")

    # remove-tag 命令
    remove_tag_parser = subparsers.add_parser("remove-tag", help="从任务移除标签")
    remove_tag_parser.add_argument("id", type=int, help="任务 ID")
    remove_tag_parser.add_argument("tag", help="标签名称")

    # set-priority 命令
    set_priority_parser = subparsers.add_parser("set-priority", help="修改任务优先级")
    set_priority_parser.add_argument("id", type=int, help="任务 ID")
    set_priority_parser.add_argument(
        "priority",
        choices=["高", "中", "低"],
        help="新的优先级（高/中/低）",
    )

    # export 命令
    export_parser = subparsers.add_parser("export", help="导出任务列表")
    export_parser.add_argument(
        "--format",
        "-f",
        choices=["csv", "markdown"],
        default="csv",
        help="导出格式（csv/markdown），默认为 csv",
    )
    export_parser.add_argument(
        "--output",
        "-o",
        help="输出文件名（默认：tasks_export.csv 或 tasks_export.md）",
    )

    # stats 命令
    stats_parser = subparsers.add_parser("stats", help="显示任务优先级统计")
    stats_parser.add_argument(
        "--tag",
        help="按标签过滤统计",
    )
    stats_parser.add_argument(
        "--priority",
        "-p",
        choices=["高", "中", "低"],
        help="按优先级过滤统计",
    )
    args = parser.parse_args()

    if args.command == "add":
        tags = None
        if args.tags:
            tags = [t.strip() for t in args.tags.replace("，", ",").split(",")]
        add_task(args.content, args.priority, args.due, tags)
    elif args.command == "list":
        list_tasks(args.tag, args.sort, args.priority)
    elif args.command == "done":
        done_task(args.id)
    elif args.command == "delete":
        delete_task(args.id)
    elif args.command == "add-tag":
        add_tag(args.id, args.tag)
    elif args.command == "remove-tag":
        remove_tag(args.id, args.tag)
    elif args.command == "set-priority":
        set_priority(args.id, args.priority)
    elif args.command == "export":
        if args.format == "csv":
            export_csv(args.output)
        else:
            export_markdown(args.output)
    elif args.command == "stats":
        stats(args.tag, args.priority)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
