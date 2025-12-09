from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from config import config_data
from utils.logger import get_logger

logger = get_logger()

# MongoDB 클라이언트
client: Optional[AsyncIOMotorClient] = None
database = None


async def connect_to_mongo():
    """MongoDB에 연결"""
    global client, database
    try:
        mongodb_config = config_data.get('MONGODB', {})
        host = mongodb_config.get('host', 'localhost')
        port = mongodb_config.get('port', 27017)
        user = mongodb_config.get('user', '')
        password = mongodb_config.get('password', '')
        db_name = mongodb_config.get('db', 'gate_control')
        
        # MongoDB URL 구성
        if user and password:
            mongodb_url = f"mongodb://{user}:{password}@{host}:{port}"
        else:
            mongodb_url = f"mongodb://{host}:{port}"
        
        pool_config = mongodb_config.get('pool', {})
        client = AsyncIOMotorClient(
            mongodb_url,
            maxPoolSize=pool_config.get('max_pool_size', 50),
            minPoolSize=pool_config.get('min_pool_size', 5),
            maxIdleTimeMS=pool_config.get('max_idle_time_ms', 30000)
        )
        database = client[db_name]
        # 연결 테스트
        await client.admin.command('ping')
        logger.info(f"MongoDB에 연결되었습니다: {db_name}")
    except Exception as e:
        logger.error(f"MongoDB 연결 실패: {e}", exc_info=True)
        raise


async def close_mongo_connection():
    """MongoDB 연결 종료"""
    global client
    if client:
        client.close()
        logger.info("MongoDB 연결이 종료되었습니다.")


def get_database():
    """데이터베이스 인스턴스 반환"""
    return database

