from fastapi import APIRouter, HTTPException
from app.utils.fake_news_data_loader import load_fake_news_schema
from app.core.openai_client import generate_openai_response
from pydantic import BaseModel
import json

router = APIRouter()

class UserInput(BaseModel):
    user_content: str  # 用户的问题内容

@router.post("/parse_html")
async def parse_html(user_input: UserInput):
    user_content = user_input.user_content

    system_content = f"""
        分析该新闻内容的html，请你只返回你认为的title、content组成JSON给我，不要加多余的话
        """

    response = await generate_openai_response(system_content, user_content, stream=False)
    return response.choices[0].message.content