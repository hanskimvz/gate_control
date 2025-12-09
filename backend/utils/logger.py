"""
로깅 유틸리티 모듈
파일 이름과 라인 수를 표시하는 커스텀 로거 제공
"""
import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class CustomFormatter(logging.Formatter):
    """파일 이름과 라인 수를 표시하는 커스텀 포매터"""
    
    # 색상 코드 (터미널에서만 사용)
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',        # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',       # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def __init__(self, use_colors: bool = True):
        super().__init__()
        self.use_colors = use_colors and sys.stdout.isatty()
    
    def format(self, record: logging.LogRecord) -> str:
        # 파일 이름만 추출 (전체 경로가 아닌)
        filename = Path(record.pathname).name
        
        # 로그 레벨에 따른 색상
        if self.use_colors:
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            reset = self.COLORS['RESET']
            levelname = f"{color}{record.levelname:8s}{reset}"
        else:
            levelname = f"{record.levelname:8s}"
        
        # 포맷: [YYYY-MM-DD HH:MM:SS] LEVEL [filename:line] function - message
        log_format = (
            f"[{self.formatTime(record, '%Y-%m-%d %H:%M:%S')}] "
            f"{levelname} "
            f"[{filename}:{record.lineno}] "
            f"{record.funcName} - "
            f"{record.getMessage()}"
        )
        
        # 예외 정보가 있으면 추가
        if record.exc_info:
            log_format += "\n" + self.formatException(record.exc_info)
        
        return log_format


def setup_logger(
    name: str = "gate",
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    use_colors: bool = True
) -> logging.Logger:
    """
    로거 설정 및 반환
    
    Args:
        name: 로거 이름
        level: 로그 레벨 (logging.DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 로그 파일 경로 (None이면 콘솔만 출력)
        use_colors: 콘솔 출력 시 색상 사용 여부
    
    Returns:
        설정된 Logger 인스턴스
    """
    logger = logging.getLogger(name)
    
    # 이미 핸들러가 설정되어 있으면 제거 (중복 방지)
    if logger.handlers:
        logger.handlers.clear()
    
    logger.setLevel(level)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = CustomFormatter(use_colors=use_colors)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러 (지정된 경우)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        # 파일에는 색상 코드 없이 출력
        file_formatter = CustomFormatter(use_colors=False)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


# 기본 로거 인스턴스 생성
_default_logger: Optional[logging.Logger] = None


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    로거 인스턴스 반환
    
    Args:
        name: 로거 이름 (None이면 기본 로거 반환)
    
    Returns:
        Logger 인스턴스
    """
    global _default_logger
    
    if name:
        return logging.getLogger(name)
    
    if _default_logger is None:
        _default_logger = setup_logger()
    
    return _default_logger


# 편의 함수들
def debug(message: str, *args, **kwargs):
    """DEBUG 레벨 로그"""
    get_logger().debug(message, *args, **kwargs)


def info(message: str, *args, **kwargs):
    """INFO 레벨 로그"""
    get_logger().info(message, *args, **kwargs)


def warning(message: str, *args, **kwargs):
    """WARNING 레벨 로그"""
    get_logger().warning(message, *args, **kwargs)


def error(message: str, *args, **kwargs):
    """ERROR 레벨 로그"""
    get_logger().error(message, *args, **kwargs)


def critical(message: str, *args, **kwargs):
    """CRITICAL 레벨 로그"""
    get_logger().critical(message, *args, **kwargs)


def exception(message: str, *args, **kwargs):
    """예외 정보와 함께 ERROR 레벨 로그"""
    get_logger().exception(message, *args, **kwargs)

