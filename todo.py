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


def list_tasks(tag_filter=None):
    """
    列出所有任务及其状态

    按顺序显示所有任务的 ID、状态、优先级和内容
    任务状态用图标表示：✅ 已完成，⭕ 待完成
    优先级用图标表示：🔴 高，🟡 中，🟢 低

    Args:
        tag_filter (str): 可选，只显示包含此标签的任务

    Returns:
        None

    Note:
        如果没有任务，会显示提示信息
    """
    tasks = load_tasks()

    # 按标签过滤
    if tag_filter:
        tasks = [t for t in tasks if tag_filter in t.get("tags", [])]

    if not tasks:
        if tag_filter:
            print(f"📭 没有找到带标签 '{tag_filter}' 的任务")
        else:
            print("📭 暂无任务")
        return

    priority_icons = {"高": "🔴", "中": "🟡", "低": "🟢"}

    print("\n📋 任务列表:")
    if tag_filter:
        print(f"标签：#{tag_filter}")
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
    args = parser.parse_args()

    if args.command == "add":
        tags = None
        if args.tags:
            tags = [t.strip() for t in args.tags.replace('，', ',').split(',')]
        add_task(args.content, args.priority, args.due, tags)
    elif args.command == "list":
        list_tasks(args.tag)
    elif args.command == "done":
        done_task(args.id)
    elif args.command == "delete":
        delete_task(args.id)
    elif args.command == "add-tag":
        add_tag(args.id, args.tag)
    elif args.command == "remove-tag":
        remove_tag(args.id, args.tag)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
