import hashlib
from typing import Optional, List
from datetime import datetime
from database import get_database
from models import User, UserCreate, UserUpdate
from config import config_data
from bson import ObjectId
from utils.logger import get_logger

logger = get_logger()


def generate_api_key(user_id: str) -> str:
    """사용자 ID로부터 API 키 생성 (MD5)"""
    return hashlib.md5(user_id.encode()).hexdigest()


async def authenticate_user(user_id: str, password: str) -> Optional[str]:
    """사용자 인증 및 API 키 반환"""
    user = await get_user_by_id(user_id)
    if not user:
        logger.warning(f"인증 실패: 사용자를 찾을 수 없습니다 (user_id: {user_id})")
        return None
    
    # password를 MD5로 해시하여 user_id와 비교
    # 실제로는 password를 별도로 저장하고 검증해야 하지만,
    # 현재 시스템에서는 user_id의 MD5가 api_key이므로
    # password의 MD5가 user_id와 일치하는지 확인
    password_hash = hashlib.md5(password.encode()).hexdigest()
    
    # 간단한 검증: password의 MD5가 user_id와 일치하면 인증 성공
    # 또는 password가 user_id와 일치하면 인증 성공 (임시)
    # 실제 운영 환경에서는 password를 별도로 저장하고 bcrypt 등으로 해시해야 함
    if password == user_id or password_hash == user_id:
        logger.info(f"인증 성공: user_id={user_id}")
        return user.get("api_key")
    
    logger.warning(f"인증 실패: password 불일치 (user_id: {user_id})")
    return None


async def get_user_by_api_key(api_key: str) -> Optional[dict]:
    """API 키로 사용자 조회 (dict 반환)"""
    db = get_database()
    if db is None:
        return None
    
    collection_name = config_data.get('MONGODB', {}).get('tables', {}).get('user', 'user')
    collection = db[collection_name]
    
    user_doc = await collection.find_one({"api_key": api_key})
    return user_doc


async def get_user_by_id(user_id: str) -> Optional[dict]:
    """사용자 ID로 사용자 조회 (dict 반환, MongoDB의 "user_id" 필드로 검색)"""
    db = get_database()
    if db is None:
        return None
    
    collection_name = config_data.get('MONGODB', {}).get('tables', {}).get('user', 'user')
    collection = db[collection_name]
    
    # MongoDB에는 "user_id" 필드로 저장되어 있음
    user_doc = await collection.find_one({"user_id": user_id})
    if user_doc:
        # plate와 plates 필드 통합 처리
        if "plate" in user_doc and "plates" not in user_doc:
            user_doc["plates"] = user_doc.get("plate", [])
        elif "plates" in user_doc and "plate" not in user_doc:
            user_doc["plate"] = user_doc.get("plates", [])
        # _id를 문자열로 변환
        if "_id" in user_doc:
            user_doc["id"] = str(user_doc["_id"])
        return user_doc
    return None


async def create_user(user_data: UserCreate) -> dict:
    """새 사용자 생성"""
    db = get_database()
    if db is None:
        raise Exception("데이터베이스 연결이 없습니다")
    
    collection_name = config_data.get('MONGODB', {}).get('tables', {}).get('user', 'user')
    collection = db[collection_name]
    
    api_key = generate_api_key(user_data.user_id)
    
    # MongoDB 스키마에 맞게 "user_id" 필드 사용, regdate는 문자열 형식
    regdate_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    user_doc = {
        "user_id": user_data.user_id,  # MongoDB에는 "user_id"로 저장
        "api_key": api_key,
        "date_from": user_data.date_from,
        "hour_from": user_data.hour_from,
        "date_to": user_data.date_to,
        "hour_to": user_data.hour_to,
        "flag": user_data.flag,
        "regdate": regdate_str,  # 문자열 형식으로 저장
        "plates": []  # 기본값
    }
    
    result = await collection.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    # plate 필드도 추가 (일부 데이터와의 호환성)
    user_doc["plate"] = user_doc.get("plates", [])
    # _id를 문자열로 변환
    user_doc["id"] = str(user_doc["_id"])
    return user_doc


async def update_user(user_id: str, user_data: UserUpdate) -> Optional[dict]:
    """사용자 정보 업데이트 (MongoDB의 "user_id" 필드로 검색)"""
    db = get_database()
    if db is None:
        raise Exception("데이터베이스 연결이 없습니다")
    
    collection_name = config_data.get('MONGODB', {}).get('tables', {}).get('user', 'user')
    collection = db[collection_name]
    
    update_data = {}
    if user_data.user_id is not None:
        update_data["user_id"] = user_data.user_id  # MongoDB에는 "user_id"로 저장
        # user_id가 변경되면 api_key도 재생성
        update_data["api_key"] = generate_api_key(user_data.user_id)
    if user_data.date_from is not None:
        update_data["date_from"] = user_data.date_from
    if user_data.hour_from is not None:
        update_data["hour_from"] = user_data.hour_from
    if user_data.date_to is not None:
        update_data["date_to"] = user_data.date_to
    if user_data.hour_to is not None:
        update_data["hour_to"] = user_data.hour_to
    if user_data.flag is not None:
        update_data["flag"] = user_data.flag
    
    if not update_data:
        return None
    
    # MongoDB에는 "user_id" 필드로 저장되어 있음
    result = await collection.find_one_and_update(
        {"user_id": user_id},
        {"$set": update_data},
        return_document=True
    )
    
    if result:
        # plate와 plates 필드 통합 처리
        if "plate" in result and "plates" not in result:
            result["plates"] = result.get("plate", [])
        elif "plates" in result and "plate" not in result:
            result["plate"] = result.get("plates", [])
        # _id를 문자열로 변환
        if "_id" in result:
            result["id"] = str(result["_id"])
        return result
    return None


async def get_all_users() -> List[dict]:
    """모든 사용자 조회"""
    db = get_database()
    if db is None:
        return []
    
    collection_name = config_data.get('MONGODB', {}).get('tables', {}).get('user', 'user')
    collection = db[collection_name]
    
    cursor = collection.find().sort("regdate", 1)
    users = []
    async for doc in cursor:
        users.append(doc)
    return users


def valid_datetime(date_from: str, date_to: str, hour_from: int, hour_to: int) -> bool:
    """날짜/시간 유효성 검사"""
    from datetime import datetime, timezone, timedelta
    
    # 한국 시간대 (UTC+9)
    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst)
    print(now)
    
    try:
        if date_from != "0000-00-00":
            dt_from = datetime.strptime(f"{date_from} 00:00:00", "%Y-%m-%d %H:%M:%S")
            dt_from = dt_from.replace(tzinfo=kst)
            # print ("dt_from", dt_from)
            if now < dt_from:
                return False
        
        if date_to != "0000-00-00":
            dt_to = datetime.strptime(f"{date_to} 23:59:59", "%Y-%m-%d %H:%M:%S")
            dt_to = dt_to.replace(tzinfo=kst)
            # print ("dt_to", dt_to)
            if now > dt_to:
                return False
        
        # print ("hour_from", hour_from)
        # print ("hour_to", hour_to)

        if hour_from + hour_to != 0:
            current_hour = now.hour
            print ("current_hour", current_hour)
            if current_hour < hour_from or current_hour >= hour_to:
                return False

        return True
    except Exception as e:
        logger.error(f"날짜/시간 검증 실패: {e}", exc_info=True)
        return False

