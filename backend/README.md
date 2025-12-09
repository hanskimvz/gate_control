# Gate Backend

FastAPI와 MongoDB를 사용한 백엔드 API 서버입니다.

## 요구사항

- Python 3.8 이상
- MongoDB 4.4 이상
- Ubuntu 20.04

## 설치 방법

### 1. 가상 환경 생성 및 활성화

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`env.example` 파일을 참고하여 `.env` 파일을 생성하고 필요한 값들을 설정하세요.

```bash
cp env.example .env
# .env 파일을 편집하여 설정값 입력
```

### 4. MongoDB 실행

로컬에서 MongoDB를 실행하거나, Docker를 사용할 수 있습니다:

```bash
# Docker 사용 시
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### 5. 서버 실행

```bash
# 개발 모드
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 프로덕션 모드
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 프로젝트 구조

```
backend/
├── main.py              # FastAPI 애플리케이션 진입점
├── config.py            # 설정 관리
├── database.py          # MongoDB 연결 관리
├── requirements.txt     # Python 의존성
├── .env.example         # 환경 변수 예시
├── routers/             # API 라우터
│   ├── __init__.py
│   ├── health.py        # 헬스 체크 엔드포인트
│   └── api.py           # 메인 API 엔드포인트
└── README.md
```

## 주요 엔드포인트

- `GET /` - 루트 엔드포인트
- `GET /health` - 헬스 체크
- `GET /api/v1/test` - 테스트 엔드포인트

