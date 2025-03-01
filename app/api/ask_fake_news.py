from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from app.utils.fake_news_data_loader import load_fake_news_schema
from app.core.openai_client import generate_openai_response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import os
import httpx

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

    system_content = f"""
        你能够根据用户的提问，查找相关的内容并以结构化的方式进行回答。你的依据是以下JSON：
        {json.dumps(fake_news_data, ensure_ascii=False)}
    """

    response = await generate_openai_response(system_content, user_content, stream=True)

    async def response_generator():
        for chunk in response:
            chunk_message = chunk.choices[0].delta.content
            yield chunk_message

    return StreamingResponse(response_generator(), media_type="text/plain")

@router.get("/get_session")
async def get_session():
    # # 构造请求体
    # body = {
    #     "question": user_content,
    #     "stream": True,
    #     "session_id": "1f9c8eac44c34b2c98dcfda139aea23f"
    # }

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
