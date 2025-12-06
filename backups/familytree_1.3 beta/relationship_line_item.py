"""
관계선 그래픽 아이템
"""
import math
from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsEllipseItem, QGraphicsItem
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPen, QColor, QPainterPath, QPainter, QBrush
from models import RelationshipLine
from config import INTIMATE_COLOR, DISTANT_COLOR, CONFLICT_COLOR


class RelationshipLineItem(QGraphicsPathItem):
    """드래그 가능한 관계선 그래픽 아이템"""
    
    def __init__(self, relationship_line: RelationshipLine, parent=None):
        super().__init__(parent)
        self.relationship_line = relationship_line
        self.start_handle = None
        self.end_handle = None
        self.dragging_state = None  # None, 'start', 'end', 'body'
        self.last_mouse_pos = None
        self.arrow_items = []  # 화살표 아이템 추적
        
        # 플래그 설정
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        # self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True) # 좌표 충돌 방지를 위해 비활성화
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        
        # z-index를 높게 설정하여 노드 위에 표시
        self.setZValue(1000)
        
        # 핸들 생성
        self.create_handles()
        
        # 선 그리기
        self.update_line()
    
    def create_handles(self):
        """양 끝점에 드래그 핸들 생성"""
        handle_size = 10  # 핸들 크기 약간 증가
        
        # 시작점 핸들
        self.start_handle = QGraphicsEllipseItem(
            -handle_size/2, -handle_size/2, handle_size, handle_size, self
        )
        self.start_handle.setBrush(QBrush(QColor("#FFFFFF")))
        self.start_handle.setPen(QPen(QColor("#000000"), 1))
        self.start_handle.setZValue(1001)
        self.start_handle.setVisible(False)
        
        # 끝점 핸들
        self.end_handle = QGraphicsEllipseItem(
            -handle_size/2, -handle_size/2, handle_size, handle_size, self
        )
        self.end_handle.setBrush(QBrush(QColor("#FFFFFF")))
        self.end_handle.setPen(QPen(QColor("#000000"), 1))
        self.end_handle.setZValue(1001)
        self.end_handle.setVisible(False)
        
        # 핸들 위치 설정
        self.update_handle_positions()
    
    def update_handle_positions(self):
        """핸들 위치 업데이트"""
        # 아이템이 항상 (0,0)에 있으므로, 절대 좌표를 그대로 로컬 좌표로 사용 가능
        if self.start_handle:
            self.start_handle.setPos(self.relationship_line.x1, self.relationship_line.y1)
        if self.end_handle:
            self.end_handle.setPos(self.relationship_line.x2, self.relationship_line.y2)
    
    def update_line(self):
        """선 스타일에 따라 경로 업데이트"""
        # 기존 화살표 제거
        for arrow_item in self.arrow_items:
            if arrow_item.scene():
                arrow_item.scene().removeItem(arrow_item)
        self.arrow_items.clear()
        
        path = QPainterPath()
        
        x1, y1 = self.relationship_line.x1, self.relationship_line.y1
        x2, y2 = self.relationship_line.x2, self.relationship_line.y2
        
        line_type = self.relationship_line.lineType
        
        # 색상 결정
        if 'intimate' in line_type:
            color = QColor(INTIMATE_COLOR)
        elif 'distant' in line_type:
            color = QColor(DISTANT_COLOR)
        elif 'conflict' in line_type:
            color = QColor(CONFLICT_COLOR)
        else:
            color = QColor("#000000")
        
        # 펜 설정
        pen = QPen(color, 2)  # 두께 약간 증가
        
        # 선 스타일 결정
        if 'distant' in line_type:
            # 점선 (소원)
            pen.setStyle(Qt.PenStyle.DashLine)
            pen.setDashPattern([6, 3])
            path.moveTo(x1, y1)
            path.lineTo(x2, y2)
        elif 'conflict' in line_type:
            # 지그재그선 (갈등)
            pen.setStyle(Qt.PenStyle.SolidLine)
            path = self.create_zigzag_path(x1, y1, x2, y2)
        else:
            # 실선 (친밀)
            pen.setStyle(Qt.PenStyle.SolidLine)
            path.moveTo(x1, y1)
            path.lineTo(x2, y2)
        
        self.setPath(path)
        self.setPen(pen)
        
        # 화살표 그리기
        self.draw_arrows(x1, y1, x2, y2, color)
    
    def create_zigzag_path(self, x1, y1, x2, y2):
        """지그재그 경로 생성"""
        path = QPainterPath()
        path.moveTo(x1, y1)
        
        # 선의 길이와 각도 계산
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx*dx + dy*dy)
        
        # 최소 길이 확인
        if length < 10:
            path.lineTo(x2, y2)
            return path
            
        # 정규화된 방향 벡터
        ux = dx / length
        uy = dy / length
        
        # 수직 벡터
        vx = -uy
        vy = ux
        
        # 직선 구간 (padding)
        padding = 15
        
        # 전체 길이가 패딩보다 작으면 그냥 직선
        if length <= padding * 2:
            path.lineTo(x2, y2)
            return path
            
        # 시작 직선 구간
        start_x = x1 + ux * padding
        start_y = y1 + uy * padding
        path.lineTo(start_x, start_y)
        
        # 지그재그 파라미터
        amplitude = 6  # 진폭
        wavelength = 12  # 파장 (조금 더 촘촘하게)
        
        # 지그재그 구간 길이
        zigzag_length = length - (padding * 2)
        num_waves = int(zigzag_length / wavelength)
        
        if num_waves < 1:
             path.lineTo(x2, y2)
             return path

        # 실제 파장에 맞춰 재조정 (끊김 방지)
        actual_wavelength = zigzag_length / num_waves
        
        for i in range(num_waves * 2 + 1): # 반파장 단위로 계산
            t = i * (actual_wavelength / 2)
            
            # 현재 위치 (직선 구간 이후부터 시작)
            current_dist = padding + t
            
            px = x1 + ux * current_dist
            py = y1 + uy * current_dist
            
            # 지그재그 오프셋
            offset = 0
            if i % 4 == 1: # 위
                offset = amplitude
            elif i % 4 == 3: # 아래
                offset = -amplitude
                
            px += vx * offset
            py += vy * offset
            
            path.lineTo(px, py)
        
        # 마지막 직선 구간
        path.lineTo(x2, y2)
        
        return path
    
    def draw_arrows(self, x1, y1, x2, y2, color):
        """화살표 그리기"""
        line_type = self.relationship_line.lineType
        arrow_size = 10
        
        # 방향 벡터 계산
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx*dx + dy*dy)
        
        if length < 1:
            return
        
        # 정규화
        ux = dx / length
        uy = dy / length
        
        # 화살표 그리기
        if 'two' in line_type:
            # 양쪽 화살표
            self.draw_arrow_head(x1, y1, -ux, -uy, arrow_size, color)
            self.draw_arrow_head(x2, y2, ux, uy, arrow_size, color)
        else:
            # 한쪽 화살표 (끝점)
            self.draw_arrow_head(x2, y2, ux, uy, arrow_size, color)
    
    def draw_arrow_head(self, x, y, ux, uy, size, color):
        """화살표 머리 그리기 (채워진 삼각형)"""
        # 화살표 각도
        angle = 30 * math.pi / 180
        
        # 왼쪽 날개
        left_x = x - size * (ux * math.cos(angle) + uy * math.sin(angle))
        left_y = y - size * (uy * math.cos(angle) - ux * math.sin(angle))
        
        # 오른쪽 날개
        right_x = x - size * (ux * math.cos(angle) - uy * math.sin(angle))
        right_y = y - size * (uy * math.cos(angle) + ux * math.sin(angle))
        
        # 채워진 삼각형 경로
        arrow_path = QPainterPath()
        arrow_path.moveTo(x, y)
        arrow_path.lineTo(left_x, left_y)
        arrow_path.lineTo(right_x, right_y)
        arrow_path.closeSubpath()
        
        # 화살표 아이템 생성 (채워진 삼각형)
        arrow_item = QGraphicsPathItem(arrow_path, self)
        arrow_item.setPen(QPen(color, 1))
        arrow_item.setBrush(QBrush(color))
        arrow_item.setZValue(1000)
        self.arrow_items.append(arrow_item)  # 화살표 추적
    
    def mousePressEvent(self, event):
        """마우스 클릭 이벤트"""
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return

        scene_pos = event.scenePos()
        
        # 시작점/끝점까지의 거리 계산
        # 아이템 좌표계가 0,0이므로 scenePos와 relationship_line 좌표를 직접 비교해도 됨
        start_dist = math.sqrt((scene_pos.x() - self.relationship_line.x1)**2 + 
                              (scene_pos.y() - self.relationship_line.y1)**2)
        end_dist = math.sqrt((scene_pos.x() - self.relationship_line.x2)**2 + 
                            (scene_pos.y() - self.relationship_line.y2)**2)
        
        # 드래그 핸들 결정 로직
        if start_dist < 20:
            self.dragging_state = 'start'
            self.last_mouse_pos = scene_pos
            event.accept()
        elif end_dist < 20:
            self.dragging_state = 'end'
            self.last_mouse_pos = scene_pos
            event.accept()
        else:
            self.dragging_state = 'body'
            self.last_mouse_pos = scene_pos
            event.accept()
            # 선택 처리
            # self.setSelected(True) # 기본 동작이 처리할 수 있음
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """마우스 이동 이벤트"""
        if not self.dragging_state:
            super().mouseMoveEvent(event)
            return
            
        scene_pos = event.scenePos()
        
        if self.dragging_state == 'start':
            # 시작점 핸들 드래그
            self.relationship_line.x1 = scene_pos.x()
            self.relationship_line.y1 = scene_pos.y()
            self.update_line()
            self.update_handle_positions()
            event.accept()
        
        elif self.dragging_state == 'end':
            # 끝점 핸들 드래그
            self.relationship_line.x2 = scene_pos.x()
            self.relationship_line.y2 = scene_pos.y()
            self.update_line()
            self.update_handle_positions()
            event.accept()
            
        elif self.dragging_state == 'body':
            # 몸통 전체 이동
            dx = scene_pos.x() - self.last_mouse_pos.x()
            dy = scene_pos.y() - self.last_mouse_pos.y()
            
            self.relationship_line.x1 += dx
            self.relationship_line.y1 += dy
            self.relationship_line.x2 += dx
            self.relationship_line.y2 += dy
            
            self.last_mouse_pos = scene_pos
            self.update_line()
            self.update_handle_positions()
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """마우스 릴리즈 이벤트"""
        self.dragging_state = None
        self.last_mouse_pos = None
        super().mouseReleaseEvent(event)
    
    def shape(self):
        """히트 디텍션 영역 재정의 (선이 얇거나 점선이어도 선택 잘 되게)"""
        path = QPainterPath()
        path.moveTo(self.relationship_line.x1, self.relationship_line.y1)
        path.lineTo(self.relationship_line.x2, self.relationship_line.y2)
        
        # 스트로커를 사용하여 경로를 넓힘
        from PyQt6.QtGui import QPainterPathStroker
        stroker = QPainterPathStroker()
        stroker.setWidth(15)  # 선택 영역 너비 (충분히 넓게)
        
        # 실제 그려지는 선의 경로(직선/지그재그)를 기반으로 확장
        # 단, create_zigzag_path 로직을 중복 호출하는 대신 현재 path()를 사용할 수도 있으나,
        # update_line에서 setPath를 하므로 self.path()가 이미 설정되어 있음.
        
        return stroker.createStroke(self.path())

    def itemChange(self, change, value):
        """아이템 변경 이벤트"""
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            # 선택 상태에 따라 핸들 표시/숨김
            is_selected = self.isSelected()
            if self.start_handle:
                self.start_handle.setVisible(is_selected)
            if self.end_handle:
                self.end_handle.setVisible(is_selected)
        
        return super().itemChange(change, value)
    
    def paint(self, painter, option, widget=None):
        """페인팅 (선택 표시 제거)"""
        # 선택 시 점선 테두리 제거 - PyQt6 호환성
        from PyQt6.QtWidgets import QStyle
        option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, option, widget)

