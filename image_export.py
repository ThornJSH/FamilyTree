"""
이미지 내보내기 기능
"""
from PyQt6.QtWidgets import QGraphicsScene
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtCore import QRectF
from typing import List
from models import Person
from config import NODE_WIDTH, NODE_HEIGHT


class ImageExporter:
    """캔버스를 이미지로 내보내기"""
    
    @staticmethod
    def export_to_image(scene: QGraphicsScene, people: List[Person], format: str = 'png') -> QImage:
        """
        씬을 이미지로 변환
        
        Args:
            scene: 그래픽 씬
            people: 인물 목록 (bounding box 계산용)
            format: 'png' 또는 'jpeg'
        
        Returns:
            QImage 객체
        """
        if not people:
            return None
        
        # 모든 노드를 포함하는 영역 계산
        padding = 20
        min_x = min(p.x - NODE_WIDTH for p in people)
        min_y = min(p.y - NODE_HEIGHT for p in people)
        max_x = max(p.x + NODE_WIDTH for p in people)
        max_y = max(p.y + NODE_HEIGHT for p in people)
        
        content_width = max_x - min_x
        content_height = max_y - min_y
        
        # 이미지 크기 설정
        image_width = int(content_width + padding * 2)
        image_height = int(content_height + padding * 2)
        
        # QImage 생성
        if format == 'jpeg' or format == 'jpg':
            image = QImage(image_width, image_height, QImage.Format.Format_RGB32)
            image.fill(0xFFFFFF)  # 흰색 배경
        else:
            image = QImage(image_width, image_height, QImage.Format.Format_ARGB32)
            image.fill(0xF4F7F9)  # 배경색
        
        # QPainter로 씬 렌더링
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # 씬의 특정 영역만 렌더링
        source_rect = QRectF(
            min_x - padding,
            min_y - padding,
            content_width + padding * 2,
            content_height + padding * 2
        )
        
        target_rect = QRectF(0, 0, image_width, image_height)
        
        scene.render(painter, target_rect, source_rect)
        painter.end()
        
        return image
