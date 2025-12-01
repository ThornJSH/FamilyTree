"""
SQLite 데이터베이스 관리 모듈
"""
import sqlite3
from typing import List, Optional
from models import Person
from config import DB_PATH


class Database:
    """SQLite 데이터베이스 연결 및 테이블 관리"""
    
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """데이터베이스 연결"""
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def create_tables(self):
        """필요한 테이블 생성"""
        # 가계도 메타데이터 테이블
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS FamilyTrees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tree_name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 인물 데이터 테이블
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS People (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tree_name TEXT NOT NULL,
                person_id TEXT NOT NULL,
                name TEXT NOT NULL,
                birth_year TEXT,
                gender TEXT,
                is_deceased INTEGER DEFAULT 0,
                node_type TEXT DEFAULT 'person',
                x REAL DEFAULT 0,
                y REAL DEFAULT 0,
                parent_id TEXT,
                spouse_id TEXT,
                relationship_type TEXT,
                multiple_birth_group_id TEXT,
                next_identical_sibling_id TEXT,
                FOREIGN KEY (tree_name) REFERENCES FamilyTrees(tree_name) ON DELETE CASCADE
            )
        ''')
        
        self.conn.commit()
    
    def get_tree_list(self) -> List[str]:
        """모든 가계도 이름 목록 조회"""
        self.cursor.execute('SELECT tree_name FROM FamilyTrees ORDER BY tree_name')
        return [row['tree_name'] for row in self.cursor.fetchall()]
    
    def save_tree(self, tree_name: str, people: List[Person]):
        """가계도 저장 (덮어쓰기)"""
        try:
            # 가계도 메타데이터 삽입/갱신
            self.cursor.execute('''
                INSERT OR IGNORE INTO FamilyTrees (tree_name) VALUES (?)
            ''', (tree_name,))
            
            # 기존 인물 데이터 삭제
            self.cursor.execute('DELETE FROM People WHERE tree_name = ?', (tree_name,))
            
            # 새 인물 데이터 삽입
            for person in people:
                self.cursor.execute('''
                    INSERT INTO People (
                        tree_name, person_id, name, birth_year, gender,
                        is_deceased, node_type, x, y, parent_id, spouse_id,
                        relationship_type, multiple_birth_group_id, next_identical_sibling_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    tree_name, person.id, person.name, person.birthYear, person.gender,
                    1 if person.isDeceased else 0, person.nodeType, person.x, person.y,
                    person.parentId, person.spouseId, person.relationshipType,
                    person.multipleBirthGroupId, person.nextIdenticalSiblingId
                ))
            
            self.conn.commit()
            return f'"{tree_name}" 가계도가 성공적으로 저장되었습니다.'
        except Exception as e:
            self.conn.rollback()
            return f'저장 중 오류가 발생했습니다: {str(e)}'
    
    def load_tree(self, tree_name: str) -> List[Person]:
        """가계도 불러오기"""
        self.cursor.execute('''
            SELECT * FROM People WHERE tree_name = ?
        ''', (tree_name,))
        
        people = []
        for row in self.cursor.fetchall():
            person = Person(
                id=row['person_id'],
                name=row['name'],
                birthYear=row['birth_year'],
                gender=row['gender'],
                isDeceased=bool(row['is_deceased']),
                nodeType=row['node_type'],
                x=row['x'],
                y=row['y'],
                parentId=row['parent_id'],
                spouseId=row['spouse_id'],
                relationshipType=row['relationship_type'],
                multipleBirthGroupId=row['multiple_birth_group_id'],
                nextIdenticalSiblingId=row['next_identical_sibling_id']
            )
            people.append(person)
        
        return people
    
    def delete_tree(self, tree_name: str) -> str:
        """가계도 삭제"""
        try:
            # People 테이블에서 먼저 삭제 (외래키 제약조건)
            self.cursor.execute('DELETE FROM People WHERE tree_name = ?', (tree_name,))
            
            # FamilyTrees 테이블에서 삭제
            self.cursor.execute('DELETE FROM FamilyTrees WHERE tree_name = ?', (tree_name,))
            
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return f'"{tree_name}" 가계도를 삭제했습니다.'
            else:
                return '삭제할 가계도를 찾지 못했습니다.'
        except Exception as e:
            self.conn.rollback()
            return f'삭제 중 오류가 발생했습니다: {str(e)}'
    
    def close(self):
        """데이터베이스 연결 종료"""
        if self.conn:
            self.conn.close()
