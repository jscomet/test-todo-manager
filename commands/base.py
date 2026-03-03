"""命令基类模块

定义 CLI 命令的抽象基类。
符合 SPEC.md 第 4.3 节 Command 接口规范。
"""

from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace


class Command(ABC):
    """命令抽象基类

    符合 SPEC 4.3 Command 接口规范

    所有 CLI 命令都必须继承此类并实现抽象方法。
    """

    name: str = ""
    """命令名称，用于 CLI 参数解析"""

    help: str = ""
    """命令帮助信息"""

    @abstractmethod
    def add_arguments(self, parser: ArgumentParser) -> None:
        """添加命令参数

        Args:
            parser: argparse 参数解析器
        """
        pass

    @abstractmethod
    def execute(self, args: Namespace) -> None:
        """执行命令

        Args:
            args: 解析后的命令行参数
        """
        pass

    def register(self, subparsers) -> None:
        """注册命令到子解析器

        Args:
            subparsers: argparse 子解析器
        """
        parser = subparsers.add_parser(self.name, help=self.help)
        self.add_arguments(parser)
        parser.set_defaults(func=self.execute)
