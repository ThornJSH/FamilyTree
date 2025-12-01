"""
개별 인물 노드를 표현하는 QGraphicsItem
"""
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsTextItem
from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QPen, QBrush, QColor, QPainterPath, QFont
from models import Person
from config import NODE_WIDTH, NODE_HEIGHT, TEXT_COLOR, PANEL_BG_COLOR, DANGER_COLOR


class PersonNode(QGraphicsItem):
    """가계도의 한 인물을 나타내는 그래픽 노드"""
    
    def __init__(self, person: Person):
        super().__init__()
        self.person = person
        # self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 텍스트 아이템 생성
        self.name_text = QGraphicsTextItem(self)
        self.name_text.setPlainText(person.name)
        # 폰트 설정 수정: 단일 폰트 이름 사용
        font = QFont("Malgun Gothic", 11, QFont.Weight.Medium)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.name_text.setFont(font)
        self.name_text.setDefaultTextColor(QColor(TEXT_COLOR))
        
        # 출생연도 텍스트 (반려동물이 아닌 경우)
        self.birth_year_text = None
        if person.nodeType != 'pet' and person.birthYear:
            self.birth_year_text = QGraphicsTextItem(self)
            self.birth_year_text.setPlainText(f"({person.birthYear})")
            birth_font = QFont("Malgun Gothic", 9)
            birth_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
            self.birth_year_text.setFont(birth_font)
            self.birth_year_text.setDefaultTextColor(QColor(TEXT_COLOR))
        
        self.update_text_positions()
    
    def boundingRect(self):
        """아이템의 경계 사각형"""
        return QRectF(-NODE_WIDTH/2, -NODE_HEIGHT/2, NODE_WIDTH, NODE_HEIGHT)
    
    def paint(self, painter, option, widget):
        """노드 그리기"""
        from PyQt6.QtGui import QPainter  # QPainter import 추가
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 선택 여부에 따른 펜 설정
        if self.isSelected():
            pen = QPen(QColor("#4A90E2"), 3)
        else:
            pen = QPen(QColor(TEXT_COLOR), 2)
        
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor(PANEL_BG_COLOR)))
        
        # 성별/타입에 따라 다른 도형 그리기
        if self.person.nodeType == 'pet':
            # 반려동물: 마름모
            path = QPainterPath()
            size = NODE_WIDTH / 2
            path.moveTo(0, -size)
            path.lineTo(size, 0)
            path.lineTo(0, size)
            path.lineTo(-size, 0)
            path.closeSubpath()
            painter.drawPath(path)
        elif self.person.gender == 'male':
            # 남성: 둥근 모서리 사각형
            rect = QRectF(-NODE_WIDTH/2, -NODE_HEIGHT/2, NODE_WIDTH, NODE_HEIGHT)
            painter.drawRoundedRect(rect, 5, 5)
        else:
            # 여성: 원형
            rect = QRectF(-NODE_HEIGHT/2, -NODE_HEIGHT/2, NODE_HEIGHT, NODE_HEIGHT)
            painter.drawEllipse(rect)
        
        # 사망한 경우 X 표시
        if self.person.isDeceased:
            # 사망 표시를 더 굵게 (3px)
            painter.setPen(QPen(QColor(DANGER_COLOR), 3))
            
            if self.person.gender == 'male' and self.person.nodeType != 'pet':
                # 남성: 모서리에서 모서리로 꽉 차게 그리기 (둥근 모서리 고려하여 3px 안쪽으로)
                inset = 3
                half_w = NODE_WIDTH / 2 - inset
                half_h = NODE_HEIGHT / 2 - inset
                painter.drawLine(int(-half_w), int(-half_h), int(half_w), int(half_h))
                painter.drawLine(int(half_w), int(-half_h), int(-half_w), int(half_h))
            else:
                # 여성/반려동물: 기존대로 (70% 크기)
                size = (NODE_WIDTH if self.person.nodeType == 'pet' else NODE_HEIGHT) * 0.7
                painter.drawLine(
                    int(-size/2), int(-size/2),
                    int(size/2), int(size/2)
                )
                painter.drawLine(
                    int(size/2), int(-size/2),
                    int(-size/2), int(size/2)
                )
    
    def update_text_positions(self):
        """텍스트 위치 업데이트 (중앙 정렬)"""
        # 이름 텍스트 중앙 정렬
        name_rect = self.name_text.boundingRect()
        self.name_text.setPos(-name_rect.width()/2, -25)
        
        # 출생연도 텍스트 중앙 정렬
        if self.birth_year_text:
            birth_rect = self.birth_year_text.boundingRect()
            self.birth_year_text.setPos(-birth_rect.width()/2, 5)
    
    def itemChange(self, change, value):
        """아이템 변경 시 호출"""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # 위치가 변경되면 Person 객체의 좌표도 업데이트
            pos = self.pos()
            self.person.x = pos.x()
            self.person.y = pos.y()
            
            # 캔버스에 선 다시 그리기 요청
            if self.scene():
                view = self.scene().views()[0] if self.scene().views() else None
                if view and hasattr(view, 'redraw_lines'):
                    view.redraw_lines()
        return super().itemChange(change, value)
