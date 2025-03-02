from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from pathlib import Path
import shutil
import whisper
from funasr.utils.postprocess_utils import rich_transcription_postprocess
from pydantic import BaseModel
import torch
from funasr import AutoModel
import re
from typing import List, Dict

from app.core.openai_client import generate_openai_response

class userContent(BaseModel):
    user_content: str  # 用户的问题内容


router = APIRouter()

# 设置文件存储路径
UPLOAD_DIR = Path("/Users/tec/Desktop")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # 保存上传的文件到本地
        file_location = UPLOAD_DIR / file.filename
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 返回文件 URL
        file_url = f"/uploads/{file.filename}"
        return JSONResponse(content={"data": file_url}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# 处理文件静态访问
@router.get("/uploads/{file_name}")
async def get_file(file_name: str):
    file_location = UPLOAD_DIR / file_name
    if file_location.exists():
        return FileResponse(file_location)
    else:
        return JSONResponse(content={"error": "File not found"}, status_code=404)


def load_sensevoice_model():
    try:
        model = AutoModel(
            model="iic/SenseVoiceSmall",
            trust_remote_code=True,
            vad_model="fsmn-vad",
            vad_kwargs={"max_single_segment_time": 30000},
            device="cuda:0" if torch.cuda.is_available() else "cpu",
        )
        return model
    except Exception as e:
        raise RuntimeError(f"模型加载失败: {str(e)}")

sensevoice_model = load_sensevoice_model()

@router.post("/audio_to_text/")
async def audio_to_text(file: UploadFile = File(...)):
    try:
        # 保存音频文件
        audio_location = UPLOAD_DIR / file.filename
        with open(audio_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 调用SenseVoice进行多模态分析
        result = sensevoice_model.generate(
            input=str(audio_location),
            cache={},
            language="auto",
            use_itn=True,
            batch_size_s=60,
            merge_vad=True,
            enable_emotion=True,
            return_all_scores=True  # 关键参数：返回所有情绪类型的置信度分布
        )
        print(result)

        # 解析SenseVoice返回的特殊标记格式
        def parse_sensevoice_output(text: str) -> Dict:
            # 使用正则表达式匹配所有标记段
            pattern = r'<\|([^|]+)\|>'
            segments = re.split(pattern, text)

            # 初始化变量
            current_lang = "unknown"
            current_emotion = "neutral"
            parsed_segments = []
            clean_text = []

            for item in segments:
                if not item.strip():
                    continue

                # 识别标记类型
                if item in ["zh", "en", "fr"]:  # 支持的语言列表
                    current_lang = item
                elif item in ["HAPPY", "NEUTRAL", "ANGER", "SAD"]:  # 情感类型
                    current_emotion = item.lower()
                elif item in ["Speech", "withitn"]:
                    continue  # 忽略无关标记
                else:
                    # 记录有效段落
                    parsed_segments.append({
                        "lang": current_lang,
                        "emotion": current_emotion,
                        "text": item.strip()
                    })
                    clean_text.append(item.strip())

            return {
                "segments": parsed_segments,
                "full_text": " ".join(clean_text),
                "main_lang": max(set([s["lang"] for s in parsed_segments]), default="unknown"),
                "main_emotion": max(set([s["emotion"] for s in parsed_segments]), default="neutral")
            }

        # 处理分析结果
        parsed_result = parse_sensevoice_output(result[0]["text"])

        processed_data = {
            "text": parsed_result["full_text"],
            "language": parsed_result["main_lang"],
            "emotion": parsed_result["main_emotion"],
            "details": {
                "segments": parsed_result["segments"],
                "audio_events": result[0].get("events", []),
                "timestamps": result[0].get("timestamp", [])
            }
        }

        # 删除临时文件（可选）
        # audio_location.unlink()

        return JSONResponse(content=processed_data, status_code=200)

    except Exception as e:
        return JSONResponse(
            content={"error": f"处理失败: {str(e)}"},
            status_code=500
        )
# 使用OpenAI对音频进行虚假新闻验证
@router.post("/verify_audio/")
async def verify_audio(user_input: userContent):
    user_content = user_input.user_content

    system_content = f"""
        你是一位虚假新闻鉴别专家，你能够根据用户的原文以及对应要求，完成对于虚假新闻的分析。请你只返回以下 JSON 数据，不要加多余的话：

        {{
            "authenticity": <新闻的真实性百分比，范围是 0 到 100>，
            "ai_probability": <AI对新闻真实性的概率百分比，范围是 0 到 100>，
            "safety_level": <AI对新闻真实性的概率百分比，范围是 0 到 100>,
            "summary": <对于新闻虚假程度的整体简要总结，大概6到8个字，例："真实性较高" 或 "信息偏虚假" 或 "可信度较低">
        }}
    """

    response = await generate_openai_response(system_content, user_content, stream=False)

    return response.choices[0].message.content
