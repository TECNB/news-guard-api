from fastapi import APIRouter, HTTPException
from app.utils.fake_news_data_loader import load_fake_news_schema
from app.core.openai_client import generate_openai_response
from pydantic import BaseModel
import json

router = APIRouter()

class UserInput(BaseModel):
    user_content: str  # 用户的问题内容
    chart_type: str  # 图表类型

@router.post("/generate_chart")
async def generate_chart(user_input: UserInput):
    user_content = user_input.user_content
    chart_type = user_input.chart_type
    fake_news_data = load_fake_news_schema()

    if chart_type == "bar":
        system_content = f"""
        分析虚假新闻内容的关键词，根据用户要求生成对应类型的图表，我需要使用ecahrts，请你只返回你认为最好的 y 轴标签以及xAxisData、seriesData组成JSON给我，不要加多余的话：
        {json.dumps(fake_news_data, ensure_ascii=False)}
        """
    elif chart_type == "pie":
        system_content = f"""
        分析虚假新闻内容的关键词，根据用户要求生成对应类型的图表，我需要使用ecahrts，请你只返回你认为最好的seriesName以及seriesData内的value,name组成JSON给我，不要加多余的话：
        {json.dumps(fake_news_data, ensure_ascii=False)}
        """
    elif chart_type == "line":
        system_content = f"""
        分析虚假新闻内容的关键词，根据用户要求生成对应类型的图表，我需要使用ecahrts，请你只返回你认为最好的 y 轴标签以及xAxisData、seriesData组成JSON给我，不要加多余的话：
        {json.dumps(fake_news_data, ensure_ascii=False)}
        """

    response = await generate_openai_response(system_content, user_content, stream=False)
    return response.choices[0].message.content