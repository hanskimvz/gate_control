from fastapi import APIRouter, status
from database import get_database

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """헬스 체크 엔드포인트"""
    db = get_database()
    try:
        # MongoDB 연결 확인
        await db.command('ping')
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

