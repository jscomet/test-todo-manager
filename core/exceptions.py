"""自定义异常模块

定义系统的异常类体系。
符合 SPEC.md 第 10 章异常处理规范。
"""

from typing import Optional


class TodoException(Exception):
    """基础异常类

    所有自定义异常的基类
    """

    def __init__(self, message: str, error_code: Optional[int] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class TaskNotFoundError(TodoException):
    """任务未找到异常

    错误码：1001
    """

    def __init__(self, task_id: int = None, message: str = None):
        if task_id is not None:
            message = f"未找到任务 ID: {task_id}"
        elif message is None:
            message = "任务未找到"
        super().__init__(message, error_code=1001)
        self.task_id = task_id


class InvalidTaskError(TodoException):
    """无效任务内容异常

    错误码：1004
    """

    def __init__(self, message: str, error_code: int = 1004, field: Optional[str] = None):
        super().__init__(message, error_code=error_code)
        self.field = field


class InvalidParameterError(TodoException):
    """无效参数异常

    错误码：1002
    """

    def __init__(self, param_name: str, message: str = None):
        if message is None:
            message = f"无效参数 '{param_name}'"
        super().__init__(message, error_code=1002)
        self.param_name = param_name


class InvalidDateFormatError(InvalidParameterError):
    """无效日期格式异常

    错误码：1002
    """

    def __init__(self, date_value: str, expected_format: str = "YYYY-MM-DD"):
        message = f"无效日期格式 '{date_value}'，应为 {expected_format}"
        super().__init__(param_name="date", message=message)
        self.date_value = date_value
        self.expected_format = expected_format


class InvalidTagError(InvalidParameterError):
    """无效标签异常

    错误码：1002
    """

    def __init__(self, tag: str, message: str = None):
        if message is None:
            message = f"无效标签 '{tag}'，仅允许中文、英文、数字、下划线"
        super().__init__(param_name="tag", message=message)
        self.tag = tag


class StorageError(TodoException):
    """存储操作异常

    错误码：1003
    """

    def __init__(self, message: str, operation: str = None):
        super().__init__(message, error_code=1003)
        self.operation = operation


class TaskContentError(InvalidTaskError):
    """任务内容错误异常

    错误码：1004
    """

    def __init__(self, message: str, content: str = None):
        super().__init__(message, error_code=1004)
        self.content = content


class EmptyContentError(TaskContentError):
    """任务内容为空异常

    错误码：1004
    """

    def __init__(self, content: str = None):
        super().__init__("任务内容不能为空", content=content)


class ContentTooLongError(TaskContentError):
    """任务内容过长异常

    错误码：1004
    """

    def __init__(self, length: int, max_length: int = 200):
        super().__init__(f"任务内容过长 ({length} 字符)，最大长度为 {max_length} 字符")
        self.length = length
        self.max_length = max_length


class DuplicateTaskError(TodoException):
    """重复任务异常

    错误码：1005
    """

    def __init__(self, content: str):
        message = (
            f"已存在相同内容的任务：'{content[:50]}...'"
            if len(content) > 50
            else f"已存在相同内容的任务：'{content}'"
        )
        super().__init__(message, error_code=1005)
        self.content = content
