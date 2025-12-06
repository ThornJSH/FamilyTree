"""
데이터 모델 클래스
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Person:
    """가계도의 인물을 나타내는 데이터 클래스"""
    id: str
    name: str
    birthYear: Optional[str] = None
    gender: str = "male"  # male, female, pet
    isDeceased: bool = False
    nodeType: str = "person"  # person, pet
    x: float = 0.0
    y: float = 0.0
    parentId: Optional[str] = None
    spouseId: Optional[str] = None
    relationshipType: Optional[str] = None  # spouse, divorce, separation, cohabitant, child, adoptedChild, petChild
    multipleBirthGroupId: Optional[str] = None
    nextIdenticalSiblingId: Optional[str] = None
    
    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            'id': self.id,
            'name': self.name,
            'birthYear': self.birthYear,
            'gender': self.gender,
            'isDeceased': self.isDeceased,
            'nodeType': self.nodeType,
            'x': self.x,
            'y': self.y,
            'parentId': self.parentId,
            'spouseId': self.spouseId,
            'relationshipType': self.relationshipType,
            'multipleBirthGroupId': self.multipleBirthGroupId,
            'nextIdenticalSiblingId': self.nextIdenticalSiblingId
        }
    
    @staticmethod
    def from_dict(data):
        """딕셔너리에서 Person 객체 생성"""
        return Person(
            id=data['id'],
            name=data['name'],
            birthYear=data.get('birthYear'),
            gender=data.get('gender', 'male'),
            isDeceased=data.get('isDeceased', False),
            nodeType=data.get('nodeType', 'person'),
            x=data.get('x', 0.0),
            y=data.get('y', 0.0),
            parentId=data.get('parentId'),
            spouseId=data.get('spouseId'),
            relationshipType=data.get('relationshipType'),
            multipleBirthGroupId=data.get('multipleBirthGroupId'),
            nextIdenticalSiblingId=data.get('nextIdenticalSiblingId')
        )


@dataclass
class RelationshipLine:
    """감정 관계선 데이터 클래스"""
    id: str
    lineType: str  # intimate-one, intimate-two, distant-one, distant-two, conflict-one, conflict-two
    x1: float
    y1: float
    x2: float
    y2: float

    def to_dict(self):
        return {
            'id': self.id,
            'lineType': self.lineType,
            'x1': self.x1,
            'y1': self.y1,
            'x2': self.x2,
            'y2': self.y2
        }

    @staticmethod
    def from_dict(data):
        return RelationshipLine(
            id=data['id'],
            lineType=data['lineType'],
            x1=data['x1'],
            y1=data['y1'],
            x2=data['x2'],
            y2=data['y2']
        )
