# Todo Manager 项目计划 (Project Plan)

## 1. 项目目标

### 1.1 愿景
构建一个支持 AI 自动执行的任务管理 CLI 工具，实现「提出任务 → AI 执行 → 自动验证 → 代码提交」的完整闭环。

### 1.2 核心目标
- **功能完整**：覆盖任务全生命周期管理
- **AI 集成**：无缝接入 OpenCode 自动执行
- **数据隔离**：真实任务与测试任务分离
- **质量保证**：高测试覆盖率，自动化验证
- **可扩展**：模块化架构，便于功能扩展

---

## 2. 里程碑规划

### 里程碑 1：基础重构 (M1)
**时间**：2026-03-04 ~ 2026-03-05  
**状态**：🔄 进行中

**目标**：
- 拆分 monolithic 的 todo.py
- 建立模块化目录结构
- 实现数据隔离（真实/测试任务分离存储）

**交付物**：
- [x] `core/models.py` - Task 数据类
- [x] `core/storage.py` - JSONStorage
- [x] `commands/` - CLI 命令模块
- [x] 新的精简入口文件 `todo.py`
- [ ] 数据迁移脚本

**验收标准**：
- 所有原有功能正常工作
- 真实任务存储在 `data/tasks.json`
- 测试任务存储在 `data/test-tasks.json`

---

## 3. 任务分解

### 3.1 当前任务队列

| 优先级 | 任务 | 状态 | 负责人 | 预计工时 | 实际工时 |
|--------|------|------|--------|----------|----------|
| 🔴 高 | 创建 core/storage.py 实现 JSONStorage | ✅ 已完成 | AI | 2h | 2h |
| 🔴 高 | 创建 commands/base.py 定义 Command 基类 | ✅ 已完成 | AI | 1h | 1h |
| 🔴 高 | 拆分 commands/task_commands.py 实现增删改查 | ✅ 已完成 | AI | 2h | 2h |
| 🔴 高 | 拆分 commands/query_commands.py 实现 list/stats/due | ✅ 已完成 | AI | 2h | 2h |
| 🔴 高 | 重构 todo.py 入口 | ✅ 已完成 | AI | 2h | 1h |
| 🟡 中 | 数据迁移脚本 | ⏳ 待开始 | AI | 1h | |

### 3.2 任务依赖关系

```
M1 基础重构
├── core/models.py ──┬── commands/*.py
├── core/storage.py ─┘   └── 新 todo.py
└── 数据迁移
```

---

## 4. 资源需求

### 4.1 技术资源
- Python 3.12+
- pytest + coverage
- OpenCode CLI
- Git

### 4.2 时间投入

| 里程碑 | 预计工时 | 实际工时 | 进度 |
|--------|----------|----------|------|
| M1 基础重构 | 8h | 8h | 85% |

---

*最后更新: 2026-03-04*
