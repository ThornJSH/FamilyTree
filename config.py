"""
애플리케이션 설정 상수
"""
import os

# 노드 크기 및 간격 설정
NODE_WIDTH = 80
NODE_HEIGHT = 80
SIBLING_SPACING = 30
LEVEL_SPACING = 140

# 색상 설정 (웹앱과 동일)
PRIMARY_COLOR = "#4A90E2"
SECONDARY_COLOR = "#50E3C2"
BACKGROUND_COLOR = "#F4F7F9"
PANEL_BG_COLOR = "#FFFFFF"
TEXT_COLOR = "#4A4A4A"
BORDER_COLOR = "#E0E6ED"
DANGER_COLOR = "#D0021B"

# 감정 관계선 색상
INTIMATE_COLOR = "#4A90E2"  # 파랑 (친밀)
DISTANT_COLOR = "#2ECC71"   # 초록 (소원)
CONFLICT_COLOR = "#9B59B6"  # 보라 (갈등)

# 폰트 설정
FONT_FAMILY = "Noto Sans KR, 맑은 고딕, Malgun Gothic, sans-serif"

# 데이터베이스 설정
import sys

# 데이터베이스 설정
DB_NAME = "familytree.db"

if getattr(sys, 'frozen', False):
    # 실행 파일로 실행 시 (exe 파일이 있는 위치)
    DB_PATH = os.path.join(os.path.dirname(sys.executable), DB_NAME)
else:
    # 파이썬 스크립트로 실행 시
    DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)

# 애플리케이션 메타데이터
APP_NAME = "가계도 그리기"
APP_VERSION = "1.0.0"
