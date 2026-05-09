"""
MiniMax API 调用服务
"""
import os
import httpx
from typing import Optional


MINIMAX_API_URL = "https://api.minimaxi.com/v1/text/chatcompletion_v2"
DEFAULT_MODEL = "MiniMax-M2.7"


def get_api_key() -> str:
    """从环境变量获取 API Key"""
    api_key = os.getenv("MINIMAX_API_KEY") or os.getenv("MINIMAX_CN_API_KEY")
    if not api_key:
        raise ValueError("未设置 MINIMAX_API_KEY 环境变量")
    return api_key


async def call_minimax(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """
    调用 MiniMax API 获取文本生成结果

    Args:
        prompt: 输入的提示词
        model: 使用的模型

    Returns:
        API 返回的文本内容

    Raises:
        ValueError: API Key 未设置或请求参数错误
        httpx.HTTPStatusError: API 请求失败
    """
    api_key = get_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            MINIMAX_API_URL,
            headers=headers,
            json=payload
        )
        response.raise_for_status()

        data = response.json()

        # 解析 MiniMax API 返回格式
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]

        raise ValueError(f"API 返回格式异常: {data}")


def parse_summary_response(raw_text: str) -> dict:
    """
    解析 AI 返回的文本，提取总结和关键词

    Args:
        raw_text: AI 原始返回文本

    Returns:
        包含 summary 和 keywords 的字典
    """
    result = {
        "summary": "",
        "keywords": []
    }

    lines = raw_text.strip().split("\n")

    for line in lines:
        line = line.strip()
        if line.startswith("总结："):
            result["summary"] = line[3:].strip()
        elif line.startswith("关键词："):
            # 解析关键词，逗号分隔
            keywords_str = line[4:].strip()
            result["keywords"] = [k.strip() for k in keywords_str.split(",") if k.strip()]

    # 如果格式解析失败，直接返回原始文本
    if not result["summary"]:
        result["summary"] = raw_text.strip()

    return result
