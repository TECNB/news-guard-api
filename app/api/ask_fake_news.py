from fastapi import APIRouter, HTTPException
from app.utils.fake_news_data_loader import load_fake_news_schema
from app.core.openai_client import generate_openai_response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json

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