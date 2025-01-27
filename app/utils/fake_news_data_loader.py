import json
from fastapi import HTTPException

fake_news_data_cache = None

def load_fake_news_schema():
    global fake_news_data_cache
    if fake_news_data_cache is None:
        try:
            with open('fake_news.json', 'r', encoding='utf-8') as f:
                fake_news_data_cache = json.load(f)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error loading JSON file: {e}")
    return fake_news_data_cache