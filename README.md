# Gate Control System

문 제어 시스템 - PHP에서 Python/FastAPI + Vue.js로 마이그레이션

## 프로젝트 구조

```
Gate/
├── backend/          # FastAPI 백엔드
│   ├── config/       # 설정 파일
│   ├── routers/      # API 라우터
│   ├── services/     # 비즈니스 로직
│   ├── models.py     # 데이터 모델
│   ├── database.py   # MongoDB 연결
│   └── main.py       # FastAPI 앱 진입점
├── frontend/         # Vue.js 프론트엔드
│   ├── src/
│   │   ├── views/    # 페이지 컴포넌트
│   │   ├── services/ # API 서비스
│   │   └── router/   # 라우터 설정
└── config/           # 설정 파일
    └── config.json   # 카메라 및 DB 설정
```

## 주요 변경사항

### 백엔드
- **PHP → Python/FastAPI**: 비동기 처리 및 현대적인 API 구조
- **MySQL → MongoDB**: NoSQL 데이터베이스로 마이그레이션
- **RESTful API**: 표준 REST API 엔드포인트 제공

### 프론트엔드
- **jQuery → Vue.js 3**: 컴포넌트 기반 프론트엔드 프레임워크
- **SPA 구조**: 단일 페이지 애플리케이션
- **반응형 UI**: 모던한 사용자 인터페이스

## 기능

1. **문 열기**: API 키 기반 인증 후 문 제어
2. **카메라 스냅샷**: 실시간 카메라 이미지 확인
3. **로그 관리**: 문 열기 이벤트 로그 조회
4. **사용자 관리**: 사용자 정보 CRUD 작업

## 설치 및 실행

### 백엔드 설정

```bash
cd backend
pip install -r requirements.txt
```

환경 변수 설정 (선택사항):
```bash
cp env.example .env
# .env 파일 수정
```

백엔드 실행:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 프론트엔드 설정

```bash
cd frontend
npm install
```

환경 변수 설정 (선택사항):
`.env` 파일 생성:
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

프론트엔드 실행:
```bash
npm run dev
```

## API 엔드포인트

### 인증 및 문 제어
- `GET /api/v1/ready?api_key={key}` - 사용자 확인
- `POST /api/v1/open` - 문 열기
- `POST /api/v1/snapshot` - 스냅샷 가져오기
- `GET /api/v1/exit?api_key={key}` - 외부 카메라에서 문 열기

### 사용자 관리
- `GET /api/v1/users?api_key={key}` - 사용자 목록
- `POST /api/v1/users` - 사용자 생성/수정

### 로그 관리
- `GET /api/v1/logs?page={page}&offset={offset}` - 로그 목록

## 설정 파일

`config/config.json` 파일 구조:

```json
{
  "CAMERAS": [
    {
      "address": "192.168.3.19",
      "userid": "root",
      "userpw": "pass",
      "snapshot_cgi": "/nvc-cgi/operator/snapshot.fcgi",
      "DO_cgi": {
        "on": "nvc-cgi/admin/param.fcgi?action=update&group=DIDO.DO.Ch0&trig=on",
        "off": "nvc-cgi/admin/param.fcgi?action=update&group=DIDO.DO.Ch0&trig=off",
        "trig": "nvc-cgi/admin/param.fcgi?action=update&group=DIDO.DO.Ch0&trigon="
      }
    }
  ],
  "MONGODB": {
    "host": "124.61.244.239",
    "user": "gate_user",
    "password": "13579",
    "db": "gate_control",
    "port": 5090,
    "tables": {
      "user": "user",
      "log": "user_log"
    }
  }
}
```

## 사용 방법

1. 브라우저에서 `http://localhost:5173` 접속
2. 각 페이지에 `?api_key=YOUR_API_KEY` 추가하여 접근
3. Gate 페이지에서 문 열기 기능 사용
4. Logs 페이지에서 이벤트 로그 확인
5. Users 페이지에서 사용자 관리

## 개발 참고사항

- 백엔드 API 문서: `http://localhost:8000/docs` (Swagger UI)
- MongoDB 연결은 `config/config.json`에서 설정
- 카메라 설정도 동일한 파일에서 관리

