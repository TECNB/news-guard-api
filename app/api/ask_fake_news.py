from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from app.utils.fake_news_data_loader import load_fake_news_schema
from app.core.openai_client import generate_openai_response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import os
import httpx
import asyncio
from typing import Dict, Any, Optional

# 加载 .env 文件中的 RAGFLOW_API_KEY
load_dotenv()
RAGFLOW_API_KEY = os.getenv('RAGFLOW_API_KEY')

router = APIRouter()

class userContent(BaseModel):
    user_content: str  # 用户的问题内容

@router.post("/ask_fake_news")
async def ask_fake_news(user_input: userContent):
    user_content = user_input.user_content
    fake_news_data = load_fake_news_schema()

    # 构造请求体
    body = {
        "question": user_content,
        "stream": False,
        "session_id": "1f9c8eac44c34b2c98dcfda139aea23f"
    }

    # 设置请求头，包含 Authorization header
    headers = {
        "Authorization": f"Bearer {RAGFLOW_API_KEY}",
        "Content-Type": "application/json"
    }

    # 设置较长的超时时间
    timeout_settings = httpx.Timeout(30.0, connect=10.0)
    
    try:
        async with httpx.AsyncClient(timeout=timeout_settings) as client:
            # 发送 POST 请求
            response = await client.post(
                "http://127.0.0.1/api/v1/chats/22c63b20f31811ef85c10242ac120006/completions",
                json=body,
                headers=headers,
            )
            
            # 确保请求成功
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            
            # 检查响应格式并提取答案
            if result.get("code") == 0 and "data" in result and "answer" in result["data"]:
                answer = result["data"]["answer"]
                return {"answer": answer, "references": result["data"].get("reference", {})}
            else:
                raise HTTPException(status_code=500, detail="无法获取有效响应")
    
    except httpx.ReadTimeout:
        # 当发生超时但请求可能已经发出时，我们尝试轮询获取结果
        return await poll_for_results(user_content)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"API请求失败: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发生错误: {str(e)}")

async def poll_for_results(question: str, max_attempts: int = 5) -> Dict[str, Any]:
    """
    当原始请求超时时，轮询尝试获取结果
    """
    headers = {
        "Authorization": f"Bearer {RAGFLOW_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 等待一小段时间后开始轮询
    await asyncio.sleep(2)
    
    for attempt in range(max_attempts):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 获取会话中的最后一条回复
                response = await client.get(
                    f"http://127.0.0.1/api/v1/chats/22c63b20f31811ef85c10242ac120006/sessions/1f9c8eac44c34b2c98dcfda139aea23f/messages",
                    headers=headers,
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # 查找与当前问题关联的最新回复
                    # 注意：这里的逻辑可能需要根据实际API响应格式调整
                    if "data" in data and "messages" in data["data"]:
                        messages = data["data"]["messages"]
                        # 获取最新的回复消息
                        for msg in reversed(messages):
                            if msg.get("role") == "assistant":
                                return {
                                    "answer": msg.get("content", "未找到回复内容"),
                                    "references": msg.get("reference", {})
                                }
            
            # 如果没有找到结果，等待后再次尝试
            await asyncio.sleep(2 * (attempt + 1))
        
        except Exception as e:
            # 记录错误但继续尝试
            print(f"轮询尝试 {attempt+1} 失败: {str(e)}")
            await asyncio.sleep(2)
    
    # 如果多次尝试后仍未成功，返回错误信息
    raise HTTPException(status_code=504, detail="请求超时且无法获取结果，请稍后再试")

@router.get("/get_session")
async def get_session():
    # 设置请求头，包含 Authorization header
    headers = {
        "Authorization": f"Bearer {RAGFLOW_API_KEY}"
    }

    async with httpx.AsyncClient() as client:
        # 发送 POST 请求
        response = await client.get(
            "http://127.0.0.1/api/v1/chats/22c63b20f31811ef85c10242ac120006/sessions",
            headers=headers,
        )

        # 确保请求成功
        response.raise_for_status()

        return response.json()
