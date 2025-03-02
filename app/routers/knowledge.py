from dotenv import load_dotenv
from fastapi import APIRouter, File, UploadFile
from fastapi import APIRouter, HTTPException
from fastapi import Form
from pydantic import BaseModel
import os
import httpx
from app.schemas.knowledge import parseDocumentsRequest, CreateKnowledgeRequest ,DeleteKnowledgeRequest

# 加载 .env 文件中的 RAGFLOW_API_KEY
load_dotenv()
RAGFLOW_API_KEY = os.getenv('RAGFLOW_API_KEY')

router = APIRouter()

@router.get("/get_knowledge")
async def get_knowledge():
    # 设置请求头，包含 Authorization header
    headers = {
        "Authorization": f"Bearer {RAGFLOW_API_KEY}"
    }

    async with httpx.AsyncClient() as client:
        # 发送 Get 请求
        response = await client.get(
            "http://localhost:80/api/v1/datasets",
            headers=headers,
        )

        # 确保请求成功
        response.raise_for_status()

        return response.json()

@router.post("/create_knowledge")
async def create_knowledge(request: CreateKnowledgeRequest):
    datasetsName = request.datasetsName

    # 设置请求头，包含 Authorization header
    headers = {
        "Authorization": f"Bearer {RAGFLOW_API_KEY}"
    }

    json = {
        "name": datasetsName
    }

    async with httpx.AsyncClient() as client:
        # 发送 POST 请求
        response = await client.post(
            "http://127.0.0.1/api/v1/datasets",
            headers=headers,
            json=json
        )

        # 确保请求成功
        response.raise_for_status()

        return response.json()

@router.delete("/delete_knowledge")
async def delete_knowledge(request: DeleteKnowledgeRequest):
    datasetsId = request.datasetsId

    # 设置请求头，包含 Authorization header
    headers = {
        "Authorization": f"Bearer {RAGFLOW_API_KEY}"
    }

    json = {
        "ids": [
            datasetsId
        ]
    }

    async with httpx.AsyncClient() as client:
        # 发送 Delete 请求
        response = await client.request(
            "DELETE",
            f"http://localhost:80/api/v1/datasets",
            headers=headers,
            json=json
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
async def update_documents(request: parseDocumentsRequest):
    datasetsId = request.datasetsId
    documentId = request.documentId
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
async def delete_documents(request: parseDocumentsRequest):
    datasetsId = request.datasetsId
    documentId = request.documentId

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
        # 发送 Delete 请求
        response = await client.request(
            "DELETE",
            f"http://localhost:80/api/v1/datasets/{datasetsId}/documents",
            headers=headers,
            json=json
        )

        # 确保请求成功
        response.raise_for_status()

        return response.json()
