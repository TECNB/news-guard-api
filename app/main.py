from fastapi import FastAPI
from app.api.ask_fake_news import router as ask_fake_news_router
from app.api.generate_chart import router as generate_chart_router
from app.api.show_fake_news import router as show_fake_news
from app.api.show_hot_news import router as show_hot_news
from app.api.restore_fake_news import router as restore_fake_news

app = FastAPI()

# 注册路由
app.include_router(ask_fake_news_router)
app.include_router(generate_chart_router)
app.include_router(show_fake_news)
app.include_router(show_hot_news)
app.include_router(restore_fake_news)