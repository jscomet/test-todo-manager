#!/usr/bin/env python3
"""
测试标签分割功能
"""

import json
import os
import subprocess
import sys

TASKS_FILE = "tasks.json"


def load_tasks():
    """加载任务"""
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tasks(tasks):
    """保存任务"""
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def run_command(cmd):
    """运行命令并返回输出"""
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, encoding="utf-8"
    )
    return result.stdout, result.stderr


def cleanup_task(task_id):
    """清理测试任务"""
    run_command(f"python3 todo.py delete {task_id}")


def test_chinese_comma_splitting():
    """测试中文逗号分割"""
    print("测试 1: 中文逗号分割标签")
    stdout, _ = run_command(
        'python3 todo.py add "测试中文逗号标签" --tags "工作，紧急，重要"'
    )
    print(f"  输出：{stdout.strip()}")

    tasks = load_tasks()
    task = tasks[-1]
    task_id = task["id"]

    expected_tags = ["工作", "紧急", "重要"]
    actual_tags = task.get("tags", [])

    print(f"  期望标签：{expected_tags}")
    print(f"  实际标签：{actual_tags}")

    if actual_tags == expected_tags:
        print("  ✅ 测试通过\n")
        cleanup_task(task_id)
        return True
    else:
        print("  ❌ 测试失败\n")
        cleanup_task(task_id)
        return False


def test_english_comma_splitting():
    """测试英文逗号分割"""
    print("测试 2: 英文逗号分割标签")
    stdout, _ = run_command(
        'python3 todo.py add "测试英文逗号标签" --tags "work,urgent,important"'
    )
    print(f"  输出：{stdout.strip()}")

    tasks = load_tasks()
    task = tasks[-1]
    task_id = task["id"]

    expected_tags = ["work", "urgent", "important"]
    actual_tags = task.get("tags", [])

    print(f"  期望标签：{expected_tags}")
    print(f"  实际标签：{actual_tags}")

    if actual_tags == expected_tags:
        print("  ✅ 测试通过\n")
        cleanup_task(task_id)
        return True
    else:
        print("  ❌ 测试失败\n")
        cleanup_task(task_id)
        return False


def test_mixed_comma_splitting():
    """测试混合逗号分割"""
    print("测试 3: 混合逗号分割标签")
    stdout, _ = run_command(
        'python3 todo.py add "测试混合逗号标签" --tags "工作，urgent,重要，test"'
    )
    print(f"  输出：{stdout.strip()}")

    tasks = load_tasks()
    task = tasks[-1]
    task_id = task["id"]

    expected_tags = ["工作", "urgent", "重要", "test"]
    actual_tags = task.get("tags", [])

    print(f"  期望标签：{expected_tags}")
    print(f"  实际标签：{actual_tags}")

    if actual_tags == expected_tags:
        print("  ✅ 测试通过\n")
        cleanup_task(task_id)
        return True
    else:
        print("  ❌ 测试失败\n")
        cleanup_task(task_id)
        return False


def test_single_tag():
    """测试单个标签"""
    print("测试 4: 单个标签（无逗号）")
    stdout, _ = run_command('python3 todo.py add "测试单个标签" --tags "single"')
    print(f"  输出：{stdout.strip()}")

    tasks = load_tasks()
    task = tasks[-1]
    task_id = task["id"]

    expected_tags = ["single"]
    actual_tags = task.get("tags", [])

    print(f"  期望标签：{expected_tags}")
    print(f"  实际标签：{actual_tags}")

    if actual_tags == expected_tags:
        print("  ✅ 测试通过\n")
        cleanup_task(task_id)
        return True
    else:
        print("  ❌ 测试失败\n")
        cleanup_task(task_id)
        return False


def test_tag_with_spaces():
    """测试带空格的标签"""
    print("测试 5: 带空格的标签（应自动去除）")
    stdout, _ = run_command(
        'python3 todo.py add "测试空格标签" --tags "工作，紧急，重要"'
    )
    print(f"  输出：{stdout.strip()}")

    tasks = load_tasks()
    task = tasks[-1]
    task_id = task["id"]

    expected_tags = ["工作", "紧急", "重要"]
    actual_tags = task.get("tags", [])

    print(f"  期望标签：{expected_tags}")
    print(f"  实际标签：{actual_tags}")

    if actual_tags == expected_tags:
        print("  ✅ 测试通过\n")
        cleanup_task(task_id)
        return True
    else:
        print("  ❌ 测试失败\n")
        cleanup_task(task_id)
        return False


def test_tag_filtering():
    """测试标签过滤功能"""
    print("测试 6: 标签过滤功能")

    stdout, _ = run_command('python3 todo.py add "过滤测试任务 1" --tags "过滤测试"')
    stdout, _ = run_command('python3 todo.py add "过滤测试任务 2" --tags "其他标签"')
    stdout, _ = run_command(
        'python3 todo.py add "过滤测试任务 3" --tags "过滤测试，重要"'
    )

    stdout, _ = run_command("python3 todo.py list --tag 过滤测试")
    print(f"  过滤结果:\n{stdout}")

    tasks = load_tasks()

    filtered_tasks = [t for t in tasks if "过滤测试" in t.get("tags", [])]

    cleanup_task(tasks[-1]["id"])
    cleanup_task(tasks[-2]["id"])
    cleanup_task(tasks[-3]["id"])

    if len(filtered_tasks) == 2:
        print("  ✅ 测试通过\n")
        return True
    else:
        print(f"  ❌ 测试失败：期望 2 个任务，找到 {len(filtered_tasks)} 个\n")
        return False


def test_add_tag_command():
    """测试 add-tag 命令"""
    print("测试 7: add-tag 命令添加单个标签")
    stdout, _ = run_command('python3 todo.py add "测试 add-tag 命令"')

    tasks = load_tasks()
    task = tasks[-1]
    task_id = task["id"]

    stdout, _ = run_command(f"python3 todo.py add-tag {task_id} 工作")
    stdout, _ = run_command(f"python3 todo.py add-tag {task_id} 紧急")

    tasks = load_tasks()
    task = [t for t in tasks if t["id"] == task_id][0]
    actual_tags = task.get("tags", [])

    print(f"  实际标签：{actual_tags}")

    expected_tags = ["工作", "紧急"]
    if actual_tags == expected_tags:
        print("  ✅ 测试通过\n")
        cleanup_task(task_id)
        return True
    else:
        print(f"  期望标签：{expected_tags}")
        print("  ❌ 测试失败\n")
        cleanup_task(task_id)
        return False


def test_remove_tag_command():
    """测试 remove-tag 命令"""
    print("测试 8: remove-tag 命令移除标签")
    stdout, _ = run_command(
        'python3 todo.py add "测试 remove-tag 命令" --tags "工作，紧急，重要"'
    )

    tasks = load_tasks()
    task = tasks[-1]
    task_id = task["id"]

    stdout, _ = run_command(f"python3 todo.py remove-tag {task_id} 紧急")

    tasks = load_tasks()
    task = [t for t in tasks if t["id"] == task_id][0]
    actual_tags = task.get("tags", [])

    print(f"  移除后标签：{actual_tags}")

    expected_tags = ["工作", "重要"]
    if actual_tags == expected_tags:
        print("  ✅ 测试通过\n")
        cleanup_task(task_id)
        return True
    else:
        print(f"  期望标签：{expected_tags}")
        print("  ❌ 测试失败\n")
        cleanup_task(task_id)
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("标签分割功能测试")
    print("=" * 60 + "\n")

    tests = [
        test_chinese_comma_splitting,
        test_english_comma_splitting,
        test_mixed_comma_splitting,
        test_single_tag,
        test_tag_with_spaces,
        test_tag_filtering,
        test_add_tag_command,
        test_remove_tag_command,
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"  ❌ 测试异常：{e}\n")
            results.append(False)

    print("=" * 60)
    print(f"测试结果：{sum(results)}/{len(results)} 通过")
    print("=" * 60)

    if all(results):
        print("🎉 所有测试通过!")
        return 0
    else:
        print("⚠️  部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
