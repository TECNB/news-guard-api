from dotenv import load_dotenv
from fastapi import APIRouter, File, UploadFile
from fastapi import APIRouter, HTTPException
from fastapi import Form
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

class parseDocumentsContent(BaseModel):
    datasetsId: str
    documentId: str

@router.get("/get_knowledge")
async def get_knowledge():
    # 设置请求头，包含 Authorization header
    headers = {
        "Authorization": f"Bearer {RAGFLOW_API_KEY}"
    }

    async with httpx.AsyncClient() as client:
        # 发送 POST 请求
        response = await client.get(
            "http://localhost:80/api/v1/datasets",
            headers=headers,
        )

        # 确保请求成功
        response.raise_for_status()

        return response.json()

@router.get("/get_documents")
async def get_documents(id: str):
    # 设置请求头，包含 Authorization header
    headers = {
        "Authorization": f"Bearer {RAGFLOW_API_KEY}"
    }

    async with httpx.AsyncClient() as client:
        # 发送 POST 请求
        response = await client.get(
            f"http://localhost:80/api/v1/datasets/{id}/documents",
            headers=headers,
        )

        # 确保请求成功
        response.raise_for_status()

        return response.json()

@router.post("/update_documents")
async def update_documents(id: str = Form(...), file: UploadFile = File(...)):
    # 设置请求头，包含 Authorization header
    headers = {
        "Authorization": f"Bearer {RAGFLOW_API_KEY}"
    }

    files = {
        "file": (file.filename, file.file, file.content_type)
    }

    async with httpx.AsyncClient() as client:
        # 发送 POST 请求
        response = await client.post(
            f"http://localhost:80/api/v1/datasets/{id}/documents",
            headers=headers,
            files=files
        )

        # 确保请求成功
        response.raise_for_status()

        return response.json()

@router.post("/parse_documents")
async def update_documents(parseDocumentsContent: parseDocumentsContent):
    datasetsId = parseDocumentsContent.datasetsId
    documentId = parseDocumentsContent.documentId
    # 设置请求头，包含 Authorization header
    headers = {
        "Authorization": f"Bearer {RAGFLOW_API_KEY}"
    }

    json = {
        "document_ids": [
            documentId
        ]
    }

    async with httpx.AsyncClient() as client:
        # 发送 POST 请求
        response = await client.post(
            f"http://localhost:80/api/v1/datasets/{datasetsId}/chunks",
            headers=headers,
            json=json
        )

        # 确保请求成功
        response.raise_for_status()

        return response.json()

@router.delete("/delete_documents")
async def delete_documents(parseDocumentsContent: parseDocumentsContent):
    datasetsId = parseDocumentsContent.datasetsId
    documentId = parseDocumentsContent.documentId

    print(datasetsId)
    print(documentId)
    # 设置请求头，包含 Authorization header
    headers = {
        "Authorization": f"Bearer {RAGFLOW_API_KEY}"
    }

    json = {
        "ids": [
            documentId
        ]
    }

    async with httpx.AsyncClient() as client:
        # 发送 POST 请求
        response = await client.request(
            "DELETE",
            f"http://localhost:80/api/v1/datasets/{datasetsId}/documents",
            headers=headers,
            json=json
        )

        # 确保请求成功
        response.raise_for_status()

        return response.json()
