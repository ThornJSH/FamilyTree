"""
메인 애플리케이션
"""
import sys
import time
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QCheckBox, QListWidget,
    QMessageBox, QFileDialog, QFrame, QScrollArea, QGroupBox, QRadioButton,
    QButtonGroup, QStatusBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from models import Person
from database import Database
from canvas_widget import CanvasWidget
from image_export import ImageExporter
from config import (
    NODE_WIDTH, NODE_HEIGHT, SIBLING_SPACING, LEVEL_SPACING,
    PRIMARY_COLOR, BACKGROUND_COLOR, APP_NAME, TEXT_COLOR, DANGER_COLOR
)


class MainWindow(QMainWindow):
    """메인 윈도우"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setGeometry(100, 100, 1280, 720)
        
        # 데이터
        self.db = Database()
        self.people = []
        self.history_stack = []
        self.current_tree_name = None
        self.initial_client = None
        
        # UI 초기화
        self.init_ui()
        
        # 저장된 가계도 목록 불러오기
        self.load_tree_list()
    
    def init_ui(self):
        """UI 구성"""
        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃 (왼쪽 패널 + 오른쪽 캔버스)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 왼쪽 정보 패널
        self.create_info_panel(main_layout)
        
        # 오른쪽 캔버스 영역
        self.create_canvas_area(main_layout)
        
        # 상태 표시줄
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status("정보를 입력하여 가계도를 그려보세요.")
        
        # 푸터 레이블 추가
        footer_label = QLabel("welfareact.net에서 제작·배포합니다.")
        footer_label.setStyleSheet("color: #666; padding: 0 10px;")
        self.status_bar.addPermanentWidget(footer_label)
        
        # 스타일 적용
        self.apply_styles()
    
    def create_info_panel(self, parent_layout):
        """왼쪽 정보 패널 생성"""
        panel = QFrame()
        panel.setFixedWidth(320)
        panel.setStyleSheet(f"background-color: white; border-right: 1px solid #E0E6ED;")
        
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)
        
        # 스크롤 영역
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(20, 20, 20, 20)
        scroll_layout.setSpacing(15)
        
        # 헤더
        header = QLabel(f"<h1 style='color: {PRIMARY_COLOR};'>가계도 그리기</h1>")
        scroll_layout.addWidget(header)
        
        # 섹션 1: 새 가계도 시작
        self.create_new_tree_section(scroll_layout)
        
        # 섹션 2: 주변인물 추가 (초기에 숨김)
        self.create_add_person_section(scroll_layout)
        
        # 섹션 3: 인물 정보 수정 (초기에 숨김)
        self.create_edit_person_section(scroll_layout)
        
        # 섹션 4: 저장된 가계도 목록
        self.create_tree_list_section(scroll_layout)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        panel_layout.addWidget(scroll)
        
        parent_layout.addWidget(panel)
    
    def create_new_tree_section(self, parent_layout):
        """새 가계도 시작 섹션"""
        group = QGroupBox("새 가계도 시작")
        layout = QVBoxLayout(group)
        
        # 가계도 이름
        layout.addWidget(QLabel("가계도 이름"))
        self.tree_name_input = QLineEdit()
        self.tree_name_input.setPlaceholderText("예: 우리 가족")
        layout.addWidget(self.tree_name_input)
        
        # 중심인물 이름
        layout.addWidget(QLabel("중심인물 이름"))
        self.client_name_input = QLineEdit()
        self.client_name_input.setPlaceholderText("이름 입력")
        layout.addWidget(self.client_name_input)
        
        # 출생연도
        layout.addWidget(QLabel("출생연도"))
        self.client_birthyear_input = QLineEdit()
        self.client_birthyear_input.setPlaceholderText("예: 1985")
        layout.addWidget(self.client_birthyear_input)
        
        # 성별
        layout.addWidget(QLabel("성별"))
        self.client_gender_select = QComboBox()
        self.client_gender_select.addItems(["남자", "여자"])
        layout.addWidget(self.client_gender_select)
        
        # 시작 버튼
        start_btn = QPushButton("▶ 새로 시작하기")
        start_btn.setMinimumHeight(40)
        start_btn.clicked.connect(self.start_new_tree)
        layout.addWidget(start_btn)
        
        parent_layout.addWidget(group)
    
    def create_add_person_section(self, parent_layout):
        """주변인물 추가 섹션"""
        self.add_person_group = QGroupBox("주변인물 추가")
        self.add_person_group.setVisible(False)
        layout = QVBoxLayout(self.add_person_group)
        
        # 기준 인물
        layout.addWidget(QLabel("기준 인물"))
        self.center_person_select = QComboBox()
        layout.addWidget(self.center_person_select)
        
        # 이름
        layout.addWidget(QLabel("이름"))
        self.person_name_input = QLineEdit()
        self.person_name_input.setPlaceholderText("이름 입력")
        layout.addWidget(self.person_name_input)
        
        # 출생연도
        layout.addWidget(QLabel("출생연도"))
        self.person_birthyear_input = QLineEdit()
        self.person_birthyear_input.setPlaceholderText("예: 1988 (선택)")
        layout.addWidget(self.person_birthyear_input)
        
        # 성별
        layout.addWidget(QLabel("성별"))
        self.person_gender_select = QComboBox()
        self.person_gender_select.addItems(["남자", "여자"])
        layout.addWidget(self.person_gender_select)
        
        # 관계
        layout.addWidget(QLabel("관계"))
        self.relationship_select = QComboBox()
        self.relationship_select.addItem("배우자 (결혼)", "spouse")
        self.relationship_select.addItem("이혼", "divorce")
        self.relationship_select.addItem("별거", "separation")
        self.relationship_select.addItem("동거인 (사실혼)", "cohabitant")
        self.relationship_select.addItem("자녀", "child")
        self.relationship_select.addItem("입양 자녀", "adoptedChild")
        self.relationship_select.addItem("반려동물", "petChild")
        self.relationship_select.addItem("부모", "parent")
        self.relationship_select.addItem("형제/자매", "sibling")
        self.relationship_select.addItem("일란성 다태아", "identicalMultipleBirth")
        self.relationship_select.addItem("이란성 다태아", "fraternalMultipleBirth")
        layout.addWidget(self.relationship_select)
        
        # 사망 여부
        self.deceased_checkbox = QCheckBox("사망 여부")
        layout.addWidget(self.deceased_checkbox)
        
        # 추가 버튼
        add_btn = QPushButton("👤 인물 추가")
        add_btn.setMinimumHeight(40)
        add_btn.clicked.connect(self.add_person)
        layout.addWidget(add_btn)
        
        parent_layout.addWidget(self.add_person_group)
    
    def create_edit_person_section(self, parent_layout):
        """인물 정보 수정 섹션"""
        self.edit_person_group = QGroupBox("인물 정보 수정")
        self.edit_person_group.setVisible(False)
        layout = QVBoxLayout(self.edit_person_group)
        
        # 이름
        layout.addWidget(QLabel("이름"))
        self.edit_name_input = QLineEdit()
        layout.addWidget(self.edit_name_input)
        
        # 출생연도
        layout.addWidget(QLabel("출생연도"))
        self.edit_birthyear_input = QLineEdit()
        layout.addWidget(self.edit_birthyear_input)
        
        # 성별
        layout.addWidget(QLabel("성별"))
        self.edit_gender_select = QComboBox()
        self.edit_gender_select.addItems(["남자", "여자"])
        layout.addWidget(self.edit_gender_select)
        
        # 사망 여부
        self.edit_deceased_checkbox = QCheckBox("사망 여부")
        layout.addWidget(self.edit_deceased_checkbox)
        
        # 버튼들
        btn_layout = QHBoxLayout()
        
        update_btn = QPushButton("수정 적용")
        update_btn.setMinimumHeight(35)
        update_btn.clicked.connect(self.update_person_info)
        btn_layout.addWidget(update_btn)
        
        delete_btn = QPushButton("삭제")
        delete_btn.setObjectName("dangerButton")
        delete_btn.setMinimumHeight(35)
        delete_btn.clicked.connect(self.delete_selected_person)
        btn_layout.addWidget(delete_btn)
        
        layout.addLayout(btn_layout)
        
        parent_layout.addWidget(self.edit_person_group)
    
    def create_tree_list_section(self, parent_layout):
        """저장된 가계도 목록 섹션"""
        group = QGroupBox("저장된 가계도 목록")
        layout = QVBoxLayout(group)
        
        # 목록
        self.tree_list_widget = QListWidget()
        self.tree_list_widget.setMaximumHeight(150)
        layout.addWidget(self.tree_list_widget)
        
        # 버튼들
        btn_layout = QHBoxLayout()
        
        load_btn = QPushButton("📂 불러오기")
        load_btn.setObjectName("secondaryButton")
        load_btn.setMinimumHeight(35)
        load_btn.clicked.connect(self.load_selected_tree)
        btn_layout.addWidget(load_btn)
        
        delete_btn = QPushButton("🗑 선택 삭제")
        delete_btn.setObjectName("dangerButton")
        delete_btn.setMinimumHeight(35)
        delete_btn.clicked.connect(self.delete_selected_tree)
        btn_layout.addWidget(delete_btn)
        
        layout.addLayout(btn_layout)
        
        parent_layout.addWidget(group)
    
    def create_canvas_area(self, parent_layout):
        """오른쪽 캔버스 영역"""
        canvas_container = QWidget()
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        canvas_layout.setSpacing(0)
        
        # 상단 컨트롤 버튼
        controls = QFrame()
        controls.setStyleSheet("background-color: white; border-bottom: 1px solid #E0E6ED;")
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(10, 10, 10, 10)
        controls_layout.setSpacing(8)
        
        save_btn = QPushButton("💾 저장")
        save_btn.setMinimumHeight(30)
        save_btn.setToolTip("현재 가계도 저장")
        save_btn.clicked.connect(self.save_current_tree)
        controls_layout.addWidget(save_btn)
        
        undo_btn = QPushButton("↶ 실행취소")
        undo_btn.setObjectName("secondaryButton")
        undo_btn.setMinimumHeight(30)
        undo_btn.setToolTip("마지막 작업 취소")
        undo_btn.clicked.connect(self.undo_last_action)
        controls_layout.addWidget(undo_btn)
        
        reset_btn = QPushButton("🗑 초기화")
        reset_btn.setObjectName("secondaryButton")
        reset_btn.setMinimumHeight(30)
        reset_btn.setToolTip("캔버스 초기화")
        reset_btn.clicked.connect(self.reset_canvas)
        controls_layout.addWidget(reset_btn)
        
        controls_layout.addStretch()
        
        save_jpg_btn = QPushButton("📷 JPG 저장")
        save_jpg_btn.setObjectName("secondaryButton")
        save_jpg_btn.setMinimumHeight(30)
        save_jpg_btn.setToolTip("JPG로 저장")
        save_jpg_btn.clicked.connect(lambda: self.save_image('jpg'))
        controls_layout.addWidget(save_jpg_btn)
        
        save_png_btn = QPushButton("🖼 PNG 저장")
        save_png_btn.setObjectName("secondaryButton")
        save_png_btn.setMinimumHeight(30)
        save_png_btn.setToolTip("PNG로 저장")
        save_png_btn.clicked.connect(lambda: self.save_image('png'))
        controls_layout.addWidget(save_png_btn)
        
        canvas_layout.addWidget(controls)
        
        # 캔버스
        # 캔버스
        # 캔버스
        self.canvas = CanvasWidget()
        self.canvas.person_selected.connect(self.on_person_selected)
        canvas_layout.addWidget(self.canvas)
        
        parent_layout.addWidget(canvas_container)
    
    def apply_styles(self):
        """스타일 적용 - 기본 스타일 사용"""
        # 버튼 스타일을 제거하여 시스템 기본값(텍스트 보임)을 사용하도록 함
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {BACKGROUND_COLOR};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
            QLineEdit, QComboBox {{
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }}
            QListWidget {{
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }}
        """)

    def start_new_tree(self):
        """새 가계도 시작"""
        try:
            name = self.client_name_input.text().strip()
            birth_year = self.client_birthyear_input.text().strip()
            gender = "male" if self.client_gender_select.currentText() == "남자" else "female"
            tree_name = self.tree_name_input.text().strip()
            
            if not tree_name or not name:
                QMessageBox.warning(self, "입력 오류", "가계도 이름과 중심인물 이름은 필수입니다.")
                return
            
            # 상태 초기화
            self.reset_state()
            self.current_tree_name = tree_name
            self.update_status(f'새 가계도 "{self.current_tree_name}" 작업을 시작합니다.')
            
            # 중심 인물 생성 (화면 중앙)
            person = Person(
                id=f"p{int(time.time() * 1000)}",
                name=name,
                birthYear=birth_year if birth_year else None,
                gender=gender,
                isDeceased=False,
                nodeType='person',
                x=0,
                y=0
            )
            
            self.initial_client = person
            self.people.append(person)
            self.save_state_for_undo()
            
            # UI 업데이트
            self.add_person_group.setVisible(True)
            self.update_center_person_select()
            
            self.canvas.draw_tree(self.people)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "치명적 오류", f"작업 중 오류가 발생했습니다:\n{str(e)}")
            person = Person(
                id=f"p{int(time.time() * 1000)}",
                name=name,
                birthYear=birth_year if birth_year else None,
                gender=gender,
                isDeceased=False,
                nodeType='person',
                x=0,
                y=0
            )
            
            self.initial_client = person
            self.people.append(person)
            self.save_state_for_undo()
            
            # UI 업데이트
            self.add_person_group.setVisible(True)
            self.update_center_person_select()
            self.canvas.draw_tree(self.people)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "치명적 오류", f"작업 중 오류가 발생했습니다:\n{str(e)}")
    
    def add_person(self):
        """주변 인물 추가"""
        center_person_id = self.center_person_select.currentData()
        name = self.person_name_input.text().strip()
        birth_year = self.person_birthyear_input.text().strip()
        gender = "male" if self.person_gender_select.currentText() == "남자" else "female"
        relationship_type = self.relationship_select.currentData()
        is_deceased = self.deceased_checkbox.isChecked()
        
        if not center_person_id or not name:
            QMessageBox.warning(self, "입력 오류", "기준 인물과 이름은 필수입니다.")
            return
        
        self.save_state_for_undo()
        
        center_person = self.find_person_by_id(center_person_id)
        new_person = Person(
            id=f"p{int(time.time() * 1000)}",
            name=name,
            birthYear=birth_year if birth_year else None,
            isDeceased=is_deceased,
            x=center_person.x,
            y=center_person.y,
            nodeType='pet' if relationship_type == 'petChild' else 'person',
            gender='pet' if relationship_type == 'petChild' else gender
        )
        
        # 관계에 따른 위치 및 관계 설정
        self.setup_relationship(new_person, center_person, relationship_type)
        
        self.people.append(new_person)
        self.canvas.draw_tree(self.people)
        self.update_center_person_select()
        
        # 입력 필드 초기화
        self.person_name_input.clear()
        self.person_birthyear_input.clear()
        self.deceased_checkbox.setChecked(False)
    
    def on_person_selected(self, person: Person):
        """인물 선택 시 처리"""
        if not person:
            self.edit_person_group.setVisible(False)
            self.add_person_group.setVisible(True)
            return
            
        self.selected_person_id = person.id
        self.edit_person_group.setVisible(True)
        # 수정 모드일 때는 추가 모드 숨김 (선택 사항)
        # self.add_person_group.setVisible(False)
        
        # 정보 채우기
        self.edit_name_input.setText(person.name)
        self.edit_birthyear_input.setText(person.birthYear or "")
        self.edit_gender_select.setCurrentText("남자" if person.gender == "male" else "여자")
        self.edit_deceased_checkbox.setChecked(person.isDeceased)
    
    def update_person_info(self):
        """인물 정보 수정 적용"""
        if not hasattr(self, 'selected_person_id') or not self.selected_person_id:
            return
            
        person = self.find_person_by_id(self.selected_person_id)
        if not person:
            return
            
        name = self.edit_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "입력 오류", "이름은 필수입니다.")
            return
            
        self.save_state_for_undo()
        
        person.name = name
        person.birthYear = self.edit_birthyear_input.text().strip() or None
        person.gender = "male" if self.edit_gender_select.currentText() == "남자" else "female"
        person.isDeceased = self.edit_deceased_checkbox.isChecked()
        
        self.canvas.draw_tree(self.people)
        self.update_center_person_select()
        self.update_status(f"{name}님의 정보를 수정했습니다.")
        
    def delete_selected_person(self):
        """선택된 인물 삭제 (버튼용)"""
        if not hasattr(self, 'selected_person_id') or not self.selected_person_id:
            return
            
        if self.initial_client and self.selected_person_id == self.initial_client.id:
            QMessageBox.warning(self, "삭제 오류", "중심인물은 삭제할 수 없습니다.")
            return
            
        reply = QMessageBox.question(
            self, '삭제 확인',
            '정말로 이 인물을 삭제하시겠습니까?\n연결된 관계도 함께 정리됩니다.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 삭제 로직을 메인 윈도우에서 직접 처리
            person_id = self.selected_person_id
            
            # 1. 다른 노드들의 참조 정리
            for p in self.people:
                if p.nextIdenticalSiblingId == person_id:
                    p.nextIdenticalSiblingId = None
                if p.parentId == person_id:
                    p.parentId = None
                if p.spouseId == person_id:
                    p.spouseId = None
            
            # 2. 리스트에서 제거
            self.people = [p for p in self.people if p.id != person_id]
            
            # 3. 상태 저장 및 UI 업데이트
            self.save_state_for_undo()
            self.canvas.draw_tree(self.people)
            self.update_center_person_select()
            self.edit_person_group.setVisible(False)
            self.add_person_group.setVisible(True)
            self.selected_person_id = None
            self.update_status("선택한 인물을 삭제했습니다.")
    
    def setup_relationship(self, new_person: Person, center_person: Person, rel_type: str):
        """관계에 따른 위치 및 속성 설정"""
        if rel_type in ['spouse', 'cohabitant', 'divorce', 'separation']:
            # 배우자 관계
            new_person.spouseId = center_person.id
            center_person.spouseId = new_person.id
            center_person.relationshipType = rel_type
            new_person.relationshipType = rel_type
            new_person.x = center_person.x + NODE_WIDTH + SIBLING_SPACING
            new_person.y = center_person.y
        
        elif rel_type == 'parent':
            # 부모 추가
            current_parent_id = center_person.parentId
            real_parent = self.find_person_by_id(current_parent_id) if current_parent_id else None
            
            if real_parent:
                # 이미 실존하는 부모가 있는 경우 -> 두 번째 부모(배우자) 추가
                new_person.spouseId = real_parent.id
                real_parent.spouseId = new_person.id
                new_person.relationshipType = 'spouse'
                real_parent.relationshipType = 'spouse'
                new_person.x = real_parent.x + NODE_WIDTH + SIBLING_SPACING
                new_person.y = real_parent.y
            elif current_parent_id:
                # 부모 ID는 있지만 실존하지 않는 경우 -> 가상 부모였음
                # 가상 부모를 공유하던 모든 형제들의 부모를 새 부모로 업데이트
                siblings = [p for p in self.people if p.parentId == current_parent_id]
                for sibling in siblings:
                    sibling.parentId = new_person.id
                
                # 새 부모 위치 설정 (형제들 중앙 상단)
                if siblings:
                    siblings.sort(key=lambda p: p.x)
                    center_x = (siblings[0].x + siblings[-1].x) / 2
                    new_person.x = center_x
                else:
                    new_person.x = center_person.x
                new_person.y = center_person.y - LEVEL_SPACING
            else:
                # 부모가 아예 없던 경우 -> 첫 부모
                center_person.parentId = new_person.id
                new_person.x = center_person.x
                new_person.y = center_person.y - LEVEL_SPACING
        
        elif rel_type in ['child', 'adoptedChild', 'petChild']:
            # 자녀 추가
            new_person.parentId = center_person.id
            new_person.relationshipType = rel_type
            new_person.y = center_person.y + LEVEL_SPACING
            
            # 같은 부모의 자녀들 찾기
            children = [p for p in self.people if p.parentId == center_person.id or 
                       (p.parentId and self.find_person_by_id(p.parentId) and 
                        self.find_person_by_id(p.parentId).spouseId == center_person.id)]
            
            if children:
                children.sort(key=lambda p: p.x)
                new_person.x = children[-1].x + NODE_WIDTH + SIBLING_SPACING
            else:
                # 첫 자녀는 부모(들) 중앙 아래
                spouse = self.find_person_by_id(center_person.spouseId) if center_person.spouseId else None
                new_person.x = (center_person.x + spouse.x) / 2 if spouse else center_person.x
        
        elif rel_type == 'sibling':
            # 형제자매
            if not center_person.parentId:
                # 부모가 없는 경우 가상의 부모 ID 생성하여 묶음
                virtual_parent_id = f"v_parent_{int(time.time() * 1000)}"
                center_person.parentId = virtual_parent_id
            
            new_person.parentId = center_person.parentId
            new_person.y = center_person.y
            new_person.x = center_person.x + NODE_WIDTH + SIBLING_SPACING
        
        elif rel_type in ['fraternalMultipleBirth', 'identicalMultipleBirth']:
            # 다태아
            if not center_person.parentId:
                # 부모가 없는 경우 가상의 부모 ID 생성하여 묶음
                virtual_parent_id = f"v_parent_{int(time.time() * 1000)}"
                center_person.parentId = virtual_parent_id
            
            new_person.parentId = center_person.parentId
            
            group_id = center_person.multipleBirthGroupId or f"mb{int(time.time() * 1000)}"
            new_person.multipleBirthGroupId = group_id
            center_person.multipleBirthGroupId = group_id
            
            if rel_type == 'identicalMultipleBirth':
                center_person.nextIdenticalSiblingId = new_person.id
            
            # 그룹 내 마지막 멤버 찾기
            group_members = [p for p in self.people if p.multipleBirthGroupId == group_id]
            if group_members:
                group_members.sort(key=lambda p: p.x)
                new_person.x = group_members[-1].x + NODE_WIDTH + SIBLING_SPACING
            else:
                new_person.x = center_person.x + NODE_WIDTH + SIBLING_SPACING
            
            new_person.y = center_person.y
    
    def save_current_tree(self):
        """현재 가계도 저장"""
        if not self.current_tree_name:
            QMessageBox.warning(self, "저장 오류", "저장할 가계도의 이름이 없습니다. 새로 시작하거나 기존 가계도를 불러오세요.")
            return
        
        if not self.people:
            QMessageBox.warning(self, "저장 오류", "저장할 내용이 없습니다.")
            return
        
        result = self.db.save_tree(self.current_tree_name, self.people)
        QMessageBox.information(self, "저장", result)
        self.load_tree_list()
    
    def load_selected_tree(self):
        """선택된 가계도 불러오기"""
        current_item = self.tree_list_widget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "선택 오류", "불러올 가계도를 목록에서 선택해주세요.")
            return
        
        tree_name = current_item.text()
        people = self.db.load_tree(tree_name)
        
        self.reset_state()
        self.people = people
        self.current_tree_name = tree_name
        self.tree_name_input.setText(tree_name)
        
        if self.people:
            # 초기 클라이언트 찾기 (부모도 배우자도 없는 사람)
            self.initial_client = next((p for p in self.people if not p.parentId and not p.spouseId), self.people[0])
        
        self.save_state_for_undo()
        self.add_person_group.setVisible(True)
        self.update_center_person_select()
        self.canvas.draw_tree(self.people)
        self.update_status(f'"{self.current_tree_name}" 가계도를 불러왔습니다.')
    
    def delete_selected_tree(self):
        """선택된 가계도 삭제"""
        current_item = self.tree_list_widget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "선택 오류", "삭제할 가계도를 목록에서 선택해주세요.")
            return
        
        tree_name = current_item.text()
        reply = QMessageBox.question(
            self, '삭제 확인',
            f'"{tree_name}" 가계도를 정말로 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            result = self.db.delete_tree(tree_name)
            QMessageBox.information(self, "삭제", result)
            self.load_tree_list()
    
    def load_tree_list(self):
        """저장된 가계도 목록 불러오기"""
        self.tree_list_widget.clear()
        tree_names = self.db.get_tree_list()
        self.tree_list_widget.addItems(tree_names)
    
    def reset_canvas(self):
        """캔버스 초기화"""
        reply = QMessageBox.question(
            self, '초기화 확인',
            '정말로 현재 가계도를 모두 지우시겠습니까?\n저장되지 않은 변경사항은 사라집니다.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.reset_state()
            self.canvas.draw_tree(self.people)
            self.add_person_group.setVisible(False)
            self.tree_name_input.clear()
            self.client_name_input.clear()
            self.client_birthyear_input.clear()
            self.update_status("캔버스가 초기화되었습니다.")
    
    def undo_last_action(self):
        """마지막 작업 취소"""
        if len(self.history_stack) > 1:
            self.history_stack.pop()
            last_state = self.history_stack[-1]
            self.people = [Person.from_dict(p) for p in last_state]
            self.canvas.draw_tree(self.people)
            self.update_center_person_select()
            self.update_status("마지막 작업을 취소했습니다.")
        else:
            self.update_status("더 이상 취소할 작업이 없습니다.")
    
    def save_image(self, format: str):
        """이미지로 저장"""
        if not self.people:
            QMessageBox.warning(self, "저장 오류", "저장할 내용이 없습니다.")
            return
        
        file_filter = f"{format.upper()} Files (*.{format})"
        default_name = f"{self.current_tree_name or 'family-tree'}.{format}"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"{format.upper()}로 저장", default_name, file_filter
        )
        
        if file_path:
            image = ImageExporter.export_to_image(self.canvas.scene, self.people, format)
            if image:
                image.save(file_path)
                QMessageBox.information(self, "저장 완료", f"이미지가 저장되었습니다:\n{file_path}")
    
    def update_center_person_select(self):
        """기준 인물 콤보박스 업데이트"""
        current_selection = self.center_person_select.currentData()
        self.center_person_select.clear()
        
        for person in self.people:
            if person.nodeType == 'person':
                self.center_person_select.addItem(person.name, person.id)
        
        # 이전 선택 복원 또는 첫 번째 선택
        if current_selection:
            index = self.center_person_select.findData(current_selection)
            if index >= 0:
                self.center_person_select.setCurrentIndex(index)
    
    def find_person_by_id(self, person_id: str) -> Person:
        """ID로 인물 찾기"""
        if not person_id:
            return None
        for person in self.people:
            if person.id == person_id:
                return person
        return None
    
    def reset_state(self):
        """상태 초기화"""
        self.people = []
        self.history_stack = []
        self.current_tree_name = None
        self.initial_client = None
    
    def save_state_for_undo(self):
        """실행 취소를 위한 상태 저장"""
        state = [p.to_dict() for p in self.people]
        self.history_stack.append(state)
        if len(self.history_stack) > 20:
            self.history_stack.pop(0)
    
    def update_status(self, message: str):
        """상태 표시줄 업데이트"""
        self.status_bar.showMessage(message)
    
    def keyPressEvent(self, event):
        """키 입력 이벤트"""
        if event.key() == Qt.Key.Key_Delete:
            # Delete 키로 선택된 노드 삭제
            self.delete_selected_person()
        
        super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """창 닫기 이벤트"""
        # 저장되지 않은 변경사항이 있는지 확인
        if self.people:
            reply = QMessageBox.question(
                self,
                '저장 확인',
                '변경사항을 저장하시겠습니까?',
                QMessageBox.StandardButton.Yes | 
                QMessageBox.StandardButton.No | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # 저장 후 종료
                self.save_tree()
                self.db.close()
                event.accept()
            elif reply == QMessageBox.StandardButton.No:
                # 저장하지 않고 종료
                self.db.close()
                event.accept()
            else:
                # 취소 - 종료하지 않음
                event.ignore()
        else:
            # 데이터가 없으면 바로 종료
            self.db.close()
            event.accept()


def main():
    """메인 함수"""
    app = QApplication(sys.argv)
    
    # 폰트 설정 제거 (시스템 기본 폰트 사용)
    # font = QFont("Segoe UI", 10)
    # font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    # app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
