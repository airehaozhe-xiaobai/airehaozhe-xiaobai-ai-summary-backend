"""
文本总结 Prompt 模板
"""

# 普通模式 Prompt
NORMAL_PROMPT_TEMPLATE = """你是一个专业的文本总结助手。
请对用户提供的文本进行总结，并提取关键词。

【总结要求】
- 用 3-5 句话概括原文核心内容
- 每句话不超过 30 个字
- 不要添加原文没有的信息
- 用中文输出

【关键词要求】
- 提取 3-5 个关键词
- 用逗号分隔
- 关键词必须在原文中出现

【输出格式】
总结：<你的总结>
关键词：<关键词1>, <关键词2>, ...

【待处理文本】
{user_text}"""

# 简短模式 Prompt
BRIEF_PROMPT_TEMPLATE = """你是一个简洁的文本总结助手。
请用 1-2 句话概括原文核心内容，并提取 2-3 个关键词。

【总结要求】
- 只用 1-2 句话，总字数不超过 50 字
- 不要添加原文没有的信息
- 用中文输出

【关键词要求】
- 提取 2-3 个关键词
- 用逗号分隔
- 关键词必须在原文中出现

【输出格式】
总结：<你的总结>
关键词：<关键词1>, <关键词2>, ...

【待处理文本】
{user_text}"""


def build_prompt(text: str, mode: str = "normal", max_chars: int = 6000) -> str:
    """
    构建发送给 AI 的完整 prompt

    Args:
        text: 用户输入的原始文本
        mode: 总结模式，normal(普通) 或 brief(简短)
        max_chars: 最大输入字符数，超过则截断

    Returns:
        格式化后的完整 prompt
    """
    # 截断策略
    if len(text) > max_chars:
        text = text[:max_chars]

    # 根据模式选择模板
    if mode == "brief":
        template = BRIEF_PROMPT_TEMPLATE
    else:
        template = NORMAL_PROMPT_TEMPLATE

    return template.format(user_text=text)
