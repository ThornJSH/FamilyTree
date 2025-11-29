"""
QGraphicsView 기반 캔버스 위젯
"""
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPen, QColor, QBrush, QPainterPath, QTransform, QPainter
from typing import List, Optional, Set
from models import Person
from person_node import PersonNode
from config import NODE_WIDTH, NODE_HEIGHT, TEXT_COLOR


class CanvasWidget(QGraphicsView):
    """가계도를 그리는 캔버스 위젯"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # 배경 그리드 설정
        self.setBackgroundBrush(QBrush(QColor("#F4F7F9")))
        
        # 뷰 설정
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        
        # 드래그 상태
        self.panning = False
        self.last_pan_point = QPointF()
        self.dragging_nodes = False
        self.dragged_group = []  # 다태아 그룹 드래그를 위한 리스트
        
        # 데이터
        self.people: List[Person] = []
        self.node_map = {}  # person.id -> PersonNode 매핑
    
    def wheelEvent(self, event):
        """마우스 휠로 줌 인/아웃"""
        zoom_factor = 1.1
        if event.angleDelta().y() > 0:
            self.scale(zoom_factor, zoom_factor)
        else:
            self.scale(1/zoom_factor, 1/zoom_factor)
    
    def mousePressEvent(self, event):
        """마우스 버튼 눌림"""
        if event.button() == Qt.MouseButton.MiddleButton or \
           (event.button() == Qt.MouseButton.LeftButton and event.modifiers() == Qt.KeyboardModifier.ShiftModifier):
            # 팬 모드 시작
            self.panning = True
            self.last_pan_point = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            # 노드 드래그 확인
            item = self.itemAt(event.pos())
            if isinstance(item, PersonNode) or (item and isinstance(item.parentItem(), PersonNode)):
                node = item if isinstance(item, PersonNode) else item.parentItem()
                self.dragging_nodes = True
                
                # 다태아 그룹인 경우 함께 드래그할 노드들 찾기
                self.dragged_group = [node]
                if node.person.multipleBirthGroupId:
                    group_id = node.person.multipleBirthGroupId
                    for person in self.people:
                        if person.multipleBirthGroupId == group_id and person.id != node.person.id:
                            other_node = self.node_map.get(person.id)
                            if other_node:
                                self.dragged_group.append(other_node)
            
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """마우스 이동"""
        if self.panning:
            # 캔버스 팬
            delta = event.pos() - self.last_pan_point
            self.last_pan_point = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """마우스 버튼 해제"""
        if self.panning:
            self.panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            self.dragging_nodes = False
            self.dragged_group = []
            super().mouseReleaseEvent(event)
    
    def draw_tree(self, people: List[Person]):
        """전체 가계도 그리기"""
        self.people = people
        # self.scene.clear()  # 잠재적 크래시 원인
        for item in self.scene.items():
            self.scene.removeItem(item)
        self.node_map.clear()
        
        if not people:
            return
        
        # 관계선 먼저 그리기 (노드 뒤에 표시)
        self.draw_relationship_lines()
        
        # 각 인물 노드 그리기
        for person in people:
            node = PersonNode(person)
            node.setPos(person.x, person.y)
            self.scene.addItem(node)
            self.node_map[person.id] = node
        
        # 씬 크기 조정
        self.scene.setSceneRect(self.scene.itemsBoundingRect().adjusted(-100, -100, 100, 100))
    
    def draw_relationship_lines(self):
        """관계선 그리기"""
        drawn_spouses = set()
        
        # 배우자 및 일란성 쌍둥이 연결선
        for person in self.people:
            # 배우자 연결선
            if person.spouseId and person.id not in drawn_spouses:
                spouse = self.find_person_by_id(person.spouseId)
                if spouse:
                    self.draw_spouse_line(person, spouse)
                    drawn_spouses.add(person.id)
                    drawn_spouses.add(spouse.id)
            
            # 일란성 쌍둥이 연결선
            if person.nextIdenticalSiblingId:
                next_sibling = self.find_person_by_id(person.nextIdenticalSiblingId)
                if next_sibling:
                    self.create_line(
                        person.x + NODE_WIDTH/2, person.y,
                        next_sibling.x - NODE_WIDTH/2, next_sibling.y
                    )
        
        # 부모-자녀 관계선
        children_by_parent = self.group_children_by_parent()
        for parent_id, siblings in children_by_parent.items():
            if not siblings:
                continue
            
            siblings.sort(key=lambda p: p.x)
            parent = self.find_person_by_id(parent_id)
            if not parent:
                continue
            
            parent_spouse = self.find_person_by_id(parent.spouseId) if parent.spouseId else None
            
            # 시작점 계산
            if parent_spouse:
                start_x = (parent.x + parent_spouse.x) / 2
                start_y = parent.y + (NODE_HEIGHT / 2) + 20
            else:
                start_x = parent.x
                start_y = parent.y + NODE_HEIGHT / 2
            
            # 자녀가 한 명일 경우
            if len(siblings) == 1:
                child = siblings[0]
                is_adopted = child.relationshipType == 'adoptedChild'
                self.create_line(start_x, start_y, start_x, child.y - NODE_HEIGHT/2, is_adopted)
                continue
            
            # 자녀가 여러 명일 경우
            sibling_bar_y = siblings[0].y - (NODE_HEIGHT / 2) - 45
            self.create_line(start_x, start_y, start_x, sibling_bar_y)
            
            # 다태아 그룹으로 나누기
            sibling_groups = []
            processed = set()
            for sibling in siblings:
                if sibling.id in processed:
                    continue
                if sibling.multipleBirthGroupId:
                    group = [s for s in siblings if s.multipleBirthGroupId == sibling.multipleBirthGroupId]
                    sibling_groups.append(group)
                    for member in group:
                        processed.add(member.id)
                else:
                    sibling_groups.append([sibling])
                    processed.add(sibling.id)
            
            # 그룹 간 수평선
            for i in range(len(sibling_groups) - 1):
                current_group = sibling_groups[i]
                next_group = sibling_groups[i + 1]
                start_point_x = (current_group[0].x + current_group[-1].x) / 2
                end_point_x = (next_group[0].x + next_group[-1].x) / 2
                self.create_line(start_point_x, sibling_bar_y, end_point_x, sibling_bar_y)
            
            # 각 그룹에서 자녀들로 V자 연결
            for group in sibling_groups:
                is_adopted = group[0].relationshipType == 'adoptedChild'
                connection_point_x = (group[0].x + group[-1].x) / 2
                top_connection_y = group[0].y - NODE_HEIGHT / 2
                v_point_y = sibling_bar_y + 1
                
                self.create_line(connection_point_x, sibling_bar_y, connection_point_x, v_point_y, is_adopted)
                
                for member in group:
                    self.create_line(connection_point_x, v_point_y, member.x, top_connection_y, is_adopted)
    
    def draw_spouse_line(self, p1: Person, p2: Person):
        """배우자 연결선 그리기"""
        marriage_line_y = p1.y + (NODE_HEIGHT / 2) + 20
        
        path = QPainterPath()
        path.moveTo(p1.x, p1.y + NODE_HEIGHT / 2)
        path.lineTo(p1.x, marriage_line_y)
        path.lineTo(p2.x, marriage_line_y)
        path.lineTo(p2.x, p2.y + NODE_HEIGHT / 2)
        
        pen = QPen(QColor(TEXT_COLOR), 1.5)
        
        rel_type = p1.relationshipType or p2.relationshipType
        if rel_type == 'cohabitant':
            pen.setStyle(Qt.PenStyle.DashLine)
        
        item = self.scene.addPath(path, pen)
        item.setZValue(-1)  # 노드 뒤에 표시
        
        # 이혼/별거 표시
        if rel_type in ['divorce', 'separation']:
            self.draw_marriage_marker(rel_type, p1, p2, marriage_line_y)
    
    def draw_marriage_marker(self, marker_type: str, p1: Person, p2: Person, y: float):
        """이혼/별거 마커 그리기"""
        mid_x = (p1.x + p2.x) / 2
        marker_height = 12
        half_height = marker_height / 2
        
        pen = QPen(QColor(TEXT_COLOR), 2)
        
        if marker_type == 'separation':  # 별거: 사선 1개
            line = self.scene.addLine(
                mid_x - 4, y + half_height,
                mid_x + 4, y - half_height,
                pen
            )
            line.setZValue(-1)
        elif marker_type == 'divorce':  # 이혼: 사선 2개
            spacing = 3
            line1 = self.scene.addLine(
                mid_x - spacing - 4, y + half_height,
                mid_x - spacing + 4, y - half_height,
                pen
            )
            line2 = self.scene.addLine(
                mid_x + spacing - 4, y + half_height,
                mid_x + spacing + 4, y - half_height,
                pen
            )
            line1.setZValue(-1)
            line2.setZValue(-1)
    
    def create_line(self, x1: float, y1: float, x2: float, y2: float, dashed: bool = False):
        """간단한 선 그리기"""
        pen = QPen(QColor(TEXT_COLOR), 1.5)
        if dashed:
            pen.setStyle(Qt.PenStyle.DashLine)
        
        line = self.scene.addLine(x1, y1, x2, y2, pen)
        line.setZValue(-1)  # 노드 뒤에 표시
    
    def group_children_by_parent(self):
        """부모별로 자녀 그룹화"""
        groups = {}
        for person in self.people:
            if person.parentId:
                parent = self.find_person_by_id(person.parentId)
                if parent:
                    # 부부가 있을 때, ID가 더 작은 쪽을 대표 부모로
                    main_parent_id = parent.id
                    if parent.spouseId and parent.spouseId < parent.id:
                        main_parent_id = parent.spouseId
                    
                    if main_parent_id not in groups:
                        groups[main_parent_id] = []
                    groups[main_parent_id].append(person)
        
        return groups
    
    def find_person_by_id(self, person_id: str) -> Optional[Person]:
        """ID로 인물 찾기"""
        if not person_id:
            return None
        for person in self.people:
            if person.id == person_id:
                return person
        return None
    
    def get_selected_person(self) -> Optional[Person]:
        """선택된 인물 가져오기"""
        selected_items = self.scene.selectedItems()
        for item in selected_items:
            if isinstance(item, PersonNode):
                return item.person
        return None
    
    def delete_selected_person(self, initial_client_id: str) -> bool:
        """선택된 인물 삭제"""
        person = self.get_selected_person()
        if not person:
            return False
        
        if person.id == initial_client_id:
            return False  # 중심인물은 삭제 불가
        
        # 다른 노드들의 참조 정리
        for p in self.people:
            if p.nextIdenticalSiblingId == person.id:
                p.nextIdenticalSiblingId = None
            if p.parentId == person.id:
                p.parentId = None
            if p.spouseId == person.id:
                p.spouseId = None
        
        # 배열에서 제거
        self.people = [p for p in self.people if p.id != person.id]
        
        # 다시 그리기
        self.draw_tree(self.people)
        return True
