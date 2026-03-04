# Todo Manager 技术规范 (Technical Specification)

## 1. 项目概述

### 1.1 项目定位
**Todo Manager** 是一个简单的命令行待办事项管理工具。

**AI 角色**: AI 作为开发者，负责开发和维护这个工具，而不是执行待办任务。

### 1.2 核心特性
- 任务增删改查（CRUD）
- 优先级管理（高/中/低）
- 截止日期追踪
- 标签分类系统
- 数据导出（CSV/Markdown）
- 统计与查询功能

### 1.3 项目边界

| 属于本项目 | 不属于本项目 |
|-----------|-------------|
| todo CLI 工具本身 | AI 自动执行待办任务 |
| 任务管理功能 | 任务自动化执行 |
| 数据持久化 | 工作流自动化 |
| 用户交互界面 | AI Agent 执行器 |

**注意**: AI 执行器是**开发工具**，用于驱动 AI 开发和完善 todo 管理器本身，不应与 todo 应用的业务逻辑耦合。

---

## 2. 系统架构

### 2.1 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    Todo CLI 应用层                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  todo.py (CLI 入口)                                  │    │
│  │   - argparse 参数解析                                │    │
│  │   - 命令分发                                         │    │
│  └─────────────────────────────────────────────────────┘    │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Commands (命令层)                                   │    │
│  │   add / list / done / delete / export / stats / due  │    │
│  └─────────────────────────────────────────────────────┘    │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Core (核心层)                                       │    │
│  │   Task 模型 / Storage 存储 / Services 业务逻辑       │    │
│  └─────────────────────────────────────────────────────┘    │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Data (数据层)                                       │    │
│  │   data/tasks.json (用户任务数据)                     │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              
┌─────────────────────────────────────────────────────────────┐
│              AI 开发执行器 (独立工具)                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  executor/                                           │    │
│  │   - 驱动 AI 开发 todo 管理器                         │    │
│  │   - 读取 docs/PLAN.md 获取开发任务                   │    │
│  │   - 生成 executor/thinking/ 记录开发思考             │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 模块职责

| 模块 | 职责 | 说明 |
|------|------|------|
| `core` | 数据定义和持久化 | Task, Priority, JSONStorage |
| `commands` | CLI 命令解析和执行 | 用户交互层 |
| `services` | 业务逻辑封装 | 任务增删改查逻辑 |
| `data/` | 用户数据存储 | **仅存储用户任务，不含开发任务** |
| `executor/` | **AI 开发工具** | 独立运行，与 todo 应用解耦 |

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
| `coverage` | `--format`, `--output-dir`, `--threshold` | 生成测试覆盖率报告 | `todo coverage -f html` |

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

## 5. 开发执行器规范（独立工具）

**重要说明**: 本章描述的是 AI 开发执行器，这是一个**独立的开发工具**，用于驱动 AI 开发和完善 todo 管理器本身。它与 todo 应用的业务逻辑完全解耦。

### 5.1 执行器定位

| 属性 | 说明 |
|------|------|
| **类型** | 开发辅助工具 |
| **用途** | 驱动 AI 开发 todo 管理器代码 |
| **输入** | `docs/PLAN.md` 中的开发任务 |
| **输出** | 代码修改、测试、文档更新 |
| **与 todo 应用关系** | **完全独立**，不操作 `data/tasks.json` |

### 5.2 执行器架构

```
executor/
├── doc-driven-executor.sh    # 主执行脚本
├── executor.sh               # 旧版备份
├── babyagi-executor.sh       # 旧版备份
├── run-in-background.sh      # 后台启动
├── executor.log              # 执行日志
└── thinking/                 # AI 开发思考记录
    └── task-{id}-{name}.md   # 每个开发任务的思考文档
```

### 5.3 开发任务管理

**任务定义位置**: `docs/PLAN.md`

**任务格式**:
```markdown
| 优先级 | 任务名称 | 状态 | 负责人 | 预计工时 | 实际工时 |
|--------|----------|------|--------|----------|----------|
| 🔴 高 | 实现 add 命令 | ✅ 已完成 | AI | 2h | 1.5h |
| 🔴 高 | 修复 test_delete 失败 | ⏳ 待开始 | AI | 1h | |
```

**任务类型**:
- 功能开发：实现新命令、新特性
- Bug 修复：修复代码缺陷、测试失败
- 重构优化：代码结构优化、性能提升
- 文档完善：README、使用指南等

### 5.4 执行流程

```
1. 读取 docs/PLAN.md 获取待开发任务
2. 加载 executor/thinking/ 最近 2 个思考记录
3. 调用 OpenCode AI 执行任务：
   ├─ 阅读相关代码和文档
   ├─ 实现/修复代码
   ├─ 运行测试验证
   └─ 更新文档
4. Git 提交代码变更
5. 更新 docs/PLAN.md 标记任务完成
6. 创建 executor/thinking/task-xxx.md 记录思考
7. 继续下一个任务
```

### 5.5 数据隔离原则

**严格禁止**:
- ❌ 执行器修改 `data/tasks.json`（用户业务数据）
- ❌ 执行器把开发任务写入用户数据
- ❌ AI 执行 todo 应用中的待办任务

**允许操作**:
- ✅ 修改代码文件（`*.py`, `*.sh`, `*.md`）
- ✅ 创建测试文件（`test_*.py`）
- ✅ 生成开发文档（`docs/*.md`）
- ✅ 创建思考记录（`executor/thinking/*.md`）

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
