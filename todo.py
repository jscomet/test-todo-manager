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
            return json.load(f)
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


def add_task(content):
    """
    添加新任务到任务列表

    Args:
        content (str): 任务内容描述

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
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"✅ 已添加任务: {content}")


def list_tasks():
    """
    列出所有任务及其状态

    按顺序显示所有任务的 ID、状态和内容
    任务状态用图标表示：✅ 已完成，⭕ 待完成

    Returns:
        None

    Note:
        如果没有任务，会显示提示信息
    """
    tasks = load_tasks()
    if not tasks:
        print("📭 暂无任务")
        return

    print("\n📋 任务列表:")
    print("-" * 40)
    for task in tasks:
        status = "✅" if task["done"] else "⭕"
        print(f"{status} [{task['id']}] {task['content']}")
    print("-" * 40)
    print(f"总计: {len(tasks)} 个任务\n")


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
            print(f"🗑️  已删除任务: {deleted['content']}")
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

    # list 命令
    subparsers.add_parser("list", help="列出所有任务")

    # done 命令
    done_parser = subparsers.add_parser("done", help="标记任务完成")
    done_parser.add_argument("id", type=int, help="任务ID")

    # delete 命令
    delete_parser = subparsers.add_parser("delete", help="删除任务")
    delete_parser.add_argument("id", type=int, help="任务ID")

    args = parser.parse_args()

    if args.command == "add":
        add_task(args.content)
    elif args.command == "list":
        list_tasks()
    elif args.command == "done":
        done_task(args.id)
    elif args.command == "delete":
        delete_task(args.id)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
