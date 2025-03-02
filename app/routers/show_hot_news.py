from fastapi import APIRouter, Query
from app.utils.hot_news_data_loader import load_hot_news_schema

router = APIRouter()

@router.get("/show_hot_news")
async def show_hot_news(page: int = Query(1, alias="page", ge=1), size: int = Query(10, alias="size", ge=1)):
    fake_news_data = load_hot_news_schema()

    start = (page - 1) * size
    end = start + size
    paginated_data = fake_news_data[start:end]

    return {
        "page": page,
        "size": size,
        "total": len(fake_news_data),
        "records": paginated_data
    }