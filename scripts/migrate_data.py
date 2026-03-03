#!/usr/bin/env python3
"""数据迁移脚本

将旧版 tasks.json 数据迁移到新架构的数据目录。
"""

import json
import shutil
from pathlib import Path
from datetime import datetime


def migrate_data():
    """迁移数据"""
    root_dir = Path(__file__).parent
    old_file = root_dir / "tasks.json"
    data_dir = root_dir / "data"
    new_tasks_file = data_dir / "tasks.json"
    test_tasks_file = data_dir / "test-tasks.json"

    # 创建数据目录
    data_dir.mkdir(exist_ok=True)

    if not old_file.exists():
        print("✅ 未找到旧版 tasks.json，无需迁移")
        return

    # 备份旧文件
    backup_file = (
        root_dir / f"tasks.json.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    shutil.copy(old_file, backup_file)
    print(f"📦 已备份旧文件到：{backup_file}")

    # 读取旧数据
    with open(old_file, "r", encoding="utf-8") as f:
        old_tasks = json.load(f)

    # 分离真实任务和测试任务
    real_tasks = []
    test_tasks = []

    for task in old_tasks:
        # 判断是否为测试任务
        is_test = (
            "test" in task.get("content", "").lower()
            or task.get("content", "").startswith("test_")
            or task.get("is_test", False)
        )

        # 迁移数据格式
        new_task = {
            "id": task.get("id"),
            "content": task.get("content", ""),
            "done": task.get("done", False),
            "priority": task.get("priority", "中"),
            "created_at": task.get("created_at", datetime.now().isoformat()),
            "completed_at": task.get("completed_at"),
            "due_date": task.get("due_date"),
            "tags": task.get("tags", []),
            "is_test": is_test,
        }

        if is_test:
            test_tasks.append(new_task)
        else:
            real_tasks.append(new_task)

    # 写入新文件
    with open(new_tasks_file, "w", encoding="utf-8") as f:
        json.dump(real_tasks, f, ensure_ascii=False, indent=2)
    print(f"✅ 已迁移 {len(real_tasks)} 个真实任务到：{new_tasks_file}")

    with open(test_tasks_file, "w", encoding="utf-8") as f:
        json.dump(test_tasks, f, ensure_ascii=False, indent=2)
    print(f"✅ 已迁移 {len(test_tasks)} 个测试任务到：{test_tasks_file}")

    # 删除旧文件（可选）
    # old_file.unlink()
    print("\n💡 提示：旧文件 tasks.json 已保留，如需删除请手动操作")


if __name__ == "__main__":
    migrate_data()
