"""
사용자 관련 API 라우터
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from bson import ObjectId
from datetime import datetime

from database import get_database
from config import config_data
from services.user_service import (
    get_user_by_api_key,
    get_all_users,
    generate_api_key
)


router = APIRouter()
@router.post("/users")
async def users_handler(body: dict):
    """사용자 관련 API 핸들러 (action 기반)"""
    action = body.get("action")
    api_key = body.get("api_key")
    data = body.get("data", {})
    
    # API 키 검증
    await _validate_api_key(api_key)
    
    # action에 따라 적절한 함수 호출
    if action == "list":
        result = await list_users()
        return result
    
    elif action == "create":
        result = await create_user(data)
        return result
    
    elif action == "modify":
        result = await modify_user(data)
        return result
    
    elif action == "remove":
        result = await remove_user(data)
        return result
    
    else:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid action: {action}. Supported actions: 'list', 'create', 'modify', 'remove'"
        )


async def _validate_api_key(api_key: str):
    """API 키 검증 헬퍼 함수"""
    if not api_key:
        raise HTTPException(status_code=401, detail="API key is required")
    
    user = await get_user_by_api_key(api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return user


def _convert_flag(flag_value) -> str:
    """flag 값을 "y"/"n" 문자열로 변환"""
    if isinstance(flag_value, bool):
        return "y" if flag_value else "n"
    else:
        return str(flag_value) if flag_value else "y"


async def list_users() -> list:
    """사용자 목록 조회"""
    users = await get_all_users()
    return [{
        "_id": str(user.get("_id")),
        "user_id": user.get("user_id"),  # MongoDB의 "user_id" 필드
        "regdate": user.get("regdate"),
        "api_key": user.get("api_key"),
        "date_from": user.get("date_from", "0000-00-00"),
        "hour_from": user.get("hour_from", 0),
        "date_to": user.get("date_to", "0000-00-00"),
        "hour_to": user.get("hour_to", 0),
        "flag": user.get("flag", "y"),
        "name": user.get("name"),
        "plates": user.get("plates") or user.get("plate") or []
    } for user in users]


async def create_user(data: dict) -> dict:
    """새 사용자 생성"""
    user_id = data.get("user_id", "").strip()
    
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    # flag 처리 (boolean -> "y"/"n")
    flag = _convert_flag(data.get("flag"))
    
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    collection_name = config_data.get('MONGODB', {}).get('tables', {}).get('user', 'user')
    collection = db[collection_name]
    
    try:
        # 중복 사용자 확인
        existing_user = await collection.find_one({"user_id": user_id})
        if existing_user:
            raise HTTPException(status_code=400, detail=f"User with user_id '{user_id}' already exists")
        
        # API 키 생성
        api_key = generate_api_key(user_id)
        
        # 등록일 생성
        regdate_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 새 사용자 문서 생성
        user_doc = {
            "user_id": user_id,
            "api_key": api_key,
            "date_from": data.get("date_from", "0000-00-00"),
            "hour_from": data.get("hour_from", 0),
            "date_to": data.get("date_to", "0000-00-00"),
            "hour_to": data.get("hour_to", 0),
            "flag": flag,
            "regdate": regdate_str,
            "plates": data.get("plates", []),
            "name": data.get("name")
        }
        
        # MongoDB에 삽입
        result = await collection.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        
        # plate 필드도 추가 (일부 데이터와의 호환성)
        if "plates" in user_doc:
            user_doc["plate"] = user_doc.get("plates", [])
        
        return {"message": "OK", "data": {"_id": str(user_doc["_id"])}}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Create error: {str(e)}")


async def modify_user(data: dict) -> dict:
    """사용자 수정"""
    user_id = data.get("user_id", "").strip()
    _id = data.get("_id")
    
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    if not _id:
        raise HTTPException(status_code=400, detail="_id is required")
    
    # flag 처리 (boolean -> "y"/"n")
    flag = _convert_flag(data.get("flag"))
    
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    collection_name = config_data.get('MONGODB', {}).get('tables', {}).get('user', 'user')
    collection = db[collection_name]
    
    try:
        # _id로 기존 사용자 찾기
        existing_user_doc = await collection.find_one({"_id": ObjectId(_id)})
        if not existing_user_doc:
            raise HTTPException(status_code=404, detail="User not found")
        
        # MongoDB에는 "user_id" 필드로 저장되어 있음
        existing_user_id = existing_user_doc.get("user_id")
        
        # 업데이트 데이터 준비
        update_data = {}
        if user_id != existing_user_id:
            update_data["user_id"] = user_id
            # user_id가 변경되면 api_key도 재생성
            update_data["api_key"] = generate_api_key(user_id)
        
        if "date_from" in data:
            update_data["date_from"] = data.get("date_from")
        if "hour_from" in data:
            update_data["hour_from"] = data.get("hour_from")
        if "date_to" in data:
            update_data["date_to"] = data.get("date_to")
        if "hour_to" in data:
            update_data["hour_to"] = data.get("hour_to")
        if "flag" in data:
            update_data["flag"] = flag
        if "name" in data:
            update_data["name"] = data.get("name")
        if "plates" in data:
            update_data["plates"] = data.get("plates", [])
        
        if not update_data:
            return {"message": "OK", "data": existing_user_doc}
        
        # 사용자 업데이트
        result = await collection.find_one_and_update(
            {"_id": ObjectId(_id)},
            {"$set": update_data},
            return_document=True
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Update failed")
        
        return {"message": "OK"}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid user ID format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update error: {str(e)}")


async def remove_user(data: dict) -> dict:
    """사용자 삭제"""
    _id = data.get("_id")
    
    if not _id:
        raise HTTPException(status_code=400, detail="_id is required")
    
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    collection_name = config_data.get('MONGODB', {}).get('tables', {}).get('user', 'user')
    collection = db[collection_name]
    
    try:
        # _id로 기존 사용자 찾기
        existing_user_doc = await collection.find_one({"_id": ObjectId(_id)})
        if not existing_user_doc:
            raise HTTPException(status_code=404, detail="User not found")
        
        # 사용자 삭제
        result = await collection.delete_one({"_id": ObjectId(_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=500, detail="Delete failed")
        
        return {"message": "OK"}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid user ID format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete error: {str(e)}")



