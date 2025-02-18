from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from pathlib import Path
import shutil
import whisper

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

# 使用Whisper进行音频转文字
@router.post("/audio_to_text/")
async def audio_to_text(file: UploadFile = File(...)):
    try:
        # 保存音频文件到本地
        audio_location = UPLOAD_DIR / file.filename
        with open(audio_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 加载Whisper模型
        model = whisper.load_model("tiny")  # 可以选择不同大小的模型（tiny,base, small, medium, large）

        # 使用Whisper对音频进行转录
        result = model.transcribe(str(audio_location), language="zh")  # 设置为中文语言模型

        # 返回转录的文本
        return JSONResponse(content={"text": result['text']}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
