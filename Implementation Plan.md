감정 관계선 (Emotional Relationship Lines) 구현 계획
이 문서는 familytree_v1.3 beta 버전에 존재했던 감정 관계선 기능을 현재 familytree 프로젝트에 복원 및 통합하기 위한 단계별 구현 계획입니다.

1. 개요 및 목표
목표: 사용자 정의 가능한 6가지 유형의 감정 관계선 추가 (친밀/소원/갈등 × 양방향/일방향).
동작 방식: 인물 노드와 독립적으로 작동하는 자유 드로잉 방식 (절대 좌표 기반).
주요 기능: 생성, 드래그 이동, 길이/방향 조절(핸들), 저장/불러오기.
2. 세부 구현 단계
단계 1: 데이터 모델 및 Core 클래스 구현
가진 기본 데이터 구조와 그래픽 아이템 클래스를 먼저 작성합니다.

models.py
 수정

RelationshipLine
 데이터클래스 정의.
속성: 
id
 (str), lineType (str), x1, y1, x2, y2 (float).
to_dict
, 
from_dict
 메서드 구현.
relationship_line_item.py
 파일 생성 (신규)

QGraphicsPathItem을 상속받는 
RelationshipLineItem
 클래스 구현.
핸들(Handle) 구현: 선의 양 끝점에 드래그 가능한 핸들(작은 원) 추가.
스타일링 로직:
친밀(Intimate): 실선 (SolidLine)
소원(Distant): 점선 (DashLine)
갈등(Conflict): 지그재그선 (Zigzag path 알고리즘 적용)
이벤트 처리: 마우스 클릭 및 드래그 이벤트 (
mousePress
, 
mouseMove
, 
mouseRelease
) 처리.
단계 2: 데이터베이스 스키마 확장
관계선 데이터를 영구 저장하기 위해 데이터베이스 구조를 변경합니다.

database.py
 수정
create_tables
 메서드: RelationshipLines 테이블 생성 쿼리 추가.
컬럼: 
id
, tree_name (FK), line_id, line_type, x1, y1, x2, y2.
save_tree
 메서드: RelationshipLines 테이블에 데이터 저장 로직 추가.
load_tree
 메서드: RelationshipLines 테이블에서 데이터 로드하고 
RelationshipLine
 객체 리스트 반환하도록 수정.
단계 3: 캔버스 위젯 통합
캔버스(화면)에서 관계선을 그리고 관리하는 로직을 추가합니다.

canvas_widget.py
 수정
relationship_lines
 리스트 관리.
create_relationship_line
 메서드 구현: 화면 중앙에 새 선 생성.
draw_emotional_relationship_lines
 메서드 구현: 
RelationshipLineItem
을 씬(Scene)에 추가.
delete_selected_relationship_line
 메서드 구현: 선택된 선 삭제.
단계 4: UI 및 사용자 인터랙션 연결
메인 윈도우에 사용자가 기능을 사용할 수 있는 버튼과 인터페이스를 추가합니다.

main.py
 수정
UI 추가: 캔버스 상단 또는 측면에 "관계선 툴바" 영역 생성.
버튼 구성: 6개 버튼 (친밀/소원/갈등 × 양방향/일방향) 배치 및 스타일링.
이벤트 연결: 버튼 클릭 시 
create_relationship_line
 호출.
삭제 기능: Delete 키 이벤트 핸들러(
keyPressEvent
)에 관계선 삭제 로직 연결.
저장/로드 연동: 
save_current_tree
 및 
load_selected_tree
 호출 시 관계선 데이터 포함.
3. 검증 계획 (Verification)
구현 후 다음 항목을 테스트하여 기능을 검증합니다.

생성: 6가지 버튼 클릭 시 각각 올바른 스타일(색상, 선 모양, 화살표)의 선이 생성되는가?
조작:
선 자체를 드래그하여 이동 가능한가?
양 끝점을 드래그하여 길이와 방향이 변경되는가?
지그재그: 갈등 관계선이 지그재그 형태로 올바르게 그려지는가?
저장/로드: 프로그램을 껐다 켜도 그린 선들이 정확한 위치와 모양으로 복원되는가?
삭제: 선택 후 Delete 키로 삭제되는가?