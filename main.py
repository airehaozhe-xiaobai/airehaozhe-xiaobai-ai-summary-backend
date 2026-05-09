"""
AI 文本总结工具 - FastAPI 后端
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# 加载 backend/.env 环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from router import summary

app = FastAPI(title="AI 文本总结工具", version="1.0.0")

# CORS 配置，允许前端直接访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://airehaozhe-xiaobai.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(summary.router, prefix="/api", tags=["总结"])


@app.get("/")
async def root():
    return {"message": "AI 文本总结工具 API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}
