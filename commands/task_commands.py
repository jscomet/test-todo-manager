"""任务操作命令模块

实现任务增删改查相关命令。
符合 SPEC.md 第 4.1 节 CLI 命令接口规范。
"""

from argparse import ArgumentParser, Namespace
from datetime import datetime

from .base import Command
from core.storage import JSONStorage
from core.models import Task, Priority


class AddCommand(Command):
    """添加任务命令"""
    
    name = "add"
    help = "添加新任务"
    
    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("content", type=str, help="任务内容")
        parser.add_argument("-p", "--priority", type=str, default="中",
                          choices=["高", "中", "低"], help="优先级")
        parser.add_argument("-d", "--due", type=str, default=None,
                          help="截止日期 (YYYY-MM-DD)")
        parser.add_argument("-t", "--tags", type=str, default=None,
                          help="标签 (逗号分隔)")
        parser.add_argument("--test", action="store_true",
                          help="标记为测试任务")
    
    def execute(self, args: Namespace) -> None:
        storage = JSONStorage()
        
        # 解析标签
        tags = []
        if args.tags:
            tags = [t.strip() for t in args.tags.split(",")]
        
        # 创建任务
        task = Task(
            id=storage.get_next_id(),
            content=args.content,
            priority=Priority.from_string(args.priority),
            due_date=args.due,
            tags=tags,
            is_test=args.test
        )
        
        storage.add_task(task)
        print(f"✅ 已添加任务：{args.content}")


class DoneCommand(Command):
    """标记任务完成命令"""
    
    name = "done"
    help = "标记任务为已完成"
    
    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("id", type=int, help="任务 ID")
    
    def execute(self, args: Namespace) -> None:
        storage = JSONStorage()
        tasks = storage.load(include_test=True)
        
        for task in tasks:
            if task.id == args.id:
                task.mark_done()
                storage.update_task(task)
                print(f"✅ 已完成任务：{task.content}")
                return
        
        print(f"❌ 未找到任务 ID: {args.id}")


class DeleteCommand(Command):
    """删除任务命令"""
    
    name = "delete"
    help = "删除任务"
    
    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("id", type=int, help="任务 ID")
    
    def execute(self, args: Namespace) -> None:
        storage = JSONStorage()
        
        if storage.delete_task(args.id):
            print(f"🗑️  已删除任务：{args.id}")
        else:
            print(f"❌ 未找到任务 ID: {args.id}")


class SetPriorityCommand(Command):
    """设置任务优先级命令"""
    
    name = "set-priority"
    help = "设置任务优先级"
    
    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("id", type=int, help="任务 ID")
        parser.add_argument("priority", type=str,
                          choices=["高", "中", "低"], help="优先级")
    
    def execute(self, args: Namespace) -> None:
        storage = JSONStorage()
        tasks = storage.load(include_test=True)
        
        for task in tasks:
            if task.id == args.id:
                task.set_priority(Priority.from_string(args.priority))
                storage.update_task(task)
                print(f"🔴 已设置任务优先级：{task.content} -> {args.priority}")
                return
        
        print(f"❌ 未找到任务 ID: {args.id}")


class AddTagCommand(Command):
    """添加标签命令"""
    
    name = "add-tag"
    help = "给任务添加标签"
    
    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("id", type=int, help="任务 ID")
        parser.add_argument("tag", type=str, help="标签名称")
    
    def execute(self, args: Namespace) -> None:
        storage = JSONStorage()
        tasks = storage.load(include_test=True)
        
        for task in tasks:
            if task.id == args.id:
                task.add_tag(args.tag)
                storage.update_task(task)
                print(f"🏷️  已添加标签：{task.content} -> +{args.tag}")
                return
        
        print(f"❌ 未找到任务 ID: {args.id}")


class RemoveTagCommand(Command):
    """移除标签命令"""
    
    name = "remove-tag"
    help = "从任务移除标签"
    
    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("id", type=int, help="任务 ID")
        parser.add_argument("tag", type=str, help="标签名称")
    
    def execute(self, args: Namespace) -> None:
        storage = JSONStorage()
        tasks = storage.load(include_test=True)
        
        for task in tasks:
            if task.id == args.id:
                task.remove_tag(args.tag)
                storage.update_task(task)
                print(f"🏷️  已移除标签：{task.content} -> -{args.tag}")
                return
        
        print(f"❌ 未找到任务 ID: {args.id}")


class CleanupCommand(Command):
    """清理测试任务命令"""
    
    name = "cleanup"
    help = "清理测试任务"
    
    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--max-age", type=int, default=24,
                          help="保留最大小时数，默认 24 小时")
        parser.add_argument("--duplicates", action="store_true",
                          help="清理重复任务")
    
    def execute(self, args: Namespace) -> None:
        storage = JSONStorage()
        
        if args.duplicates:
            # 清理重复任务
            tasks = storage.load()
            seen = set()
            duplicates = []
            for task in tasks:
                key = task.content
                if key in seen:
                    duplicates.append(task.id)
                else:
                    seen.add(key)
            
            for task_id in duplicates:
                storage.delete_task(task_id)
            
            print(f"🗑️  已清理 {len(duplicates)} 个重复任务")
        
        # 清理测试任务
        count = storage.clear_test_tasks()
        print(f"🗑️  已清理 {count} 个测试任务")
