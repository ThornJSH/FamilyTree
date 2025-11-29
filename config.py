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

# 폰트 설정
FONT_FAMILY = "Noto Sans KR, 맑은 고딕, Malgun Gothic, sans-serif"

# 데이터베이스 설정
DB_NAME = "familytree.db"
DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)

# 애플리케이션 메타데이터
APP_NAME = "가계도 그리기"
APP_VERSION = "1.0.0"
