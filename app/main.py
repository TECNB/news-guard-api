from fastapi import FastAPI
from app.api.ask_fake_news import router as ask_fake_news_router
from app.api.generate_chart import router as generate_chart_router

app = FastAPI()

# 注册路由
app.include_router(ask_fake_news_router)
app.include_router(generate_chart_router)