#!/usr/bin/env python3
"""
Simple Todo Manager - 简单任务管理器
一个基于 BabyAGI 思想开发的 CLI 工具
"""

import argparse

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
