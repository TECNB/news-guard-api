from openai import OpenAI
from fastapi import HTTPException
from dotenv import load_dotenv
import os
# 加载环境变量
load_dotenv()

# 获取 API 密钥和基础 URL
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
client = OpenAI(api_key=api_key, base_url=base_url)

# 打印 OpenAI API 的基础 URL
async def generate_openai_response(system_content: str, user_content: str, stream: bool):
    try:
        response = client.chat.completions.create(
            # model="deepseek-ai/DeepSeek-V3",
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content},
            ],
            stream=stream
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling OpenAI API: {e}")