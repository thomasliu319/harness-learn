"""
DeepSeek API 调用模块。

体验「无状态推理」：模型不知道项目背景，不能读写文件。
"""

import json
import os
import urllib.request
from typing import Optional


DEFAULT_MODEL = "deepseek-v4-pro"
DEFAULT_MAX_TOKENS = 1000
API_URL = "https://api.deepseek.com/chat/completions"


def call_api(
    prompt: str,
    *,
    api_key: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    system_prompt: Optional[str] = None,
) -> str:
    """调用 DeepSeek Chat API 并返回模型回复文本。

    参数:
        prompt: 用户消息内容。
        api_key: API 密钥，默认从环境变量 DEEPSEEK_API_KEY 读取。
        model: 模型名称。
        max_tokens: 最大输出 token 数。
        system_prompt: 可选的系统提示。

    返回:
        模型生成的文本回复。

    异常:
        ValueError: 未提供 API 密钥。
        urllib.error.URLError: 网络请求失败。
    """
    key = api_key or os.environ.get("DEEPSEEK_API_KEY", "")
    if not key:
        raise ValueError(
            "未找到 API 密钥。请设置环境变量 DEEPSEEK_API_KEY 或传入 api_key 参数。"
        )

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    data = json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
    }).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
    )

    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode())
        return result["choices"][0]["message"]["content"]
