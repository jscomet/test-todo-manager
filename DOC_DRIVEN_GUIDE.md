# 文档驱动执行流程说明

## 概述

本项目采用 **文档驱动** 的执行模式，所有工作基于 `SPEC.md` 和 `PLAN.md` 双文档进行。

---

## 双文档体系

### SPEC.md - 技术规范
- **位置**: `./SPEC.md`
- **用途**: 定义技术架构、接口规范、数据模型
- **读取时机**: 每个任务执行前
- **维护者**: Agent（实现时更新）

### PLAN.md - 项目计划
- **位置**: `./PLAN.md`
- **用途**: 定义任务队列、进度跟踪、里程碑
- **读取时机**: 获取任务时
- **更新时机**: 每个任务完成后（强制）

---

## 新执行器

### 执行器脚本

```bash
# 文档驱动执行器
./doc-driven-executor.sh
```

### 执行流程

```
开始
 │
 ▼
检查 SPEC.md 和 PLAN.md 存在
 │
 ▼
从 PLAN.md 获取第一个 ⏳ 待开始 任务
 │
 ▼
六阶段执行:
 ├─ 阶段 1: 任务分析（标记 🔄 进行中）
 ├─ 阶段 2-5: OpenCode AI 执行
 │   ├─ 阅读 SPEC 确定技术方案
 │   ├─ 编写代码
 │   ├─ 运行测试
 │   ├─ Git 提交
 │   └─ 更新 SPEC（如需要）
 └─ 阶段 6: 更新 PLAN（标记 ✅ 已完成）
 │
 ▼
检查 PLAN 是否还有未完成任务?
 │
 ├─ 有 ──▶ 等待5秒 ──▶ 获取下一个任务
 │
 └─ 无 ──▶ 🎉 所有任务完成，退出
```

---

## 使用方法

### 1. 准备阶段

确保文档存在:
```bash
# 检查 SPEC.md
ls -la SPEC.md

# 检查 PLAN.md
ls -la PLAN.md
```

### 2. 编辑 PLAN.md 添加任务

在 PLAN.md 中添加任务，格式:

```markdown
| 优先级 | 任务 | 状态 | 预计工时 | 实际工时 |
|--------|------|------|----------|----------|
| 🔴 高 | 创建 core/models.py | ⏳ 待开始 | 2h | |
| 🟡 中 | 创建 core/storage.py | ⏳ 待开始 | 2h | |
```

提交 PLAN.md:
```bash
git add PLAN.md
git commit -m "Docs: 添加任务计划"
git push
```

### 3. 启动执行器

```bash
# 前台运行
./doc-driven-executor.sh

# 后台运行（推荐）
nohup ./doc-driven-executor.sh > logs/executor.log 2>&1 &
```

### 4. 监控执行

```bash
# 查看执行日志
tail -f logs/executor.log

# 查看 PLAN 更新
cat PLAN.md | grep -E "(✅|⏳|🔄)"
```

### 5. 停止执行器

```bash
# 查找进程
ps aux | grep doc-driven-executor

# 停止进程
kill <PID>
```

---

## 执行器特点

### ✅ 自动文档检查
- 启动前检查 SPEC.md 和 PLAN.md 存在
- 不存在则报错退出

### ✅ 自动任务获取
- 从 PLAN.md 解析任务列表
- 只执行 ⏳ 待开始 的任务
- 自动跳过 ✅ 已完成 的任务

### ✅ 自动状态更新
- 任务开始时标记 🔄 进行中
- 任务完成时标记 ✅ 已完成
- 自动记录实际工时

### ✅ 自动完成检测
- 每轮检查 PLAN 是否全部完成
- 所有任务完成后自动退出
- 不会无限循环

### ✅ Git 自动提交
- 自动提交 PLAN.md 更新
- 提交信息格式: `Docs: 更新 PLAN 进度 - 任务名 状态`

---

## 与旧执行器对比

| 特性 | 旧执行器 (executor.sh) | 新执行器 (doc-driven-executor.sh) |
|------|------------------------|-----------------------------------|
| 任务来源 | tasks.json | PLAN.md |
| 文档驱动 | ❌ 否 | ✅ 是 |
| SPEC 检查 | ❌ 否 | ✅ 是 |
| 自动更新 PLAN | ❌ 否 | ✅ 是 |
| 完成自动退出 | ❌ 无限循环 | ✅ PLAN完成即退出 |
| 状态跟踪 | 简单完成标记 | 完整状态流转 |

---

## 任务状态流转

```
⏳ 待开始 → 🔄 进行中 → ✅ 已完成
    ↓
   失败时
    ↓
   ❌ 失败
```

---

## 常见问题

### Q: 执行器启动时报 "SPEC.md 不存在"
确保 SPEC.md 存在于项目根目录:
```bash
cp SPEC.md.example SPEC.md  # 如有示例
# 或手动创建
```

### Q: PLAN.md 中没有任务被识别
检查任务行格式:
```markdown
| 🔴 高 | 任务名称 | ⏳ 待开始 | 2h | |
      ↑ 注意这个分隔符必须是 |
```

### Q: 如何暂停执行器
```bash
# 查找并杀死进程
pkill -f doc-driven-executor
```

### Q: 如何恢复已完成的任务重新执行
编辑 PLAN.md，将状态改回 ⏳ 待开始:
```bash
sed -i 's/✅ 已完成/⏳ 待开始/g' PLAN.md
```

---

## 迁移指南

### 从旧执行器迁移

1. **停止旧执行器**:
   ```bash
   pkill -f executor.sh
   ```

2. **将 tasks.json 中的任务迁移到 PLAN.md**:
   ```bash
   # 导出待完成任务
   python3 -c "
   import json
   with open('tasks.json') as f:
       tasks = [t for t in json.load(f) if not t.get('done')]
   for t in tasks[:10]:  # 取前10个
       print(f\"| 🟡 中 | {t['content']} | ⏳ 待开始 | 2h | |\")
   "
   ```

3. **复制到 PLAN.md 任务表格中**

4. **启动新执行器**:
   ```bash
   ./doc-driven-executor.sh
   ```

---

## 配置文件

可通过环境变量配置:

```bash
# 最大迭代次数（默认100）
export MAX_ITERATIONS=50

# 启动执行器
./doc-driven-executor.sh
```

---

*最后更新: 2026-03-04*
