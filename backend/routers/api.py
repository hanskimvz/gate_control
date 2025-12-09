from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import HTMLResponse
from typing import Optional
from datetime import datetime
from models import LoginRequest
from services.user_service import authenticate_user
from services.log_service import get_logs, get_log_count


router = APIRouter()




@router.get("/logs")
async def list_log(
    page: int = Query(1, ge=1),
    offset: int = Query(20, ge=1, le=100),
    api_key: Optional[str] = Query(None)
):
    """로그 목록 조회"""
    logs = await get_logs(page=page, offset=offset)
    total = await get_log_count()
    
    return {
        "logs": [{
            "regdate": log.get("regdate").isoformat() if isinstance(log.get("regdate"), datetime) else log.get("regdate"),
            "user_id": log.get("user_id"),
            "user_name": log.get("user_name"),
            "eventinfo": log.get("eventinfo", {}),
            "snapshot": log.get("snapshot"),
            "user_agent": log.get("user_agent"),
            "cam_no": log.get("cam_no", 0)
        } for log in logs],
        "page": page,
        "offset": offset,
        "total": total
    }


@router.post("/login")
async def login(body: LoginRequest):
    """사용자 ID와 password로 로그인하여 API 키 반환"""
    api_key = await authenticate_user(body.user_id, body.password)
    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid user_id or password")
    
    return {
        "api_key": api_key,
        "user_id": body.user_id
    }



