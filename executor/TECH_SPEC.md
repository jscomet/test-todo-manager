# BabyAGI Executor 技术规范

## 1. 项目概述

### 1.1 定位
BabyAGI Executor 是一个**极简的 AI 驱动开发执行器**，通过 Prompt + OpenCode 实现任务的自动执行与修复。

### 1.2 核心设计原则

| 原则 | 实现方式 |
|------|----------|
| **Agent 极简** | Prompt 模板 + OpenCode 调用，不封装复杂 Agent 类 |
| **记忆简化** | 文件-based（JSON + Markdown），**无向量数据库** |
| **工具零实现** | **完全依赖 OpenCode 内置工具**（read/edit/exec） |

### 1.3 系统边界

- **输入**: `tasks/tasks.json` 中的开发任务
- **输出**: 代码修改、测试验证、Git 提交
- **不处理**: 用户业务数据（`data/tasks.json`）

---

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────────────────────────────────┐
│           BabyAGI Executor              │
│           (Python 脚本)                 │
└─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
   ┌────────┐  ┌────────┐  ┌────────┐
   │  Task  │  │ Prompt │  │ Memory │
   │ Queue  │──│ Engine │──│ Store  │
   │(tasks) │  │(OpenCo)│  │(Files) │
   └────────┘  └────────┘  └────────┘
                    │
                    ▼
            ┌───────────────┐
            │  OpenCode CLI │
            │ (内置工具集)  │
            └───────────────┘
```

### 2.2 模块职责

| 模块 | 职责 | 关键文件 |
|------|------|----------|
| **Task Queue** | 从 tasks.json 读取任务，维护状态 | `tasks/manager.py` |
| **Prompt Engine** | 根据任务类型选择 Prompt 模板 | `prompts/*.txt` |
| **Memory Store** | 保存/加载上下文和经验 | `memory/*.py` |
| **OpenCode Client** | 调用 OpenCode CLI 执行任务 | `opencode/client.py` |

---

## 3. 核心数据模型

### 3.1 Task 结构

```python
@dataclass
class Task:
    id: str                    # 唯一标识，如 "task-001"
    objective: str             # 目标描述
    task_type: TaskType        # coder / repair / planner / docs
    priority: str              # 🔴🟡🟢
    status: TaskStatus         # pending / executing / completed / failed
    context: Dict              # 额外上下文（包含 attempts）

# tasks.json 中的完整字段
{
  "id": "task-001",
  "objective": "实现功能",
  "type": "coder",
  "priority": "🔴",
  "status": "pending",
  "assignee": "AI",
  "estimated_hours": 1.0,
  "actual_hours": null,
  "created_at": "2026-03-04T13:00:00",
  "started_at": null,
  "completed_at": null,
  "parent_id": null,
  "context": {},
  "tags": ["feature", "core"]
}
```

### 3.2 TaskType 枚举

```python
class TaskType(Enum):
    CODER = "coder"       # 代码开发任务
    REPAIR = "repair"     # 修复任务
    PLANNER = "planner"   # 任务分解
```

### 3.3 记忆存储结构

```json
// memory/context.json - 当前会话
{
  "current_task": "task-001",
  "last_thinking": "executor/thinking/task-001.md",
  "recent_experiences": ["exp-001", "exp-002"]
}
```

```json
// memory/experiences.json - 经验积累
[
  {
    "id": "exp-001",
    "pattern": "修复 import 错误",
    "solution": "添加缺失的 import 语句",
    "success": true,
    "count": 3
  }
]
```

---

## 4. 核心流程

### 4.1 主执行循环

```python
def main_loop():
    """BabyAGI 核心循环"""
    while True:
        # 1. 获取最高优先级任务
        task = task_queue.get_next()
        if not task:
            logger.info("所有任务完成")
            break
        
        # 2. 加载上下文记忆
        context = memory.load(task)
        
        # 3. 构建 Prompt
        prompt = build_prompt(task, context)
        
        # 4. 调用 OpenCode 执行
        result = opencode.execute(prompt)
        
        # 5. 分析结果
        if result.success:
            handle_success(task, result)
        else:
            handle_failure(task, result)
        
        # 6. 保存记忆
        memory.save(task, result)
        
        # 7. 短暂休眠
        time.sleep(config.poll_interval)
```

### 4.2 成功处理流程

```python
def handle_success(task: Task, result: ExecutionResult):
    """任务成功处理"""
    # 更新任务状态
    queue.update_status(task.id, TaskStatus.COMPLETED)
    
    # 保存思考记录
    thinking.save(task, result.output)
    
    # 记录成功经验
    memory.record_experience(task, result, success=True)
    
    # 检查是否需要生成后续任务
    if result.suggests_followup:
        new_task = generate_followup_task(task, result)
        task_queue.add(new_task)
```

### 4.3 失败处理流程

```python
def handle_failure(task: Task, result: ExecutionResult):
    """任务失败处理"""
    task.attempts += 1
    
    if task.attempts < config.max_attempts:
        # 生成修复任务
        repair_task = Task(
            id=f"repair-{task.id}-{task.attempts}",
            objective=f"修复 {task.objective}",
            task_type=TaskType.REPAIR,
            priority="🔴",
            parent_id=task.id,
            context={
                "error": result.error,
                "previous_output": result.output
            }
        )
        task_queue.add(repair_task)
        queue.update_status(task.id, TaskStatus.EXECUTING)
    else:
        # 超过最大尝试次数
        queue.update_status(task.id, TaskStatus.FAILED)
        memory.record_experience(task, result, success=False)
```

---

## 5. Prompt 设计

### 5.1 Coder Prompt

```
你是专业的 Python 开发者，负责实现功能。

## 任务
{objective}

## 上下文
{context}

## 可用工具
你可以使用以下 OpenCode 工具完成任务：
- `read <file>` - 读取文件内容
- `edit <file>` - 修改文件
- `exec <command>` - 执行命令
- `write <file> <content>` - 创建新文件

## 工作流程
请按以下步骤完成：
1. 阅读 docs/SPEC.md 了解项目规范
2. 阅读相关代码文件
3. 实现功能（创建或修改文件）
4. 运行 `pytest` 验证功能
5. 运行 `git add . && git commit -m "Feat: {objective}"`
6. 报告完成状态和文件变更

请开始工作。
```

### 5.2 Repair Prompt

```
你是专业的调试工程师，负责修复代码错误。

## 需要修复的问题
{objective}

## 错误信息
```
{error_message}
```

## 相关代码
```
{code_context}
```

## 可用工具
- `read <file>` - 读取文件
- `edit <file>` - 修改文件
- `exec <command>` - 执行命令

## 修复步骤
1. 分析错误原因
2. 定位问题代码
3. 使用 edit 工具修复代码
4. 运行 `pytest` 验证修复
5. 运行 `git commit` 提交修复
6. 报告修复结果

请开始调试。
```

### 5.3 Planner Prompt

```
你是架构师，负责将复杂任务分解为子任务。

## 原始任务
{objective}

## 任务分析
请分析这个任务的复杂度，考虑：
- 需要修改哪些模块？
- 是否有依赖关系？
- 是否可以并行执行？

## 输出要求
请将任务分解为 2-5 个子任务，每个子任务应该：
- 目标明确
- 可独立执行
- 有明确的验收标准

按优先级输出子任务列表。
```

---

## 6. OpenCode 集成

### 6.1 调用方式（Serve + Attach 模式）

```python
class OpenCodeClient:
    """OpenCode CLI 封装 - 使用 serve + attach 模式"""
    
    def __init__(self, server_url="http://localhost:4096", timeout=300):
        self.server_url = server_url
        self.timeout = timeout
        self.server_process = None
    
    def start_server(self) -> bool:
        """启动 headless OpenCode 服务器"""
        # 检查服务器是否已在运行
        # 启动 opencode serve --port 4096
        # 等待服务器就绪
    
    def execute(self, prompt: str) -> ExecutionResult:
        """
        执行 Prompt - 使用 attach 模式
        连接到运行中的 OpenCode 服务器，避免每次冷启动
        """
        # 1. 确保服务器在运行
        if not self.start_server():
            return ExecutionResult(success=False, error="服务器启动失败")
        
        # 2. 使用 attach 模式执行
        result = subprocess.run(
            ["opencode", "run", "--attach", self.server_url, prompt],
            capture_output=True,
            text=True,
            timeout=self.timeout
        )
        
        # 3. 解析结果
        return ExecutionResult(
            success=result.returncode == 0,
            output=result.stdout,
            error=result.stderr if result.returncode != 0 else None
        )
```

**优势**：
- 避免 MCP 服务器冷启动（每次可节省 10-30 秒）
- 非交互式执行，适合自动化
- 服务器保持运行，多任务复用

---

## 7. 记忆系统

### 7.1 短期记忆

```python
class ShortTermMemory:
    """当前会话记忆"""
    
    def load(self, task: Task) -> Dict:
        """加载与任务相关的上下文"""
        context = {}
        
        # 1. 加载最近 2 个思考记录
        recent_thinking = self._get_recent_thinking(2)
        context["recent_thinking"] = recent_thinking
        
        # 2. 加载相关经验
        relevant_experiences = self._find_relevant_experiences(task)
        context["relevant_experiences"] = relevant_experiences
        
        # 3. 加载父任务上下文（如果是修复任务）
        if task.parent_id:
            parent_context = self._get_parent_context(task.parent_id)
            context["parent_context"] = parent_context
        
        return context
```

### 7.2 长期记忆

```python
class LongTermMemory:
    """经验积累"""
    
    def record_experience(self, task: Task, result: ExecutionResult, success: bool):
        """记录经验"""
        experience = {
            "id": f"exp-{uuid.uuid4().hex[:8]}",
            "task_type": task.task_type.value,
            "pattern": self._extract_pattern(task, result),
            "solution": result.output if success else None,
            "error": result.error if not success else None,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        
        # 保存到文件
        self._save_experience(experience)
    
    def find_relevant(self, task: Task) -> List[Dict]:
        """查找相关经验"""
        # 基于任务类型和关键词匹配
        experiences = self._load_all_experiences()
        
        relevant = [
            exp for exp in experiences
            if exp["task_type"] == task.task_type.value
            and self._is_relevant(exp["pattern"], task.objective)
        ]
        
        # 按成功率和时间排序
        relevant.sort(key=lambda x: (x["success"], x["timestamp"]), reverse=True)
        
        return relevant[:3]  # 返回最相关的 3 条
```

---

## 8. 配置设计

### 8.1 配置文件

```yaml
# executor/config.yaml
executor:
  # 运行配置
  poll_interval: 5              # 轮询间隔（秒）
  max_attempts: 3               # 单任务最大尝试次数
  continue_on_error: true       # 错误后继续执行
  
  # OpenCode 配置
  opencode:
    timeout: 300                # OpenCode 调用超时（秒）
    model: "qwen3.5-plus"       # 默认模型
    
  # 记忆配置
  memory:
    short_term_file: "memory/context.json"
    long_term_file: "memory/experiences.json"
    max_thinking_files: 50      # 保留最近 50 个思考记录
    
  # 日志配置
  logging:
    level: "INFO"
    file: "logs/executor.log"
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

---

## 9. 目录结构

```
executor/
├── main.py                    # 入口：BabyAGI 循环
├── config.py                  # 配置加载
├── config.yaml                # 配置文件
│
├── core/                      # 核心模块
│   ├── task.py                # Task 数据模型
│   ├── queue.py               # 任务队列管理（使用 TaskManager）
│   └── runner.py              # 执行引擎
│
├── tasks/                     # 任务管理
│   ├── __init__.py
│   ├── manager.py             # TaskManager - JSON 任务管理
│   └── tasks.json             # 任务数据文件
│
├── prompts/                   # Prompt 模板
│   ├── __init__.py
│   ├── coder.txt              # Coder Prompt
│   ├── repair.txt             # Repair Prompt
│   └── planner.txt            # Planner Prompt
│
├── opencode/                  # OpenCode 集成
│   ├── __init__.py
│   └── client.py              # OpenCode 调用封装（serve+attach 模式）
│
├── memory/                    # 记忆系统
│   ├── __init__.py
│   ├── short_term.py          # 短期记忆
│   ├── long_term.py           # 长期记忆
│   └── thinking.py            # 思考记录管理
│
├── logs/                      # 日志目录
│   └── executor.log
│
└── thinking/                  # 思考记录（保留原有）
    └── task-*.md
```

---

## 10. 实现计划

### Phase 1: 基础框架 (1 天)

| 任务 | 文件 | 说明 |
|------|------|------|
| 1.1 目录结构 | - | 创建 `executor/` 子目录 |
| 1.2 配置系统 | `config.py`, `config.yaml` | 配置加载与管理 |
| 1.3 Task 模型 | `core/task.py` | Task 数据类 |
| 1.4 任务队列 | `core/queue.py` | PLAN.md 读写 + 队列管理 |
| 1.5 主循环 | `main.py` | BabyAGI 基础循环 |

**验收标准**: 能读取 PLAN.md 并循环输出任务

### Phase 2: OpenCode 集成 (1 天)

| 任务 | 文件 | 说明 |
|------|------|------|
| 2.1 OpenCode 客户端 | `opencode/client.py` | 封装 opencode run 调用 |
| 2.2 结果解析 | `opencode/parser.py` | 解析 stdout/stderr |
| 2.3 Prompt 模板 | `prompts/*.txt` | 三种 Prompt 模板 |
| 2.4 集成测试 | - | 验证完整执行流程 |

**验收标准**: 能调用 OpenCode 完成简单任务

### Phase 3: 记忆系统 (0.5 天)

| 任务 | 文件 | 说明 |
|------|------|------|
| 3.1 短期记忆 | `memory/short_term.py` | 当前会话状态 |
| 3.2 长期记忆 | `memory/long_term.py` | 经验积累 |
| 3.3 思考记录 | `memory/thinking.py` | thinking/ 管理 |
| 3.4 记忆加载 | - | 自动加载最近 2 个 thinking |

**验收标准**: 记忆正确加载和保存

### Phase 4: 自动修复 (1 天)

| 任务 | 文件 | 说明 |
|------|------|------|
| 4.1 失败检测 | `core/result.py` | 检测结果和错误类型 |
| 4.2 修复任务生成 | `core/runner.py` | 失败时生成修复任务 |
| 4.3 错误上下文 | `memory/short_term.py` | 传递错误信息 |
| 4.4 修复流程测试 | - | 验证修复循环 |

**验收标准**: 任务失败时自动生成并执行修复任务

### Phase 5: 完善 (0.5 天)

| 任务 | 文件 | 说明 |
|------|------|------|
| 5.1 日志增强 | - | 结构化日志输出 |
| 5.2 状态持久化 | `memory/short_term.py` | 重启后恢复状态 |
| 5.3 配置调优 | `config.yaml` | 优化默认参数 |
| 5.4 文档完善 | - | 代码注释和 README |

**验收标准**: 稳定运行，重启可恢复

---

## 11. 使用方式

### 启动执行器

```bash
cd executor
python main.py
```

### 预期输出

```
🚀 BabyAGI Executor 启动
📋 从 tasks.json 加载: 12 个待处理 / 12 个总计

🔄 第 1 轮
📝 任务: [🔴] 设计执行器技术架构
💾 加载上下文: 1 个思考记录
🤖 调用 OpenCode...
    [OpenCode] 读取 SPEC.md...
    [OpenCode] 创建代码文件...
    [OpenCode] 运行 pytest...
    [OpenCode] git commit...
✅ 任务完成
📝 保存思考: thinking/task-task-029.md
⏳ 等待 5 秒...

🔄 第 2 轮
...
```

---

## 12. 风险评估

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| OpenCode 调用失败 | 中 | 高 | 指数退避重试，记录失败任务 |
| 修复循环死循环 | 低 | 高 | 限制 max_attempts，人工标记 |
| Prompt 效果不佳 | 中 | 中 | 迭代优化 Prompt 模板 |
| 状态丢失 | 低 | 高 | 频繁 checkpoint，原子写入 |

---

## 附录

### A. 依赖清单

```
# Python 标准库
- dataclasses
- json
- subprocess
- pathlib
- datetime
- re
- time
- uuid

# 无需第三方库
```

### B. 外部依赖

- Python 3.10+
- OpenCode CLI (已安装配置)
- Git

### C. 参考资源

- BabyAGI: https://github.com/yoheinakajima/babyagi
- OpenCode: https://github.com/opencode-ai/opencode
