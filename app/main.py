from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # 导入 CORSMiddleware
from app.routers.ask_fake_news import router as ask_fake_news_router
from app.routers.generate_chart import router as generate_chart_router
from app.routers.show_fake_news import router as show_fake_news
from app.routers.show_hot_news import router as show_hot_news
from app.routers.restore_fake_news import router as restore_fake_news
from app.routers.verify_audio import router as verify_audio
from app.routers.knowledge import router as knowledge

app = FastAPI()

# 设置 CORS 中间件，允许来自指定的前端地址的请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许的来源地址
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

# 注册路由
app.include_router(ask_fake_news_router)
app.include_router(generate_chart_router)
app.include_router(show_fake_news)
app.include_router(show_hot_news)
app.include_router(restore_fake_news)
app.include_router(verify_audio)
app.include_router(knowledge)