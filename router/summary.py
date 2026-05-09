"""
文本总结 API 路由
"""
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from typing import Optional
from pydantic import BaseModel, Field

from service.llm import call_minimax, parse_summary_response
from prompt.summary_prompt import build_prompt


router = APIRouter()


class SummaryRequest(BaseModel):
    """总结请求参数"""
    text: str = Field(..., min_length=1, description="待总结的文本内容")
    mode: str = Field(default="normal", description="总结模式：normal(普通) / brief(简短)")


class SummaryResponse(BaseModel):
    """总结响应"""
    success: bool
    summary: str
    keywords: list[str]
    word_count: int


class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = False
    error: str


@router.post("/summary", response_model=SummaryResponse)
async def summarize(request: SummaryRequest):
    """
    文本总结接口

    接收文本，返回 AI 生成的总结和关键词
    """
    # 1. 参数校验
    if not request.text or not request.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文本内容不能为空"
        )

    text = request.text.strip()

    # 2. 简单截断（防止超长）
    MAX_TEXT_LENGTH = 6000
    original_length = len(text)
    if original_length > MAX_TEXT_LENGTH:
        text = text[:MAX_TEXT_LENGTH]

    # 3. 构建 Prompt
    prompt = build_prompt(text, mode=request.mode)

    # 4. 调用 AI
    try:
        raw_response = await call_minimax(prompt)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 服务配置错误: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 服务调用失败: {str(e)}"
        )

    # 5. 解析结果
    parsed = parse_summary_response(raw_response)

    # 6. 返回
    return SummaryResponse(
        success=True,
        summary=parsed["summary"],
        keywords=parsed["keywords"],
        word_count=original_length
    )


@router.post("/summary/upload")
async def summarize_upload(file: UploadFile = File(...), mode: Optional[str] = Form(default="normal")):
    """
    文件上传总结接口

    支持 .txt 文件，文件内容作为总结文本
    """
    # 校验文件类型
    if not file.filename.endswith(".txt"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="仅支持 .txt 文件"
        )

    # 读取文件内容
    try:
        content = await file.read()
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件编码不支持，请使用 UTF-8 编码的 .txt 文件"
        )

    if not text or not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件内容为空"
        )

    # 截断
    MAX_TEXT_LENGTH = 6000
    original_length = len(text)
    if original_length > MAX_TEXT_LENGTH:
        text = text[:MAX_TEXT_LENGTH]

    # 构建 Prompt
    prompt = build_prompt(text, mode=mode)

    # 调用 AI
    try:
        raw_response = await call_minimax(prompt)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 服务配置错误: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 服务调用失败: {str(e)}"
        )

    # 解析结果
    parsed = parse_summary_response(raw_response)

    return SummaryResponse(
        success=True,
        summary=parsed["summary"],
        keywords=parsed["keywords"],
        word_count=original_length
    )
