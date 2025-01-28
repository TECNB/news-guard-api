import json
from fastapi import HTTPException

hot_news_data_cache = None

def load_hot_news_schema():
    global hot_news_data_cache
    if hot_news_data_cache is None:
        try:
            with open('hot_news.json', 'r', encoding='utf-8') as f:
                hot_news_data_cache = json.load(f)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error loading JSON file: {e}")
    return hot_news_data_cache