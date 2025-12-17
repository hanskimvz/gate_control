"""
Gate 관련 API 라우터
"""
from fastapi import APIRouter, HTTPException, Request, Query
from typing import Optional
import base64
from urllib.parse import unquote, parse_qs
from models import OpenDoorRequest, SnapshotRequest
from services.user_service import (
    get_user_by_api_key,
    valid_datetime
)
from services.camera_service import get_snapshot, put_do
from services.log_service import update_log
from config import config_data


router = APIRouter()


@router.post("/gate")
async def gate_handler(request: Request, body: dict):
    """Gate 관련 API 핸들러 (action 기반)"""
    action = body.get("action")
    api_key = body.get("api_key")
    data = body.get("data", {})
    
    # API 키 검증
    user = await _validate_api_key(api_key)
    
    # action에 따라 적절한 함수 호출
    if action == "ready":
        user = await get_user_by_api_key(api_key)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid API key")

        user_valid = True
        if user.get("flag") != "y":
            user_valid = False

        if not valid_datetime(
                user.get("date_from", "0000-00-00"), 
                user.get("date_to", "0000-00-00"), 
                user.get("hour_from", 0), 
                user.get("hour_to", 0)
            ):
            user_valid = False

        print ("user_valid", user_valid)
        return {
            "user_id": user.get("user_id"),
            "user_name": user.get("name"),
            "valid": user_valid,
            "camera_list": [name for name in config_data.get("CAMERAS", {}).keys()]
        }        

    elif action == "open":
        ret = await open_action(api_key, user)

        if ret: 
            snapshot = await get_snapshot(cam_name="main")
            # 서버에서 가져온 정보
            client_ip = request.client.host if request and request.client else "unknown"
            server_user_agent = request.headers.get("user-agent", "unknown") if request else "unknown"
            
            # 클라이언트에서 보낸 request 정보 (있는 경우 사용)
            client_info = data.get("request_info", {})
            client_user_agent = client_info.get("user_agent") or server_user_agent
            
            eventinfo = {
                "ip": client_ip,
                "mode": "open",
                "api_key": api_key,
                "client_info": {
                    "language": client_info.get("language"),
                    "platform": client_info.get("platform"),
                    "screen": f"{client_info.get('screen_width')}x{client_info.get('screen_height')}",
                    "timezone": client_info.get("timezone"),
                    "timestamp": client_info.get("timestamp")
                }
            }
            print(eventinfo)        

            await update_log(user_id=user.get("user_id"), eventinfo=eventinfo, snapshot=snapshot, user_agent=client_user_agent)
            return {"message": "opened OK"}

        return {"message": "Fail to open"}

        
    
    elif action == "snapshot":
        cam_name = data.get("cam_name", "main")
        return await get_snapshot(cam_name=cam_name)
    

    
    elif action == "exit":
        return await exit_action(request, api_key, user)
    
    else:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid action: {action}. Supported actions: 'ready', 'open', 'snapshot', 'exit'"
        )


@router.get("/gate")
# http://192.168.1.252:22450/api/v1/gate?mode=exit&api_key=fb16fea114c5788ab752f0dbca224c5c
async def exit(
    api_key: str = Query(..., description="API 키"),
    mode: Optional[str] = Query("exit", description="모드 (기본값: exit)")
):
    """외부 카메라에서 문 열기 (기존 호환성 유지)"""
    print(api_key, mode)
    user = await get_user_by_api_key(api_key)
    if not user:
        raise HTTPException(status_code=401, detail="check api_key")
    
    user_id = user.get("user_id") if user else None
    if not user or user_id != "vivasejin":
        raise HTTPException(status_code=401, detail="check api_key")

    ret = await open_action(api_key, user)
    # ret = True
    if ret:
        snapshot = await get_snapshot(cam_name="sub1")
        eventinfo = {
            "ip": "external",
            "mode": mode or "exit",
            "api_key": api_key
        }
        await update_log(user_id=user_id, eventinfo=eventinfo, snapshot=snapshot, user_agent="external_camera")
        return {"message": "opened"}
    
    else:
        raise HTTPException(status_code=500, detail="Failed to open")
    

async def _validate_api_key(api_key: str):
    """API 키 검증 헬퍼 함수"""
    if not api_key:
        raise HTTPException(status_code=401, detail="API key is required")
    
    user = await get_user_by_api_key(api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return user


async def open_action(api_key: str, user: dict):
    print ("open_action: ", user, api_key)
    """문 열기"""
    if user.get("flag") != "y":
        raise HTTPException(status_code=403, detail="Not valid auth, contact admin")
    
    if not valid_datetime(user.get("date_from", "0000-00-00"), user.get("date_to", "0000-00-00"), 
                          user.get("hour_from", 0), user.get("hour_to", 0)):
        raise HTTPException(status_code=403, detail="Not valid datetime, contact admin")
    
    # 문 열기 (1초)
    ret = await put_do(cam_name="main", secs=1)
    if ret:
        return True
    
    return False


async def exit_action(request: Optional[Request], api_key: str, user: dict):
    """외부 카메라에서 문 열기"""
    user_id = user.get("user_id") if user else None
    if not user or user_id != "vivasejin":
        raise HTTPException(status_code=401, detail="check api_key")
    
    ret = await put_do(cam_name="main", secs=1)
    if ret:
        # 로그 기록
        snapshot = await get_snapshot(cam_name="sub1")
        eventinfo = {
            "ip": "external",
            "mode": "exit",
            "api_key": api_key
        }
        await update_log(
            user_id=user_id,
            eventinfo=eventinfo,
            user_agent="external_camera",
            snapshot=snapshot,
        )
        return {"message": "opened"}
    else:
        raise HTTPException(status_code=500, detail="Failed to open")

@router.post("/snapshot")
async def store_snapshot(request: Request):
    """스냅샷 저장 API (POST 방식으로 eventinfo와 snapshot 파일 받기)"""
    # Query string 파싱
    query_str = unquote(str(request.url.query))
    query_params = parse_qs(query_str)
    
    # Query string에서 eventinfo 딕셔너리 생성
    eventinfo = {
        "mode": "snapshot"
    }
    for key, value_list in query_params.items():
        # parse_qs는 리스트를 반환하므로 첫 번째 값 사용
        eventinfo[key] = value_list[0] if value_list else ""

    # Snapshot 파일 처리
    snapshot_data = ""
    try:
        form = await request.form()
        snapshot_file = form.get("snapshot")
        if snapshot_file:
            # 파일 읽기
            file_content = await snapshot_file.read()
            # Base64 인코딩 및 data URI 형식으로 변환
            snapshot_base64 = base64.b64encode(file_content).decode('utf-8')
            snapshot_data = f"data:image/jpg;base64,{snapshot_base64}"
    except Exception as e:
        # Form data가 없거나 파일이 없는 경우 정상적으로 처리
        print(f"Form data 처리 오류 (무시 가능): {e}")
    
    # 로그 업데이트
    await update_log(user_id="snapshot", eventinfo=eventinfo, snapshot=snapshot_data, user_agent='snapshot')
    return {"message": "snapshot stored OK"}

