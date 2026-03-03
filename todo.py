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
    """加载任务列表"""
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    """保存任务列表"""
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def add_task(content):
    """添加任务"""
    tasks = load_tasks()
    task = {
        "id": len(tasks) + 1,
        "content": content,
        "done": False,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"✅ 已添加任务: {content}")

def list_tasks():
    """列出所有任务"""
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
    """标记任务完成"""
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
            save_tasks(tasks)
            print(f"✅ 任务 {task_id} 已完成: {task['content']}")
            return
    print(f"❌ 未找到任务 {task_id}")

def delete_task(task_id):
    """删除任务"""
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
    parser = argparse.ArgumentParser(
        description="Simple Todo Manager - 简单任务管理器",
        prog="todo"
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
