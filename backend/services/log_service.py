from typing import Optional, List, Dict, Any
import time
from datetime import datetime, timedelta, timezone
from database import get_database
from config import config_data
from bson import ObjectId


async def update_log(
    user_id: Optional[str],
    eventinfo: dict, 
    snapshot: str, 
    user_agent: Optional[str],
) -> Dict[str, Any]:
    """로그 업데이트"""
    db = get_database()
    if db is None:
        raise Exception("데이터베이스 연결이 없습니다")
    
    collection_name = config_data.get('MONGODB', {}).get('tables', {}).get('log', 'user_log')
    collection = db[collection_name]
    
    timestamp = time.time()
    regdate = time.strftime("%Y-%m-%d %H:%M:%S")
    
    log_doc = {
        "regdate": regdate,
        "timestamp": timestamp,
        "user_id": user_id,
        "eventinfo": eventinfo,
        "user_agent": user_agent,
        "snapshot": snapshot,
    }
    
    # 30일 이전의 오래된 로그 찾기
    old_timestamp = timestamp - (3600*24*30)  # 30일
    old_log = await collection.find_one(
        {"timestamp": {"$lt": old_timestamp}},
        sort=[("timestamp", 1)]
    )
    
    if old_log:
        # 기존 로그 업데이트
        await collection.update_one(
            {"_id": old_log["_id"]},
            {"$set": log_doc}
        )
        log_doc["_id"] = old_log["_id"]
    else:
        # 새 로그 생성
        result = await collection.insert_one(log_doc)
        log_doc["_id"] = result.inserted_id
    
    # _id를 문자열로 변환
    if "_id" in log_doc:
        log_doc["id"] = str(log_doc["_id"])

    return log_doc


async def create_log(
    user_id: Optional[str],
    eventinfo: dict,
    user_agent: Optional[str],
    snapshot: Optional[str],
    cam_no: int = 0
) -> Dict[str, Any]:
    """로그 생성"""
    db = get_database()
    if db is None:
        raise Exception("데이터베이스 연결이 없습니다")
    
    collection_name = config_data.get('MONGODB', {}).get('tables', {}).get('log', 'user_log')
    collection = db[collection_name]
    
    kst = timezone(timedelta(hours=9))
    timestamp = datetime.now(kst).timestamp()
    regdate = datetime.now(kst)
    
    # 30일 이전의 오래된 로그 찾기
    old_timestamp = timestamp - 2592000  # 30일
    old_log = await collection.find_one(
        {"timestamp": {"$lt": old_timestamp}},
        sort=[("timestamp", 1)]
    )
    
    log_doc = {
        "regdate": regdate,
        "timestamp": timestamp,
        "user_id": user_id,
        "eventinfo": eventinfo,
        "user_agent": user_agent,
        "snapshot": snapshot,
        "flag": "n",
        "cam_no": cam_no
    }
    
    if old_log:
        # 기존 로그 업데이트
        await collection.update_one(
            {"_id": old_log["_id"]},
            {"$set": log_doc}
        )
        log_doc["_id"] = old_log["_id"]
    else:
        # 새 로그 생성
        result = await collection.insert_one(log_doc)
        log_doc["_id"] = result.inserted_id
    
    # _id를 문자열로 변환
    if "_id" in log_doc:
        log_doc["id"] = str(log_doc["_id"])
    return log_doc


async def get_logs(page: int = 1, offset: int = 20) -> List[Dict[str, Any]]:
    """로그 목록 조회 (페이지네이션)"""
    db = get_database()
    if db is None:
        return []
    
    collection_name = config_data.get('MONGODB', {}).get('tables', {}).get('log', 'user_log')
    collection = db[collection_name]
    
    skip = (page - 1) * offset
    
    cursor = collection.find().sort("timestamp", -1).skip(skip).limit(offset)
    logs = []
    async for doc in cursor:
        # _id를 문자열로 변환
        if "_id" in doc:
            doc["id"] = str(doc["_id"])
        logs.append(doc)
    return logs


async def get_log_count() -> int:
    """전체 로그 개수 조회"""
    db = get_database()
    if db is None:
        return 0
    
    collection_name = config_data.get('MONGODB', {}).get('tables', {}).get('log', 'user_log')
    collection = db[collection_name]
    
    return await collection.count_documents({})

