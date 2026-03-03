# Todo Manager 技术规范 (Technical Specification)

## 1. 项目概述

### 1.1 项目定位
基于 BabyAGI 理念开发的 CLI 任务管理器，支持 AI 自动执行任务闭环。

### 1.2 核心特性
- 任务增删改查（CRUD）
- 优先级管理（高/中/低）
- 截止日期追踪
- 标签分类系统
- 数据导出（CSV/Markdown）
- AI 自动执行集成
- 测试任务自动隔离与清理

---

## 2. 系统架构

### 2.1 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI 入口层                            │
│                    (todo.py / argparse)                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      命令分发层 (Commands)                    │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌────────┐ │
│  │  add    │ │  list   │ │  done   │ │ delete  │ │ export │ │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └────────┘ │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐            │
│  │add-tag  │ │rm-tag   │ │set-prio │ │ stats   │            │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     业务服务层 (Services)                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │  TaskService    │  │  FilterService  │  │ExportService│  │
│  │  - create()     │  │  - by_tag()     │  │ - to_csv()  │  │
│  │  - complete()   │  │  - by_priority()│  │ - to_md()   │  │
│  │  - delete()     │  │  - by_due()     │  │             │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据模型层 (Models)                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  class Task                                           │  │
│  │    - id: int                                          │  │
│  │    - content: str                                     │  │
│  │    - done: bool                                       │  │
│  │    - priority: Priority (Enum)                        │  │
│  │    - created_at: str                                  │  │
│  │    - completed_at: Optional[str]                      │  │
│  │    - due_date: Optional[str]                          │  │
│  │    - tags: List[str]                                  │  │
│  │    - is_test: bool                                    │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      存储层 (Storage)                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  class JSONStorage                                    │  │
│  │    - tasks.json       (真实任务)                      │  │
│  │    - test-tasks.json  (测试任务，隔离存储)              │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    AI 执行器 (Executor)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │Task Parser  │  │ BabyAGI     │  │  Cleanup Service    │  │
│  │(任务解析)   │  │ Runner      │  │  (自动清理)          │  │
│  └─────────────┘  │ (循环执行)   │  └─────────────────────┘  │
│                   └─────────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 模块职责

| 模块 | 职责 | 接口/类 |
|------|------|---------|
| `core` | 数据定义和持久化 | `Task`, `Priority`, `JSONStorage` |
| `commands` | CLI 命令解析和执行 | `AddCommand`, `ListCommand`, ... |
| `services` | 业务逻辑封装 | `TaskService`, `FilterService` |
| `executor` | AI 自动执行 | `BabyAGIRunner`, `TaskParser`, `TaskCleaner` |
| `utils` | 工具函数 | `validators`, `cli_utils` |

---

## 3. 数据模型规范

### 3.1 Task 类

```python
class Task:
    id: int                          # 唯一标识，从1递增
    content: str                     # 任务内容，长度限制 1-200字符
    done: bool = False               # 完成状态
    priority: Priority = MEDIUM      # 优先级：HIGH/MEDIUM/LOW
    created_at: str                  # ISO格式时间戳
    completed_at: Optional[str]      # 完成时间（可选）
    due_date: Optional[str]          # 截止日期 YYYY-MM-DD（可选）
    tags: List[str]                  # 标签列表（可选）
    is_test: bool = False            # 是否测试任务
```

### 3.2 Priority 枚举

```python
class Priority(Enum):
    HIGH = "高"      # 🔴 红色
    MEDIUM = "中"    # 🟡 黄色  
    LOW = "低"       # 🟢 绿色
```

### 3.3 存储格式

**tasks.json**（真实任务）
```json
[
  {
    "id": 1,
    "content": "真实任务",
    "done": false,
    "priority": "高",
    "created_at": "2026-03-04T10:00:00",
    "due_date": "2026-03-10",
    "tags": ["工作"],
    "is_test": false
  }
]
```

**test-tasks.json**（测试任务，隔离存储）
```json
[
  {
    "id": 1001,
    "content": "自动化测试任务",
    "done": true,
    "priority": "中",
    "created_at": "2026-03-04T09:00:00",
    "is_test": true
  }
]
```

---

## 4. 接口规范

### 4.1 CLI 命令接口

| 命令 | 参数 | 功能 | 示例 |
|------|------|------|------|
| `add` | `content`, `--priority`, `--due`, `--tags`, `--test` | 添加任务 | `todo add "任务" -p 高 -d 2026-03-10` |
| `list` | `--tag`, `--priority`, `--sort` | 列出任务 | `todo list --tag 工作` |
| `done` | `id` | 标记完成 | `todo done 1` |
| `delete` | `id` | 删除任务 | `todo delete 1` |
| `add-tag` | `id`, `tag` | 添加标签 | `todo add-tag 1 紧急` |
| `remove-tag` | `id`, `tag` | 移除标签 | `todo remove-tag 1 紧急` |
| `set-priority` | `id`, `priority` | 修改优先级 | `todo set-priority 1 高` |
| `export` | `--format`, `--output` | 导出数据 | `todo export -f csv -o out.csv` |
| `stats` | `--tag`, `--priority` | 统计信息 | `todo stats --tag 工作` |
| `due` | `--days`, `--sort` | 即将到期 | `todo due --days 7` |
| `cleanup` | `--max-age`, `--duplicates` | 清理测试任务 | `todo cleanup --max-age 24` |

### 4.2 Storage 接口

```python
class Storage(ABC):
    @abstractmethod
    def load(self) -> List[Task]: ...
    
    @abstractmethod  
    def save(self, tasks: List[Task]) -> None: ...
    
    @abstractmethod
    def clear_test_tasks(self) -> int: ...  # 返回清理数量
```

### 4.3 Command 接口

```python
class Command(ABC):
    name: str
    help: str
    
    @abstractmethod
    def add_arguments(self, parser: ArgumentParser) -> None: ...
    
    @abstractmethod
    def execute(self, args: Namespace) -> None: ...
```

---

## 5. 执行器规范

### 5.1 BabyAGI Runner

```python
class BabyAGIRunner:
    """AI 任务自动执行器"""
    
    def __init__(self, storage: Storage, max_iterations: int = None):
        self.storage = storage
        self.max_iterations = max_iterations  # None 表示无限循环
        self.iteration_count = 0
    
    def run(self) -> None:
        """主循环"""
        while self._should_continue():
            task = self._get_next_task()
            if not task:
                break
            self._execute_task(task)
            self._cleanup_if_needed()
    
    def run_single(self) -> ExecutionResult:
        """执行单轮"""
        pass
```

### 5.2 执行流程

```
1. 获取待完成任务
2. 调用 OpenCode AI 执行
   ├─ 生成测试用例
   ├─ 执行代码修改
   └─ 运行 pytest 验证
3. Git 提交（如有变更）
4. 标记任务完成
5. 检查是否需要清理（每5轮）
6. 等待 5 秒，回到步骤1
```

### 5.3 任务解析规则

**有效任务内容：**
- 长度 3-200 字符
- 不以 "根据分析"、"我需要"、"**" 等开头
- 不是纯数字列表项

**自动标记为测试任务：**
- 内容包含 "测试"
- 内容以 "test_" 开头
- 由执行器自动创建的任务

---

## 6. 测试规范

### 6.1 测试目录结构

```
tests/
├── unit/              # 单元测试
│   ├── core/         # 模型、存储
│   ├── commands/     # 命令
│   ├── services/     # 业务逻辑
│   └── utils/        # 工具
├── integration/      # 集成测试
├── e2e/              # 端到端测试
└── fixtures/         # 测试数据
```

### 6.2 测试标记

| 标记 | 说明 | 运行命令 |
|------|------|----------|
| `@pytest.mark.unit` | 单元测试 | `pytest -m unit` |
| `@pytest.mark.integration` | 集成测试 | `pytest -m integration` |
| `@pytest.mark.e2e` | 端到端测试 | `pytest -m e2e` |
| `@pytest.mark.slow` | 慢速测试 | 跳过或单独运行 |

### 6.3 覆盖率要求

- 整体覆盖率：≥ 80%
- 核心模块（core/）：≥ 90%
- 命令模块（commands/）：≥ 85%

---

## 7. 数据管理规范

### 7.1 目录用途

| 目录 | 用途 | 文件示例 |
|------|------|----------|
| `data/` | 生产数据 | `tasks.json`, `test-tasks.json` |
| `tests/` | 测试代码 | `test_*.py`, `conftest.py` |
| `test-output/` | 测试产物 | 导出的 CSV、临时文件 |
| `logs/` | 运行日志 | `execution.log`, `runtime.log` |
| `tests/coverage/` | 覆盖率报告 | HTML/XML 报告 |

### 7.2 任务生命周期

```
创建 → 执行 → 完成 → 清理（测试任务）
  │      │      │
  │      │      └─ 标记 done=True，记录 completed_at
  │      └─ OpenCode AI 执行代码修改
  └─ 自动检测是否为测试任务，设置 is_test 标记
```

### 7.3 清理策略

| 类型 | 策略 | 触发时机 |
|------|------|----------|
| 测试任务 | 保留 24 小时 | 每 5 轮执行后自动清理 |
| 重复任务 | 按内容去重 | 手动触发 `cleanup --duplicates` |
| 过期导出 | 保留 7 天 | 可配置定时任务 |

---

## 8. Git 规范

### 8.1 提交信息格式

```
<type>: <subject>

<body>
```

| Type | 用途 |
|------|------|
| `Feat` | 新功能 |
| `Fix` | 修复 |
| `Test` | 测试相关 |
| `Refactor` | 重构 |
| `Docs` | 文档 |

### 8.2 自动提交触发

执行器在以下情况自动提交：
- 代码文件被修改
- 测试文件被修改
- 新增测试用例

提交信息：`Feat: <任务内容>`

---

## 9. 配置规范

### 9.1 配置文件 (config.py)

```python
class Config:
    # 路径
    DATA_DIR = Path("data")
    TASKS_FILE = DATA_DIR / "tasks.json"
    
    # 执行器
    EXECUTOR_CLEANUP_INTERVAL = 5      # 每5轮清理一次
    TEST_TASK_MAX_AGE_HOURS = 24       # 测试任务保留24小时
    EXECUTOR_DELAY_SECONDS = 5         # 轮询间隔5秒
    
    # 测试
    COVERAGE_THRESHOLD = 80            # 覆盖率阈值
```

### 9.2 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `TODO_DATA_DIR` | 数据目录 | `./data` |
| `TODO_TEST_MODE` | 测试模式 | `False` |
| `EXECUTOR_MAX_ITER` | 最大执行轮数 | `None`（无限）|

---

## 10. 异常处理

### 10.1 自定义异常

```python
class TodoException(Exception):
    """基础异常"""
    pass

class TaskNotFoundError(TodoException):
    """任务不存在"""
    pass

class InvalidTaskError(TodoException):
    """无效任务内容"""
    pass

class StorageError(TodoException):
    """存储操作失败"""
    pass
```

### 10.2 错误码

| 错误码 | 说明 | HTTP 映射 |
|--------|------|-----------|
| 1001 | 任务未找到 | 404 |
| 1002 | 无效参数 | 400 |
| 1003 | 存储错误 | 500 |
| 1004 | 任务内容无效 | 400 |

---

## 11. 性能指标

### 11.1 目标性能

| 指标 | 目标值 |
|------|--------|
| 启动时间 | < 100ms |
| 列出 1000 个任务 | < 200ms |
| 添加任务 | < 50ms |
| 导出 1000 个任务 | < 500ms |
| JSON 文件大小 | < 10MB（自动归档）|

### 11.2 优化策略

- 任务数量 > 1000 时启用分页
- 导出使用生成器减少内存占用
- 存储使用缓冲写入

---

## 12. 安全规范

### 12.1 输入验证

- 任务内容：过滤控制字符，限制长度
- 标签：仅允许中文、英文、数字、下划线
- 日期：严格校验 YYYY-MM-DD 格式

### 12.2 文件安全

- 数据文件使用 UTF-8 编码
- 临时文件写入 `test-output/` 目录
- 敏感信息（如有）不入库

---

## 附录 A：版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0 | 2026-03-04 | 初始版本，模块化重构 |

## 附录 B：术语表

| 术语 | 说明 |
|------|------|
| BabyAGI | 基于 AI 的任务自动执行框架 |
| OpenCode | AI 代码执行工具 |
| Fixture | pytest 的测试数据和环境 |
| Mock | 测试中的模拟对象 |
| Coverage | 代码测试覆盖率 |
