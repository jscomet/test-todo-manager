# Simple Todo Manager + BabyAGI Executor

基于 BabyAGI 思想的自动化任务执行项目。

## 🚀 快速开始

### 基础 CLI 使用
```bash
# 添加任务
python todo.py add "学习 Python"

# 查看任务列表
python todo.py list

# 标记任务完成
python todo.py done 1

# 删除任务
python todo.py delete 1
```

### BabyAGI 自动执行器 🎯

```bash
# 启动 BabyAGI 风格的自动任务执行
./babyagi-executor.sh
```

执行器工作流程：
1. 获取任务列表中的第一个待完成任务
2. 调用 opencode AI 执行该任务
3. 测试执行结果
4. Git 提交并推送更改
5. opencode 更新任务状态
6. 循环直到所有任务完成

## 📋 命令说明

### todo.py 命令
| 命令 | 说明 | 示例 |
|------|------|------|
| `add` | 添加任务 | `python todo.py add "买牛奶"` |
| `list` | 列出所有任务 | `python todo.py list` |
| `done` | 标记任务完成 | `python todo.py done 1` |
| `delete` | 删除任务 | `python todo.py delete 1` |

### babyagi-executor.sh
| 命令 | 说明 |
|------|------|
| `./babyagi-executor.sh` | 启动自动任务执行循环 |

## 🏗️ 项目结构

```
todo-manager/
├── todo.py               # 主程序
├── babyagi-executor.sh   # BabyAGI 风格自动执行器 ⭐
├── tasks.json            # 任务数据
├── README.md             # 说明文档
└── execution.log         # 执行日志
```

## 🤖 BabyAGI 执行流程

```
┌─────────────────────────────────────────────┐
│           BabyAGI 执行循环                   │
├─────────────────────────────────────────────┤
│ 1. 读取任务列表，获取第一个待完成任务          │
│ 2. 调用 opencode AI 分析并执行任务            │
│ 3. 执行功能测试                              │
│ 4. Git 提交并推送到 GitHub                   │
│ 5. opencode 更新任务状态或创建新任务          │
│ 6. 重复直到所有任务完成                      │
└─────────────────────────────────────────────┘
```

## 💡 技术特点

### Todo Manager
- 纯 Python 标准库，无需额外依赖
- JSON 数据存储，方便查看和备份
- 支持中文任务内容
- 自动任务编号管理

### BabyAGI Executor
- 自动化任务执行循环
- 集成 opencode AI 编程助手
- 自动 Git 版本控制
- 详细的执行日志

## 📝 使用示例

### 1. 准备任务列表
编辑 `tasks.json` 添加开发任务：
```json
[
  {
    "id": 1,
    "content": "添加任务优先级功能",
    "done": false
  },
  {
    "id": 2, 
    "content": "优化代码结构",
    "done": false
  }
]
```

### 2. 启动自动执行
```bash
./babyagi-executor.sh
```

### 3. 观察执行过程
- 执行器会自动调用 opencode 完成任务
- 每个任务完成后自动测试
- 自动提交到 GitHub
- 任务全部完成后自动退出

## 🔧 开发思路

本项目采用 BabyAGI 的核心思想：
1. **任务列表**：明确定义需要完成的功能
2. **循环执行**：逐个获取并执行任务
3. **AI 驱动**：使用 opencode 自动编写代码
4. **持续集成**：每个任务完成后自动提交
5. **反馈优化**：根据结果调整后续任务

---

*Created by OpenClaw + BabyAGI + opencode*
