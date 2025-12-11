# Gate Control System

문 제어 시스템 - PHP에서 Python/FastAPI + Vue.js로 마이그레이션

## 프로젝트 구조

```
Gate/
├── backend/                  # FastAPI 백엔드
│   ├── config/              # 설정 모듈
│   │   ├── __init__.py
│   │   └── config.py
│   ├── routers/             # API 라우터
│   │   ├── __init__.py
│   │   ├── api.py           # 로그인/로그 API
│   │   ├── gate.py          # Gate 제어 API
│   │   ├── health.py        # 헬스체크 API
│   │   └── users.py         # 사용자 관리 API
│   ├── services/            # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── camera_service.py    # 카메라 스냅샷/DO 제어
│   │   ├── log_service.py       # 로그 CRUD
│   │   └── user_service.py      # 사용자 인증/CRUD
│   ├── utils/               # 유틸리티
│   │   ├── __init__.py
│   │   └── logger.py        # 로깅 설정
│   ├── database.py          # MongoDB 연결 (Motor 비동기)
│   ├── models.py            # Pydantic 데이터 모델
│   ├── main.py              # FastAPI 앱 진입점
│   └── requirements.txt     # Python 의존성
├── frontend/                # Vue.js 프론트엔드
│   ├── src/
│   │   ├── views/           # 페이지 컴포넌트
│   │   │   ├── gate/        # Gate 제어 페이지
│   │   │   ├── log/         # 로그 조회 페이지
│   │   │   ├── user/        # 사용자 관리 페이지
│   │   │   ├── LoginView.vue
│   │   │   ├── HomeView.vue
│   │   │   └── AboutView.vue
│   │   ├── components/      # 공통 컴포넌트
│   │   │   ├── Header.vue
│   │   │   ├── Modal.vue
│   │   │   └── SlidePanel.vue
│   │   ├── services/        # API 서비스
│   │   │   ├── api.js           # 공통 API 서비스
│   │   │   ├── gate_service.js  # Gate 관련 API
│   │   │   └── user_service.js  # 사용자 관련 API
│   │   ├── router/          # Vue Router 설정
│   │   ├── stores/          # Pinia 상태 관리
│   │   └── utils/           # 유틸리티 (쿠키 등)
│   ├── package.json
│   └── vite.config.js
├── config/                  # 설정 파일
│   ├── config.json          # 카메라 및 DB 설정
│   └── users.json
├── gate_control.service     # systemd 서비스 파일
└── nginx.gate_control.conf  # Nginx 설정
```

## 기술 스택

### 백엔드
- **Python 3.10+**
- **FastAPI 0.104.1** - 비동기 웹 프레임워크
- **Motor 3.3.2** - MongoDB 비동기 드라이버
- **Pydantic 2.5.0** - 데이터 검증
- **Uvicorn** - ASGI 서버

### 프론트엔드
- **Vue.js 3.5** - 프론트엔드 프레임워크
- **Vue Router 4.6** - SPA 라우팅
- **Pinia 3.0** - 상태 관리
- **Vite 7.2** - 빌드 도구
- **Node.js 20.19+ / 22.12+**

### 데이터베이스
- **MongoDB** - NoSQL 데이터베이스
  - `user` 컬렉션: 사용자 정보
  - `gate_log` 컬렉션: 문 열기 이벤트 로그

## 주요 기능

### 1. 문 제어 (Gate)
- API 키 기반 사용자 인증
- 카메라 DO(Digital Output) 제어로 문 열기
- 문 열기 후 자동 닫힘 (10초)
- 다중 카메라 지원 (main, sub1, sub2, sub3, sub4)
- 실시간 카메라 스냅샷 확인

### 2. 로그인 시스템
- 사용자 ID/비밀번호 기반 인증
- API 키 발급 (MD5 해시)
- 쿠키 기반 세션 관리 (7일 유지)
- 네비게이션 가드로 접근 제어

### 3. 로그 관리
- 문 열기 이벤트 자동 기록
- 스냅샷 이미지 저장 (Base64)
- 클라이언트 정보 수집 (IP, User-Agent, 브라우저 정보)
- 페이지네이션 지원
- 30일 이상 오래된 로그 자동 정리 (재활용)

### 4. 사용자 관리
- 사용자 CRUD (생성/조회/수정/삭제)
- 유효 기간 설정 (날짜, 시간대)
- 활성/비활성 상태 관리
- Gate 접근 링크 생성
- 차량 번호판 등록

### 5. 카메라 시스템
- 다중 카메라 지원
- 카메라별 인증 설정 (Basic Auth)
- 스냅샷 CGI 호출
- DO(Digital Output) 제어

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
# 개발 모드 (자동 새로고침)
uvicorn main:app --reload --host 0.0.0.0 --port 22450

# 또는 main.py 직접 실행 (config.json의 API_SERVER 설정 사용)
python main.py
```

### 프론트엔드 설정

```bash
cd frontend
npm install
```

환경 변수 설정 (선택사항):
`.env` 파일 생성:
```
VITE_API_BASE_URL=http://localhost:22450/api/v1
```

프론트엔드 실행:
```bash
# 개발 모드
npm run dev

# 프로덕션 빌드
npm run build
```

## API 엔드포인트

### 인증
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/v1/login` | 로그인 (user_id, password) → api_key 반환 |

### Gate 제어 (Action 기반)
| Method | Endpoint | Action | 설명 |
|--------|----------|--------|------|
| POST | `/api/v1/gate` | `ready` | 사용자 확인 및 카메라 목록 조회 |
| POST | `/api/v1/gate` | `open` | 문 열기 |
| POST | `/api/v1/gate` | `snapshot` | 카메라 스냅샷 가져오기 |
| GET | `/api/v1/gate?api_key={key}&mode=exit` | - | 외부 카메라에서 문 열기 (레거시) |

**요청 형식:**
```json
{
  "action": "open",
  "api_key": "your_api_key",
  "data": { ... }
}
```

### 스냅샷 저장
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/v1/snapshot` | 외부에서 스냅샷 저장 (form-data) |

### 사용자 관리 (Action 기반)
| Method | Endpoint | Action | 설명 |
|--------|----------|--------|------|
| POST | `/api/v1/users` | `list` | 사용자 목록 조회 |
| POST | `/api/v1/users` | `create` | 사용자 생성 |
| POST | `/api/v1/users` | `modify` | 사용자 수정 |
| POST | `/api/v1/users` | `remove` | 사용자 삭제 |

### 로그 관리
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/logs?page={page}&offset={offset}` | 로그 목록 조회 (페이지네이션) |

### 헬스체크
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/health` | 서버 상태 확인 |

## 설정 파일

### `config/config.json`

```json
{
  "VERSION": "1.0.0",
  "BUILD": {
    "web": "20251209",
    "api": "20251209"
  },
  "CAMERAS": {
    "main": {
      "address": "192.168.3.19",
      "port": 80,
      "userid": "root",
      "userpw": "pass",
      "snapshot_cgi": "/nvc-cgi/operator/snapshot.fcgi",
      "DO_cgi": {
        "on": "nvc-cgi/admin/param.fcgi?action=update&group=DIDO.DO.Ch0&trig=on",
        "off": "nvc-cgi/admin/param.fcgi?action=update&group=DIDO.DO.Ch0&trig=off",
        "trig": "nvc-cgi/admin/param.fcgi?action=update&group=DIDO.DO.Ch0&trigon="
      },
      "rs485port": 7101
    },
    "sub1": { ... },
    "sub2": { ... }
  },
  "MONGODB": {
    "host": "your_mongodb_host",
    "user": "gate_user",
    "password": "your_password",
    "db": "gate_control",
    "port": 5090,
    "pool": {
      "max_pool_size": 50,
      "min_pool_size": 5,
      "max_idle_time_ms": 30000
    },
    "tables": {
      "user": "user",
      "log": "gate_log"
    }
  },
  "API_SERVER": {
    "host": "0.0.0.0",
    "port": 22450
  }
}
```

## 사용 방법

### 관리자 접근
1. 브라우저에서 `http://localhost:5173` 접속
2. 로그인 페이지에서 사용자 ID/비밀번호 입력
3. 로그인 후 사용자 관리, 로그 조회 가능

### Gate 사용자 접근
1. 관리자가 사용자 등록 후 Gate 링크 제공
2. `http://gate.amisense.com/gate?api_key={api_key}` 형식의 URL로 접속
3. OPEN 버튼으로 문 열기

## 데이터 모델

### User (사용자)
```json
{
  "_id": "ObjectId",
  "user_id": "사용자 ID",
  "name": "사용자 이름",
  "api_key": "MD5 해시된 API 키",
  "date_from": "유효 시작일 (YYYY-MM-DD)",
  "date_to": "유효 종료일 (YYYY-MM-DD)",
  "hour_from": 0,
  "hour_to": 24,
  "flag": "y/n (활성/비활성)",
  "regdate": "등록일",
  "plates": ["차량번호1", "차량번호2"]
}
```

### Log (로그)
```json
{
  "_id": "ObjectId",
  "regdate": "기록일시",
  "timestamp": 1234567890.123,
  "user_id": "사용자 ID",
  "eventinfo": {
    "ip": "클라이언트 IP",
    "mode": "open/exit/snapshot",
    "api_key": "사용된 API 키",
    "client_info": { ... }
  },
  "user_agent": "브라우저 정보",
  "snapshot": "data:image/jpg;base64,..."
}
```

## 개발 참고사항

- **API 문서**: `http://localhost:22450/docs` (Swagger UI)
- **로그 파일**: `backend/logs/gate.log`
- **커넥션 풀**: MongoDB 비동기 커넥션 풀 지원 (기본: 5~50)
- **CORS**: 현재 모든 도메인 허용 (프로덕션에서는 제한 필요)

## 배포

### systemd 서비스 등록
```bash
sudo cp gate_control.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gate_control
sudo systemctl start gate_control
```

### Nginx 리버스 프록시
```bash
sudo cp nginx.gate_control.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/nginx.gate_control.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```
