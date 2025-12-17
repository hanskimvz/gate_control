from pydantic_settings import BaseSettings
from typing import Optional, Dict, List, Any
import json
import os
from pathlib import Path


class Settings(BaseSettings):
    # MongoDB 설정
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "gate_db"
    
    # API 설정
    api_title: str = "Gate API"
    api_version: str = "1.0.0"
    debug: bool = False
    
    # 보안 설정
    secret_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def load_config_json() -> Dict[str, Any]:
    """config.json 파일을 읽어서 반환"""
    # 환경 변수로 경로 지정 가능
    env_config_path = os.getenv("CONFIG_JSON_PATH")
    if env_config_path:
        config_path = Path(env_config_path).resolve()
        if config_path.exists() and config_path.is_file():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            raise FileNotFoundError(f"환경 변수 CONFIG_JSON_PATH로 지정한 파일을 찾을 수 없습니다: {config_path}")
    
    # 현재 파일 위치에서 프로젝트 루트 찾기
    # backend/config/config.py -> backend/ -> 프로젝트 루트
    current_file = Path(__file__).resolve()
    backend_dir = current_file.parent.parent  # backend/
    project_root = backend_dir.parent  # 프로젝트 루트
    
    # 여러 가능한 경로 시도
    possible_paths = [
        # 1. 프로젝트 루트의 config/config.json (기본)
        project_root / "config" / "config.json",
        # 2. 현재 작업 디렉토리 기준
        Path.cwd() / "config" / "config.json",
        # 3. backend/ 디렉토리에서 실행하는 경우
        Path.cwd().parent / "config" / "config.json" if Path.cwd().name == "backend" else None,
        # 4. backend/config/ 디렉토리에서 실행하는 경우
        Path.cwd().parent.parent / "config" / "config.json" if Path.cwd().name == "config" else None,
        # 5. backend/config/config.json (로컬 설정 파일)
        backend_dir / "config" / "config.json",
    ]
    
    # None이 아닌 경로만 필터링하고 시도
    config_path = None
    tried_paths = []
    
    for path in possible_paths:
        if path is None:
            continue
        try:
            resolved_path = path.resolve()
            tried_paths.append(str(resolved_path))
            if resolved_path.exists() and resolved_path.is_file():
                config_path = resolved_path
                break
        except (OSError, RuntimeError) as e:
            tried_paths.append(f"{path} (오류: {e})")
            continue
    
    if config_path is None:
        # 모든 경로를 시도했지만 찾지 못한 경우
        cwd = Path.cwd()
        raise FileNotFoundError(
            f"config.json 파일을 찾을 수 없습니다.\n"
            f"현재 파일 위치: {current_file}\n"
            f"프로젝트 루트: {project_root}\n"
            f"현재 작업 디렉토리: {cwd}\n"
            f"시도한 경로:\n" + 
            "\n".join(f"  - {p}" for p in tried_paths) +
            f"\n\n디버깅 정보:\n"
            f"  - backend_dir 존재: {backend_dir.exists()}\n"
            f"  - project_root 존재: {project_root.exists()}\n"
            f"  - project_root/config 존재: {(project_root / 'config').exists()}"
        )
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_config_json_path() -> Path:
    """config.json 파일 경로를 반환"""
    # 환경 변수로 경로 지정 가능
    env_config_path = os.getenv("CONFIG_JSON_PATH")
    if env_config_path:
        config_path = Path(env_config_path).resolve()
        if config_path.exists() and config_path.is_file():
            return config_path
        else:
            raise FileNotFoundError(f"환경 변수 CONFIG_JSON_PATH로 지정한 파일을 찾을 수 없습니다: {config_path}")
    
    # 현재 파일 위치에서 프로젝트 루트 찾기
    current_file = Path(__file__).resolve()
    backend_dir = current_file.parent.parent
    project_root = backend_dir.parent
    
    # 여러 가능한 경로 시도
    possible_paths = [
        project_root / "config" / "config.json",
        Path.cwd() / "config" / "config.json",
        Path.cwd().parent / "config" / "config.json" if Path.cwd().name == "backend" else None,
        Path.cwd().parent.parent / "config" / "config.json" if Path.cwd().name == "config" else None,
        backend_dir / "config" / "config.json",
    ]
    
    for path in possible_paths:
        if path is None:
            continue
        try:
            resolved_path = path.resolve()
            if resolved_path.exists() and resolved_path.is_file():
                return resolved_path
        except (OSError, RuntimeError):
            continue
    
    raise FileNotFoundError("config.json 파일을 찾을 수 없습니다.")


def update_config(key: str, value: Any) -> Dict[str, Any]:
    """
    config.json 파일의 특정 키 값을 업데이트합니다.
    
    Args:
        key: 업데이트할 키 (점으로 구분된 경로 지원)
             예: "VERSION", "CAMERAS.sub2.header.X-Token"
        value: 새로운 값
    
    Returns:
        업데이트된 전체 config 딕셔너리
    
    Examples:
        update_config("VERSION", "1.1.1")
        update_config("CAMERAS.sub2.header.X-Token", "new_token_value")
        update_config("MONGODB.port", 5091)
    """
    global config_data
    
    config_path = get_config_json_path()
    
    # 현재 config 다시 로드 (다른 프로세스에서 변경되었을 수 있음)
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 키 경로를 파싱하여 중첩된 딕셔너리 업데이트
    keys = key.split('.')
    
    if len(keys) == 1:
        # 최상위 키인 경우
        config[key] = value
    else:
        # 중첩된 키인 경우
        current = config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
    
    # 파일에 저장
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    
    # 전역 config_data 업데이트
    config_data = config
    
    return config


settings = Settings()
config_data = load_config_json()

if __name__ == "__main__":
    print(config_data)
    
    # 테스트 예시
    # update_config("VERSION", "1.1.1")
    # update_config("CAMERAS.sub2.header.X-Token", "new_token_value")

