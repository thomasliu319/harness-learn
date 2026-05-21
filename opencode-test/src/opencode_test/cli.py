"""命令行入口 — 演示裸 API 调用的「无状态」特性。"""

import sys
import os

from src.opencode_test.api import call_api

# 确保 src 目录在搜索路径中（无需 pip install）
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import textwrap


def main() -> None:
    print("=" * 60)
    print("测试：让 AI 分析当前项目的代码结构")
    print("=" * 60)

    try:
        response = call_api(
            "请分析当前项目的目录结构和代码质量，给出改进建议。"
        )
        print(response)
    except Exception as e:
        print(f"[错误] {e}")
        return

    print()
    print("=" * 60)
    print("观察：AI 能看到你的项目文件吗？")
    print("=" * 60)
    print(textwrap.dedent("""
        答案显然是不能 —— 因为我们只是发了一条纯文本消息到 API，
        没有任何文件上下文。这就是「无状态推理」的含义：

        - 模型没有项目上下文
        - 模型不能读写文件
        - 模型只能"猜"你的项目结构

        对比 Claude Code：Claude Code Agent 在每次调用时，会把
        文件内容作为上下文注入到 prompt 中，从而具备「有状态推理」能力。
    """).strip())


if __name__ == "__main__":
    main()
