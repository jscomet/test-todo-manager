# 思考记录：修复 test_export.py 测试失败

**任务 ID**: 004  
**日期**: 2026-03-04  
**工时**: 0.5h

---

## 问题分析

### 测试失败原因

运行 `pytest test_export.py` 后发现所有 25 个测试都失败，错误信息一致：
- `AttributeError: module 'todo' has no attribute 'export_csv'`
- `AttributeError: module 'todo' has no attribute 'done_task'`
- `AttributeError: module 'todo' has no attribute 'export_markdown'`

### 根本原因

在之前的重构中，将导出功能移到了 `commands/export_commands.py` 模块中，使用了 `ExportCommand` 类来实现。但是测试文件 `test_export.py` 仍然期望 `todo` 模块直接导出以下函数：
- `export_csv(filename)` - CSV 导出函数
- `export_markdown(filename)` - Markdown 导出函数
- `done_task(task_id)` - 标记任务完成函数

测试的设计是基于旧的函数式 API，而不是新的命令类 API。

---

## 解决方案

### 方案选择

**方案 1**: 修改测试文件，使用新的命令类 API
- 缺点：需要大量修改测试代码
- 缺点：测试会变得更复杂，需要 mock 命令执行

**方案 2**: 在 todo.py 中添加向后兼容的函数
- 优点：测试无需修改
- 优点：保持 API 向后兼容性
- 优点：简单直接

选择**方案 2**。

### 实现细节

在 `todo.py` 中添加三个向后兼容的函数：

1. **`done_task(task_id)`**: 简单的别名函数，调用已有的 `complete_task()`

2. **`export_csv(filename)`**: 
   - 获取存储实例
   - 加载所有任务
   - 使用 csv 模块写入文件
   - 处理空任务情况

3. **`export_markdown(filename)`**:
   - 获取存储实例
   - 加载所有任务
   - 生成 Markdown 表格格式
   - 包含统计信息
   - 处理管道符转义

### 额外修改

添加 `import csv` 到 todo.py 的导入语句中，因为 `export_csv` 函数需要使用 csv 模块。

---

## 测试验证

运行测试：
```bash
python3 -m pytest test_export.py -v
```

结果：**25 passed in 0.06s** ✅

所有测试通过，包括：
- CSV 导出测试（11 个）
- Markdown 导出测试（12 个）
- 边界情况测试（2 个）

---

## 经验总结

1. **向后兼容性很重要**：在重构时，要保持旧 API 的兼容性，特别是当有测试依赖这些 API 时

2. **函数式 API vs 命令类 API**：两者可以共存，函数式 API 适合简单调用和测试，命令类 API 适合 CLI 集成

3. **测试驱动重构**：通过测试可以快速发现重构后的兼容性问题

---

## 相关文件

- 修改文件：`todo.py`
- 测试文件：`test_export.py`
- 参考规范：SPEC.md 第 4.1 节（CLI 命令接口）
