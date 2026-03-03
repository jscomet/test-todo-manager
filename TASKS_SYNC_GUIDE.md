# 遗留任务处理说明

## 功能概述

doc-driven-executor.sh 现在支持处理 `tasks.json` 中的遗留任务，同时保持文档驱动的核心流程。

## 工作流程

```
启动执行器
    │
    ▼
检查 SPEC.md 和 PLAN.md
    │
    ▼
【新增】同步 tasks.json 中的有效任务到 PLAN
    │   - 过滤掉测试任务 (is_test=true)
    │   - 过滤掉无效内容（分析文本、列表项等）
    │   - 将有效任务添加到 PLAN 任务队列
    ▼
从 PLAN 获取任务
    │
    ▼
六阶段执行（遵循文档驱动流程）
    │
    ▼
更新 PLAN 状态为 ✅ 已完成
    │
    ▼
【新增】同时标记 tasks.json 中的对应任务为完成
    │
    ▼
检查是否还有未完成任务
```

## 任务过滤规则

### 会同步到 PLAN 的任务：
- `done: false`（未完成）
- `is_test: false`（非测试任务）
- 内容长度 > 2 个字符
- 不以以下前缀开头：
  - `测试任务_` - 自动化测试任务
  - `test_` - 英文测试任务
  - `根据分析` - AI 分析文本
  - `我需要` - AI 思考文本
  - `**` - Markdown 格式
  - `1.`, `2.`, `3.` - 列表项

### 不会同步的任务：
- 已完成的任务 (`done: true`)
- 测试任务 (`is_test: true`)
- AI 分析文本或列表项

## 数据目录

```
data/
└── tasks.json    # 任务数据（会被同步到 PLAN）
```

## 示例 tasks.json

```json
[
  {
    "id": 1,
    "content": "实现 todo add 命令的基础功能",
    "done": false,
    "priority": "高",
    "created_at": "2026-03-04 10:00:00",
    "is_test": false
  },
  {
    "id": 2,
    "content": "测试任务_1772563690",
    "done": false,
    "priority": "中",
    "created_at": "2026-03-04 04:30:00",
    "is_test": true
  }
]
```

**结果**：
- 任务 1 会同步到 PLAN（有效任务）
- 任务 2 不会同步（is_test=true）

## 使用步骤

### 1. 准备 tasks.json

将遗留任务放入 `data/tasks.json`：

```bash
# 或者使用现有的 tasks.json
cp tasks.json data/tasks.json
```

### 2. 启动执行器

```bash
./doc-driven-executor.sh
```

执行器会自动：
1. 读取 `data/tasks.json`
2. 过滤有效任务
3. 同步到 `PLAN.md`
4. 开始文档驱动执行流程

### 3. 查看同步结果

```bash
# 查看 PLAN 中新增的任务
grep "⏳ 待开始" PLAN.md

# 查看执行日志
tail -f logs/executor.log
```

## 同步示例

**执行前 tasks.json**：
```json
[
  {"content": "实现用户登录", "done": false, "is_test": false},
  {"content": "测试任务_123", "done": false, "is_test": true},
  {"content": "根据分析，这是测试", "done": false}
]
```

**同步后 PLAN.md**：
```markdown
| 优先级 | 任务 | 状态 | 负责人 | 预计工时 | 实际工时 |
|--------|------|------|--------|----------|----------|
| 🟡 中 | 实现用户登录 | ⏳ 待开始 | AI | 2h | |
```

**注意**：测试任务和无效内容被过滤掉了。

## 双向同步

执行器会保持两个文件的同步：

| 操作 | PLAN.md | tasks.json |
|------|---------|------------|
| 启动时同步 | 新增任务 | 读取源 |
| 任务完成后 | 标记 ✅ 已完成 | 标记 `done: true` |

## 注意事项

1. **任务内容匹配**：通过 `content` 字段匹配，确保内容完全一致
2. **最多同步 20 个**：避免一次性添加过多任务
3. **Git 自动提交**：同步后会自动提交 PLAN.md 更新
4. **不会删除原任务**：只是标记为完成，不会从 tasks.json 删除

## 完整数据流

```
tasks.json (遗留任务)
    │
    │ 过滤有效任务
    ▼
sync_tasks_to_plan()
    │
    ▼
PLAN.md (新增 ⏳ 待开始 任务)
    │
    │ 文档驱动执行
    ▼
任务完成
    │
    ├──────▶ PLAN.md 标记 ✅ 已完成
    │
    └──────▶ tasks.json 标记 done: true
```
