# Simple Todo Manager

基于 BabyAGI 思想开发的简单任务管理器 CLI 工具。

## 🚀 快速开始

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

## 📋 命令说明

| 命令 | 说明 | 示例 |
|------|------|------|
| `add` | 添加任务 | `python todo.py add "买牛奶"` |
| `list` | 列出所有任务 | `python todo.py list` |
| `done` | 标记任务完成 | `python todo.py done 1` |
| `delete` | 删除任务 | `python todo.py delete 1` |

## 🏗️ 项目结构

```
todo-manager/
├── todo.py          # 主程序
├── tasks.json       # 任务数据（自动生成）
└── README.md        # 说明文档
```

## 💡 技术特点

- 纯 Python 标准库，无需额外依赖
- JSON 数据存储，方便查看和备份
- 支持中文任务内容
- 自动任务编号管理

## 📝 开发思路

本项目采用 BabyAGI 的任务执行循环思想：
1. **任务分解**：将项目拆分为小功能点
2. **循环执行**：逐个实现功能
3. **结果反馈**：每个功能完成后再进行下一个

---

*Created by OpenClaw + opencode*
