# 测试目录规划方案

## 目标
- 统一测试代码组织
- 区分单元测试、集成测试、E2E测试
- 支持 fixtures 和 mocks
- 便于 CI/CD 集成

---

## 目录结构

```
tests/
├── conftest.py                 # pytest 全局配置和 fixtures
├── pytest.ini                  # pytest 配置文件
├── __init__.py
│
├── unit/                       # 单元测试（无外部依赖）
│   ├── __init__.py
│   ├── core/                   # 核心模块测试
│   │   ├── __init__.py
│   │   ├── test_models.py      # Task 数据类测试
│   │   └── test_storage.py     # 存储层测试
│   │
│   ├── commands/               # 命令模块测试
│   │   ├── __init__.py
│   │   ├── test_add_command.py
│   │   ├── test_list_command.py
│   │   ├── test_done_command.py
│   │   ├── test_delete_command.py
│   │   ├── test_export_commands.py
│   │   └── test_query_commands.py
│   │
│   ├── services/               # 服务层测试
│   │   ├── __init__.py
│   │   ├── test_task_service.py
│   │   └── test_filter_service.py
│   │
│   └── utils/                  # 工具函数测试
│       ├── __init__.py
│       ├── test_validators.py
│       └── test_cli_utils.py
│
├── integration/                # 集成测试（有外部依赖）
│   ├── __init__.py
│   ├── test_cli_integration.py     # CLI 端到端测试
│   ├── test_storage_integration.py # JSON 文件读写测试
│   └── test_executor_integration.py # BabyAGI 执行器测试
│
├── e2e/                        # 端到端测试（完整工作流）
│   ├── __init__.py
│   ├── test_full_workflow.py   # 完整任务生命周期测试
│   └── test_babyagi_loop.py    # BabyAGI 循环测试
│
├── fixtures/                   # 测试数据和辅助工具
│   ├── __init__.py
│   ├── sample_tasks.py         # 示例任务数据
│   ├── mock_storage.py         # Mock 存储类
│   └── temp_files.py           # 临时文件管理
│
└── coverage/                   # 覆盖率报告输出目录
    └── .gitkeep
```

---

## 详细设计

### 1. conftest.py - 全局配置

```python
"""pytest 全局配置和共享 fixtures"""
import pytest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import Mock

# 将项目根目录加入路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models import Task, Priority
from core.storage import JSONStorage


@pytest.fixture
def temp_dir():
    """创建临时目录，测试后自动清理"""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def sample_task():
    """单个示例任务"""
    return Task(
        id=1,
        content="测试任务",
        priority=Priority.MEDIUM,
        tags=["工作", "紧急"]
    )


@pytest.fixture
def sample_tasks():
    """多个示例任务列表"""
    return [
        Task(id=1, content="高优先级任务", priority=Priority.HIGH, done=False),
        Task(id=2, content="中优先级任务", priority=Priority.MEDIUM, done=True),
        Task(id=3, content="低优先级任务", priority=Priority.LOW, done=False),
        Task(id=4, content="带标签任务", priority=Priority.MEDIUM, 
             tags=["工作", "重要"], due_date="2026-03-10"),
    ]


@pytest.fixture
def mock_storage(temp_dir, sample_tasks):
    """Mock 存储对象，使用临时文件"""
    storage_path = temp_dir / "test_tasks.json"
    storage = JSONStorage(str(storage_path))
    storage.save(sample_tasks)
    return storage


@pytest.fixture
def empty_storage(temp_dir):
    """空的存储对象"""
    storage_path = temp_dir / "empty_tasks.json"
    return JSONStorage(str(storage_path))


@pytest.fixture
def test_task_factory():
    """任务工厂函数，用于动态创建任务"""
    def _create_task(task_id: int, content: str = None, **kwargs):
        return Task(
            id=task_id,
            content=content or f"测试任务_{task_id}",
            **kwargs
        )
    return _create_task


@pytest.fixture(autouse=True)
def clean_env():
    """每个测试前清理环境变量"""
    # 保存原始环境
    orig_env = os.environ.copy()
    yield
    # 恢复环境
    os.environ.clear()
    os.environ.update(orig_env)
```

### 2. pytest.ini - 配置文件

```ini
[pytest]
# 测试目录
testpaths = tests

# 文件命名模式
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# 覆盖率配置
addopts = 
    -v
    --strict-markers
    --tb=short
    --cov=core
    --cov=commands
    --cov=services
    --cov-report=term-missing
    --cov-report=html:tests/coverage/html
    --cov-report=xml:tests/coverage/coverage.xml

# 标记分类
markers =
    unit: 单元测试（快速，无外部依赖）
    integration: 集成测试（涉及文件/网络）
    e2e: 端到端测试（完整工作流）
    slow: 耗时测试
    executor: BabyAGI 执行器相关测试

# 忽略目录
norecursedirs = .git .tox build dist *.egg node_modules

# 超时设置
timeout = 60
```

### 3. 单元测试示例 (tests/unit/core/test_models.py)

```python
"""Task 模型单元测试"""
import pytest
from datetime import datetime
from core.models import Task, Priority


class TestTaskModel:
    """Task 数据类测试"""
    
    def test_task_creation(self):
        """测试基本任务创建"""
        task = Task(id=1, content="测试任务")
        
        assert task.id == 1
        assert task.content == "测试任务"
        assert task.done is False
        assert task.priority == Priority.MEDIUM
        assert task.is_test is False
    
    def test_task_with_all_fields(self):
        """测试完整字段的任务创建"""
        task = Task(
            id=2,
            content="完整任务",
            done=True,
            priority=Priority.HIGH,
            tags=["工作", "紧急"],
            due_date="2026-03-15",
            is_test=True
        )
        
        assert task.priority == Priority.HIGH
        assert task.tags == ["工作", "紧急"]
        assert task.due_date == "2026-03-15"
        assert task.is_test is True
    
    def test_task_to_dict(self):
        """测试转换为字典"""
        task = Task(id=1, content="测试")
        data = task.to_dict()
        
        assert data["id"] == 1
        assert data["content"] == "测试"
        assert "created_at" in data
    
    def test_task_from_dict(self):
        """测试从字典恢复"""
        data = {
            "id": 1,
            "content": "恢复的任务",
            "priority": "高",
            "done": False,
            "created_at": "2026-03-04T10:00:00",
            "tags": ["标签1"]
        }
        
        task = Task.from_dict(data)
        assert task.content == "恢复的任务"
        assert task.priority == Priority.HIGH
        assert task.tags == ["标签1"]


class TestPriorityEnum:
    """优先级枚举测试"""
    
    def test_priority_values(self):
        """测试优先级值"""
        assert Priority.HIGH.value == "高"
        assert Priority.MEDIUM.value == "中"
        assert Priority.LOW.value == "低"
    
    def test_priority_comparison(self):
        """测试优先级排序"""
        order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        assert order[Priority.HIGH] < order[Priority.LOW]
```

### 4. 命令测试示例 (tests/unit/commands/test_add_command.py)

```python
"""添加任务命令测试"""
import pytest
from unittest.mock import Mock, patch
from commands.task_commands import AddCommand
from core.models import Priority


class TestAddCommand:
    """添加任务命令测试"""
    
    @pytest.fixture
    def command(self):
        return AddCommand()
    
    @pytest.fixture
    def mock_args(self):
        """模拟命令行参数"""
        args = Mock()
        args.content = "新任务"
        args.priority = "中"
        args.due = None
        args.tags = None
        args.test = False
        return args
    
    def test_add_simple_task(self, command, mock_args, mock_storage):
        """测试添加简单任务"""
        with patch('commands.task_commands.TaskService') as mock_service:
            service_instance = Mock()
            mock_service.return_value = service_instance
            
            command.execute(mock_args)
            
            service_instance.create.assert_called_once_with(
                content="新任务",
                priority="中",
                due_date=None,
                tags=None,
                is_test=False
            )
    
    def test_add_task_with_tags(self, command, mock_args):
        """测试添加带标签的任务"""
        mock_args.tags = "工作, 紧急, 重要"
        
        with patch('commands.task_commands.TaskService') as mock_service:
            service_instance = Mock()
            mock_service.return_value = service_instance
            
            command.execute(mock_args)
            
            call_kwargs = service_instance.create.call_args[1]
            assert call_kwargs["tags"] == ["工作", "紧急", "重要"]
    
    def test_add_test_task(self, command, mock_args):
        """测试添加测试任务"""
        mock_args.test = True
        
        with patch('commands.task_commands.TaskService') as mock_service:
            service_instance = Mock()
            mock_service.return_value = service_instance
            
            command.execute(mock_args)
            
            call_kwargs = service_instance.create.call_args[1]
            assert call_kwargs["is_test"] is True
```

### 5. 集成测试示例 (tests/integration/test_cli_integration.py)

```python
"""CLI 集成测试"""
import pytest
import subprocess
import json
from pathlib import Path


class TestCLIIntegration:
    """命令行工具集成测试"""
    
    @pytest.fixture
    def cli(self, temp_dir):
        """CLI 运行辅助函数"""
        def _run(*args):
            result = subprocess.run(
                ["python3", "todo.py"] + list(args),
                cwd=temp_dir.parent,  # 项目根目录
                capture_output=True,
                text=True
            )
            return result
        return _run
    
    def test_add_and_list_task(self, cli, temp_dir):
        """测试添加和列出任务"""
        # 添加任务
        result = cli("add", "集成测试任务", "--priority", "高")
        assert result.returncode == 0
        assert "已添加任务" in result.stdout
        
        # 列出任务
        result = cli("list")
        assert result.returncode == 0
        assert "集成测试任务" in result.stdout
        assert "🔴" in result.stdout  # 高优先级图标
    
    def test_complete_task_workflow(self, cli):
        """测试完整任务工作流"""
        # 1. 添加任务
        cli("add", "工作流测试")
        
        # 2. 标记完成
        result = cli("done", "1")
        assert "已完成" in result.stdout
        
        # 3. 验证状态
        result = cli("list")
        assert "✅" in result.stdout
    
    def test_export_import(self, cli, temp_dir):
        """测试导出导入功能"""
        # 添加测试数据
        cli("add", "导出测试1")
        cli("add", "导出测试2", "--tags", "测试")
        
        # 导出 CSV
        export_path = temp_dir / "export.csv"
        result = cli("export", "--format", "csv", "--output", str(export_path))
        assert result.returncode == 0
        assert export_path.exists()


@pytest.mark.integration
class TestStorageIntegration:
    """存储层集成测试"""
    
    def test_json_persistence(self, temp_dir):
        """测试 JSON 持久化"""
        from core.storage import JSONStorage
        from core.models import Task
        
        storage_path = temp_dir / "tasks.json"
        storage = JSONStorage(str(storage_path))
        
        # 保存任务
        tasks = [Task(id=1, content="持久化测试")]
        storage.save(tasks)
        
        # 重新加载
        loaded = storage.load()
        assert len(loaded) == 1
        assert loaded[0].content == "持久化测试"
    
    def test_test_task_separation(self, temp_dir):
        """测试任务分离存储"""
        from core.storage import JSONStorage
        from core.models import Task
        
        storage = JSONStorage(str(temp_dir / "tasks.json"))
        
        # 混合保存真实和测试任务
        storage.save([
            Task(id=1, content="真实任务", is_test=False),
            Task(id=2, content="测试任务", is_test=True),
        ])
        
        # 验证分离存储
        assert (temp_dir / "tasks.json").exists()
        assert (temp_dir / "test-tasks.json").exists()
```

### 6. Fixtures 示例 (tests/fixtures/sample_tasks.py)

```python
"""测试数据 fixtures"""
from core.models import Task, Priority
from datetime import datetime, timedelta


def create_sample_tasks():
    """创建标准测试数据集"""
    return [
        # 不同优先级
        Task(id=1, content="高优先级未完成", priority=Priority.HIGH),
        Task(id=2, content="中优先级已完成", priority=Priority.MEDIUM, done=True),
        Task(id=3, content="低优先级未完成", priority=Priority.LOW),
        
        # 带标签
        Task(id=4, content="工作相关", tags=["工作"]),
        Task(id=5, content="紧急工作", tags=["工作", "紧急"]),
        Task(id=6, content="个人事务", tags=["个人"]),
        
        # 带截止日期
        Task(id=7, content="即将到期", due_date=(datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")),
        Task(id=8, content="已过期", due_date=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")),
        
        # 测试任务
        Task(id=9, content="测试任务1", is_test=True),
        Task(id=10, content="测试任务2", is_test=True, done=True),
    ]


def create_edge_case_tasks():
    """边界情况测试数据"""
    return [
        Task(id=1, content=""),  # 空内容
        Task(id=2, content="a" * 1000),  # 超长内容
        Task(id=3, content="特殊字符：@#$%^&*()"),
        Task(id=4, content="Unicode：日本語 한국어 العربية 🎉"),
        Task(id=5, content="换行\n内容\n测试"),
    ]


def create_bulk_tasks(count: int = 100):
    """批量任务（性能测试）"""
    return [
        Task(id=i, content=f"批量任务_{i}")
        for i in range(1, count + 1)
    ]
```

### 7. E2E 测试示例 (tests/e2e/test_full_workflow.py)

```python
"""端到端测试 - 完整工作流"""
import pytest
import subprocess
import time


@pytest.mark.e2e
@pytest.mark.slow
class TestFullWorkflow:
    """完整用户工作流测试"""
    
    def test_babyagi_simulation(self, temp_dir):
        """模拟 BabyAGI 执行流程"""
        # 准备测试环境
        tasks_file = temp_dir / "tasks.json"
        
        # 1. 创建初始任务
        subprocess.run([
            "python3", "todo.py", "add",
            "实现功能X", "--priority", "高"
        ], check=True)
        
        # 2. 添加相关测试任务
        subprocess.run([
            "python3", "todo.py", "add",
            "测试功能X", "--test"
        ], check=True)
        
        # 3. 执行任务工作流
        subprocess.run([
            "python3", "todo.py", "done", "1"
        ], check=True)
        
        # 4. 清理测试任务
        subprocess.run([
            "python3", "todo.py", "cleanup", "--max-age", "0"
        ], check=True)
        
        # 5. 验证结果
        result = subprocess.run(
            ["python3", "todo.py", "list"],
            capture_output=True,
            text=True
        )
        
        assert "实现功能X" in result.stdout
        assert "✅" in result.stdout
        assert "测试功能X" not in result.stdout  # 已清理


@pytest.mark.e2e
class TestBabyAGILoop:
    """BabyAGI 执行器 E2E 测试"""
    
    def test_executor_single_iteration(self):
        """测试执行器单轮执行"""
        from executor.runner import BabyAGIRunner
        from core.storage import JSONStorage
        
        runner = BabyAGIRunner(
            storage=JSONStorage("/tmp/test_tasks.json"),
            max_iterations=1  # 只执行一轮
        )
        
        # 添加测试任务
        runner.add_task("E2E测试任务")
        
        # 执行一轮
        result = runner.run_single()
        
        assert result.success is True
        assert result.task_completed is True
```

---

## 运行测试

```bash
# 运行所有测试
pytest

# 仅运行单元测试
pytest -m unit

# 仅运行集成测试
pytest -m integration

# 运行特定模块
pytest tests/unit/core/

# 生成覆盖率报告
pytest --cov-report=html

# 运行并打开报告
pytest --cov-report=html && open tests/coverage/html/index.html
```

---

## 测试规范

### 命名规范
- 文件: `test_*.py`
- 类: `Test*` 
- 方法: `test_*`
- fixtures: 小写，描述性名称

### 测试原则
1. **独立性**: 每个测试可独立运行
2. **确定性**: 相同输入总是相同输出
3. **快速**: 单元测试 < 100ms
4. **覆盖边界**: 空值、超大值、特殊字符

### 标记使用
```python
@pytest.mark.unit           # 单元测试
@pytest.mark.integration    # 集成测试
@pytest.mark.e2e            # 端到端
@pytest.mark.slow           # 慢速测试
@pytest.mark.executor       # BabyAGI相关
```
