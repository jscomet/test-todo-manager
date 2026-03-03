#!/usr/bin/env python3
"""
测试覆盖率报告生成脚本

用法:
    python scripts/generate_coverage_report.py [--format html|xml|json|term] [--output-dir PATH]

输出:
    - HTML 报告：tests/coverage/html/index.html
    - XML 报告：tests/coverage/coverage.xml
    - JSON 报告：tests/coverage/coverage.json
    - 终端报告：直接输出到 stdout
"""

import argparse
import subprocess
import sys
from pathlib import Path


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="生成测试覆盖率报告",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["html", "xml", "json", "term", "all"],
        default="all",
        help="报告格式 (默认：all)",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=Path("tests/coverage"),
        help="输出目录 (默认：tests/coverage)",
    )
    parser.add_argument(
        "--cov-dir",
        type=Path,
        default=Path("."),
        help="要统计覆盖率的目录 (默认：当前目录)",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=80,
        help="覆盖率阈值，低于此值会警告 (默认：80)",
    )
    parser.add_argument("--branch", action="store_true", help="启用分支覆盖率")
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="安静模式，只输出错误信息"
    )
    return parser.parse_args()


def run_coverage_report(args):
    """运行覆盖率报告生成"""
    import glob
    import os

    test_files = []
    test_dirs = ["tests/"]

    if os.getcwd().endswith("todo-manager"):
        test_files.extend(glob.glob("test_*.py"))

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        *test_dirs,
        *test_files,
        f"--cov={args.cov_dir}",
        "--cov-report=term-missing",
    ]

    if args.branch:
        cmd.append("--cov-branch")

    if args.fail_under:
        cmd.append(f"--cov-fail-under={args.fail_under}")

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.format in ["html", "all"]:
        html_dir = output_dir / "html"
        html_dir.mkdir(parents=True, exist_ok=True)
        cmd.append(f"--cov-report=html:{html_dir}")

    if args.format in ["xml", "all"]:
        cmd.append(f"--cov-report=xml:{output_dir}/coverage.xml")

    if args.format in ["json", "all"]:
        cmd.append(f"--cov-report=json:{output_dir}/coverage.json")

    if not args.quiet:
        print(f"运行测试覆盖率报告...")
        print(f"输出目录：{output_dir}")
        print(f"格式：{args.format}")
        print("-" * 60)

    result = subprocess.run(cmd, capture_output=False)

    return result.returncode


def print_summary(args):
    """打印覆盖率摘要"""
    if args.quiet:
        return

    print("\n" + "=" * 60)
    print("覆盖率报告生成完成！")
    print("=" * 60)

    output_dir = args.output_dir

    if args.format in ["html", "all"]:
        html_report = output_dir / "html" / "index.html"
        if html_report.exists():
            print(f"HTML 报告：file://{html_report.absolute()}")

    if args.format in ["xml", "all"]:
        xml_report = output_dir / "coverage.xml"
        if xml_report.exists():
            print(f"XML 报告：{xml_report}")

    if args.format in ["json", "all"]:
        json_report = output_dir / "coverage.json"
        if json_report.exists():
            print(f"JSON 报告：{json_report}")

    print("=" * 60)


def main():
    """主函数"""
    args = parse_args()
    args.fail_under = args.threshold

    returncode = run_coverage_report(args)
    print_summary(args)

    if returncode != 0:
        print(f"\n警告：测试覆盖率低于阈值 {args.threshold}%")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
