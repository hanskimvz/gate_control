from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


# API 요청/응답 모델만 Pydantic 사용, 내부 로직은 dict 사용
class User(BaseModel):
    """사용자 모델 (API 응답용)"""
    id: Optional[str] = None  # _id를 문자열로 변환
    user_id: Optional[str] = None  # 사용자 ID (MongoDB의 "id" 필드)
    api_key: str  # API 키 (MD5 해시)
    date_from: str = "0000-00-00"  # 시작 날짜
    hour_from: int = 0  # 시작 시간
    date_to: str = "0000-00-00"  # 종료 날짜
    hour_to: int = 0  # 종료 시간
    flag: str = "y"  # 활성화 여부 (y/n)
    regdate: Optional[str] = None  # 등록일 (문자열 형식: "2023-07-18 20:13:56")
    name: Optional[str] = None  # 사용자 이름
    plates: Optional[List[str]] = None  # 차량 번호 배열


class Log(BaseModel):
    """로그 모델 (API 응답용)"""
    id: Optional[str] = None  # _id를 문자열로 변환
    regdate: datetime  # 등록일
    timestamp: float  # Unix timestamp
    user_id: Optional[str] = None  # 사용자 ID
    eventinfo: dict = {}  # 이벤트 정보 (IP, mode, api_key 등)
    user_agent: Optional[str] = None
    snapshot: Optional[str] = None  # Base64 인코딩된 이미지
    flag: str = "n"  # 처리 플래그
    cam_no: int = 0  # 카메라 번호


class UserCreate(BaseModel):
    """사용자 생성 요청 모델"""
    user_id: str
    date_from: str = "0000-00-00"
    hour_from: int = 0
    date_to: str = "0000-00-00"
    hour_to: int = 0
    flag: str = "y"


class UserUpdate(BaseModel):
    """사용자 업데이트 요청 모델"""
    user_id: Optional[str] = None
    date_from: Optional[str] = None
    hour_from: Optional[int] = None
    date_to: Optional[str] = None
    hour_to: Optional[int] = None
    flag: Optional[str] = None


class OpenDoorRequest(BaseModel):
    """문 열기 요청 모델"""
    api_key: str


class SnapshotRequest(BaseModel):
    """스냅샷 요청 모델"""
    api_key: str
    cam_no: int = 0


class LoginRequest(BaseModel):
    """로그인 요청 모델"""
    user_id: str
    password: str
