from fastapi import APIRouter, HTTPException
from app.core.openai_client import generate_openai_response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json

router = APIRouter()


class userContent(BaseModel):
    user_content: str  # 用户的问题内容


@router.post("/restore_fake_news")
async def restore_fake_news(user_input: userContent):
    user_content = user_input.user_content

    system_content = f"""
        你是一位虚假新闻还原专家，你能够根据用户的原文以及对应要求，完成对于虚假新闻的分析以及还原。请你只返回以下 JSON 数据，不要加多余的话：

        {{
            "fake_news_type": [<虚假新闻的类型>],
            "original_fake_news": {{
                "title": "<虚假新闻标题>",
                "content": "<虚假新闻内容>"
            }},
            "restored_news": {{
                "title": "<还原后的标题>",
                "content": "<还原后的内容>"
            }},
            "restoration_basis": {{
                "source_correction": "<还原依据>",
                "evidence": "<支持证据>"
            }},
            "fake_news_probability_score": <虚假新闻的可能性分数>
        }}
    """

    response = await generate_openai_response(system_content, user_content, stream=False)

    return response.choices[0].message.content
