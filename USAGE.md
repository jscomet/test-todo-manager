# Todo Manager 使用指南

## 📖 目录

- [快速开始](#快速开始)
- [命令详解](#命令详解)
- [数据管理](#数据管理)
- [AI 自动执行](#ai-自动执行)
- [测试与覆盖率](#测试与覆盖率)
- [常见问题](#常见问题)

---

## 🚀 快速开始

### 安装要求

- Python 3.12+
- 无需额外依赖（标准库）
- 测试需要：`pytest`, `pytest-cov`

### 基础使用

```bash
# 添加任务
python todo.py add "学习 Python 编程"

# 查看所有任务
python todo.py list

# 标记任务完成
python todo.py done 1

# 删除任务
python todo.py delete 1
```

### 高级功能

```bash
# 添加带优先级和截止日期的任务
python todo.py add "完成项目报告" --priority 高 --due 2026-03-10

# 添加带标签的任务
python todo.py add "代码审查" --tags 工作，紧急

# 查看特定标签的任务
python todo.py list --tag 工作

# 查看即将到期的任务
python todo.py due --days 7

# 统计信息
python todo.py stats

# 导出数据
python todo.py export --format csv --output tasks.csv
```

---

## 📋 命令详解

### 任务管理命令

#### `add` - 添加任务

**语法**：
```bash
python todo.py add <内容> [选项]
```

**选项**：
| 选项 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--priority` | `-p` | 优先级（高/中/低） | 中 |
| `--due` | `-d` | 截止日期 (YYYY-MM-DD) | 无 |
| `--tags` | `-t` | 标签列表（逗号分隔） | 无 |
| `--test` | | 标记为测试任务 | False |

**示例**：
```bash
# 简单任务
python todo.py add "买牛奶"

# 高优先级任务
python todo.py add "完成项目报告" -p 高

# 带截止日期
python todo.py add "提交申请" -d 2026-03-15

# 带多个标签
python todo.py add "代码审查" -t 工作，紧急，代码

# 测试任务
python todo.py add "测试新功能" --test
```

---

#### `list` - 列出任务

**语法**：
```bash
python todo.py list [选项]
```

**选项**：
| 选项 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--tag` | `-t` | 按标签筛选 | 全部 |
| `--priority` | `-p` | 按优先级筛选 | 全部 |
| `--sort` | `-s` | 排序方式（priority/due/created） | priority |
| `--include-test` | | 包含测试任务 | False |

**示例**：
```bash
# 所有任务
python todo.py list

# 按标签筛选
python todo.py list -t 工作

# 高优先级任务
python todo.py list -p 高

# 按截止日期排序
python todo.py list -s due
```

---

#### `done` - 标记任务完成

**语法**：
```bash
python todo.py done <任务 ID>
```

**示例**：
```bash
python todo.py done 1
python todo.py done 2 3 4  # 批量标记
```

---

#### `delete` - 删除任务

**语法**：
```bash
python todo.py delete <任务 ID>
```

**示例**：
```bash
python todo.py delete 1
python todo.py delete 2 3 4  # 批量删除
```

---

### 标签管理命令

#### `add-tag` - 添加标签

**语法**：
```bash
python todo.py add-tag <任务 ID> <标签>
```

**示例**：
```bash
python todo.py add-tag 1 紧急
python todo.py add-tag 2 工作
```

---

#### `remove-tag` - 移除标签

**语法**：
```bash
python todo.py remove-tag <任务 ID> <标签>
```

**示例**：
```bash
python todo.py remove-tag 1 紧急
```

---

### 优先级管理命令

#### `set-priority` - 设置优先级

**语法**：
```bash
python todo.py set-priority <任务 ID> <优先级>
```

**优先级选项**：高、中、低

**示例**：
```bash
python todo.py set-priority 1 高
python todo.py set-priority 2 低
```

---

### 查询命令

#### `stats` - 统计信息

**语法**：
```bash
python todo.py stats [选项]
```

**选项**：
| 选项 | 简写 | 说明 |
|------|------|------|
| `--tag` | `-t` | 按标签统计 |
| `--priority` | `-p` | 按优先级统计 |

**示例**：
```bash
# 总体统计
python todo.py stats

# 按标签统计
python todo.py stats -t 工作

# 按优先级统计
python todo.py stats -p 高
```

**输出示例**：
```
任务统计
====================
总任务数：10
已完成：4
未完成：6
完成率：40%

按优先级：
  高：3 (未完成：2)
  中：5 (未完成：3)
  低：2 (未完成：1)
```

---

#### `due` - 即将到期的任务

**语法**：
```bash
python todo.py due [选项]
```

**选项**：
| 选项 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--days` | `-d` | 天数范围 | 7 |
| `--sort` | `-s` | 排序方式 | due |

**示例**：
```bash
# 未来 7 天到期
python todo.py due

# 未来 30 天到期
python todo.py due -d 30

# 按优先级排序
python todo.py due -s priority
```

---

### 导出命令

#### `export` - 导出数据

**语法**：
```bash
python todo.py export [选项]
```

**选项**：
| 选项 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--format` | `-f` | 导出格式（csv/markdown） | csv |
| `--output` | `-o` | 输出文件名 | tasks.csv / tasks.md |

**示例**：
```bash
# 导出为 CSV
python todo.py export -f csv -o tasks.csv

# 导出为 Markdown
python todo.py export -f markdown -o tasks.md
```

**CSV 格式示例**：
```csv
ID,任务内容，优先级，状态，创建日期，截止日期，标签
1，学习 Python，高，未完成，2026-03-04,2026-03-10，工作，学习
2，买牛奶，低，已完成，2026-03-04,,日常
```

**Markdown 格式示例**：
```markdown
# 任务列表

| ID | 任务内容 | 优先级 | 状态 | 创建日期 | 截止日期 | 标签 |
|----|----------|--------|------|----------|----------|------|
| 1 | 学习 Python | 🔴 高 | ⏳ 未完成 | 2026-03-04 | 2026-03-10 | 工作，学习 |
| 2 | 买牛奶 | 🟢 低 | ✅ 已完成 | 2026-03-04 | - | 日常 |
```

---

### 清理命令

#### `cleanup` - 清理任务

**语法**：
```bash
python todo.py cleanup [选项]
```

**选项**：
| 选项 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--max-age` | `-a` | 最大保留小时数 | 24 |
| `--duplicates` | `-d` | 清理重复任务 | False |

**示例**：
```bash
# 清理超过 24 小时的测试任务
python todo.py cleanup

# 清理超过 48 小时的测试任务
python todo.py cleanup -a 48

# 清理重复任务
python todo.py cleanup --duplicates
```

---

### 覆盖率命令

#### `coverage` - 生成测试覆盖率报告

**语法**：
```bash
python todo.py coverage [选项]
```

**选项**：
| 选项 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--format` | `-f` | 报告格式 | html |
| `--output-dir` | `-o` | 输出目录 | tests/coverage |
| `--threshold` | | 覆盖率阈值 | 80 |
| `--branch` | | 启用分支覆盖率 | False |
| `--quiet` | `-q` | 安静模式 | False |

**格式选项**：html, xml, json, term, all

**示例**：
```bash
# 生成 HTML 报告
python todo.py coverage -f html

# 生成所有格式报告
python todo.py coverage -f all

# 启用分支覆盖率
python todo.py coverage --branch

# 安静模式
python todo.py coverage -q
```

**输出目录结构**：
```
tests/coverage/
├── html/          # HTML 报告（可在浏览器查看）
│   └── index.html
├── coverage.xml   # XML 格式（CI/CD 集成）
└── coverage.json  # JSON 格式（程序处理）
```

---

## 💾 数据管理

### 数据存储位置

| 数据类型 | 文件路径 | 说明 |
|----------|----------|------|
| 真实任务 | `data/tasks.json` | 生产环境任务 |
| 测试任务 | `data/test-tasks.json` | 自动化测试任务 |

### 数据格式

**Task 对象结构**：
```json
{
  "id": 1,
  "content": "任务内容",
  "done": false,
  "priority": "高",
  "created_at": "2026-03-04T10:00:00",
  "completed_at": null,
  "due_date": "2026-03-10",
  "tags": ["工作", "紧急"],
  "is_test": false
}
```

### 数据备份

建议定期备份数据目录：
```bash
# 手动备份
cp -r data/ data.backup.$(date +%Y%m%d)

# 或使用提供的备份脚本
./scripts/backup.sh
```

### 数据迁移

如有旧版本数据，使用迁移脚本：
```bash
python scripts/migrate_data.py
```

---

## 🤖 AI 自动执行

### BabyAGI 执行器

启动自动执行循环：
```bash
./babyagi-executor.sh
```

**工作流程**：
1. 获取待完成任务列表
2. 调用 OpenCode AI 执行任务
3. 运行测试验证
4. Git 提交变更
5. 更新任务状态
6. 循环直到所有任务完成

### 执行器配置

编辑 `config.py` 调整参数：
```python
class Config:
    EXECUTOR_CLEANUP_INTERVAL = 5      # 每 5 轮清理一次
    TEST_TASK_MAX_AGE_HOURS = 24       # 测试任务保留 24 小时
    EXECUTOR_DELAY_SECONDS = 5         # 轮询间隔
    EXECUTOR_MAX_ITER = None           # 最大执行轮数（None=无限）
```

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `TODO_DATA_DIR` | 数据目录 | `./data` |
| `TODO_TEST_MODE` | 测试模式 | `False` |
| `EXECUTOR_MAX_ITER` | 最大执行轮数 | `None` |

---

## 🧪 测试与覆盖率

### 运行测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest -m unit

# 运行集成测试
pytest -m integration

# 运行端到端测试
pytest -m e2e

# 带覆盖率
pytest --cov=. --cov-report=html
```

### 查看覆盖率报告

```bash
# 生成 HTML 报告
python todo.py coverage -f html

# 在浏览器查看
open tests/coverage/html/index.html  # macOS
xdg-open tests/coverage/html/index.html  # Linux
```

### 测试目录结构

```
tests/
├── unit/              # 单元测试
│   ├── core/         # 模型、存储
│   ├── commands/     # 命令
│   └── services/     # 业务逻辑
├── integration/      # 集成测试
├── e2e/              # 端到端测试
└── fixtures/         # 测试数据
```

---

## ❓ 常见问题

### Q: 任务 ID 如何生成？

A: 任务 ID 自动递增，从 1 开始。删除任务不会重置 ID 序列。

### Q: 如何区分真实任务和测试任务？

A: 测试任务存储在独立的 `data/test-tasks.json` 文件中，且有 `is_test: true` 标记。默认命令不显示测试任务。

### Q: 测试任务何时被清理？

A: 执行器每 5 轮自动清理超过 24 小时的测试任务。也可手动运行 `todo cleanup`。

### Q: 优先级有哪些选项？

A: 支持三种优先级：高、中、低。默认优先级为"中"。

### Q: 标签命名有什么限制？

A: 标签仅允许中文、英文、数字、下划线。建议使用简短有意义的标签名。

### Q: 如何批量操作任务？

A: `done` 和 `delete` 命令支持批量操作：
```bash
python todo.py done 1 2 3
python todo.py delete 4 5 6
```

### Q: 导出格式有哪些？

A: 支持 CSV 和 Markdown 两种格式。CSV 适合导入 Excel，Markdown 适合文档展示。

### Q: 如何查看帮助？

A: 运行以下命令查看所有可用命令：
```bash
python todo.py --help
python todo.py <command> --help  # 查看具体命令帮助
```

### Q: 数据文件损坏怎么办？

A: 
1. 检查是否有备份文件（`tasks.json.backup.*`）
2. 使用备份恢复：`cp data.backup.*/tasks.json data/`
3. 手动编辑 JSON 文件修复（注意保持格式正确）

### Q: 如何在 CI/CD 中使用？

A: 使用 XML 覆盖率报告格式，集成到 CI 流程：
```bash
python todo.py coverage -f xml
# 在 CI 配置中解析 tests/coverage/coverage.xml
```

---

## 📚 相关文档

- [SPEC.md](./SPEC.md) - 技术规范文档
- [PLAN.md](./PLAN.md) - 项目计划文档
- [AGENTS.md](./AGENTS.md) - Agent 工作流程规范
- [README.md](./README.md) - 项目说明

---

*最后更新：2026-03-04*
*版本：1.0*
