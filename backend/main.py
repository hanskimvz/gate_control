from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from database import connect_to_mongo, close_mongo_connection
from routers import health, api, users, gate
from config import config_data
from utils.logger import setup_logger, get_logger

# 로거 초기화
logger = setup_logger(
    name="gate",
    level=logging.INFO,
    log_file="logs/gate.log" if config_data.get("LOG", {}).get("file") else None
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 실행
    logger.info("애플리케이션 시작")
    await connect_to_mongo()
    yield
    # 종료 시 실행
    logger.info("애플리케이션 종료")
    await close_mongo_connection()


app = FastAPI(
    title="Gate API",
    description="FastAPI backend with MongoDB",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(health.router, tags=["Health"])
app.include_router(api.router, prefix="/api/v1", tags=["API"])
app.include_router(users.router, prefix="/api/v1", tags=["Users"])
app.include_router(gate.router, prefix="/api/v1", tags=["Gate"])


@app.get("/")
async def root():
    return {"message": "Welcome to Gate API"}


if __name__ == "__main__":
    import uvicorn
    # config.json에서 서버 설정 읽기
    api_server_config = config_data.get("API_SERVER", {})
    host = api_server_config.get("host", "0.0.0.0")
    port = api_server_config.get("port", 8000)
    # reload를 사용하려면 import string으로 전달해야 함
    uvicorn.run("main:app", host=host, port=port, reload=True)