# 새 PC에서 가계도 프로젝트 설정하기

## 1단계: 파일 복사

### 필수 파일만 복사 (최소 구성)
다음 파일들을 새 PC로 복사하세요:
```
familytree/
├── main.py
├── canvas_widget.py
├── person_node.py
├── database.py
├── models.py
├── image_export.py
├── config.py
├── requirements.txt
└── familytree.db          # 기존 데이터가 있다면
```

> **참고**: `.venv`, `__pycache__` 폴더는 복사하지 마세요 (자동 생성됩니다)

## 2단계: 새 PC에서 환경 설정

### Python 설치 확인
```bash
python --version
```
- Python 3.8 이상이 설치되어 있어야 합니다

### 가상환경 생성
```bash
# familytree 폴더로 이동
cd familytree

# 가상환경 생성
python -m venv .venv
```

### 가상환경 활성화
```bash
# Windows
.venv\Scripts\activate

# 활성화되면 프롬프트 앞에 (.venv)가 표시됩니다
```

### 패키지 설치
```bash
pip install -r requirements.txt
```

## 3단계: 실행

```bash
python main.py
```

## 빠른 명령어 (순서대로 실행)

```bash
# 1. 가상환경 생성
python -m venv .venv

# 2. 가상환경 활성화
.venv\Scripts\activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 프로그램 실행
python main.py
```

## 데이터 보존

- `familytree.db` 파일을 복사하면 기존 가계도 데이터가 그대로 유지됩니다
- 복사하지 않으면 빈 상태에서 새로 시작합니다

## 문제 해결

### 가상환경 활성화 오류
PowerShell 실행 정책 오류가 나면:
```bash
# 직접 Python으로 실행
c:\...\familytree\.venv\Scripts\python.exe main.py
```

### 패키지 설치 오류
```bash
# pip 업그레이드 후 재시도
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

**이제 새 PC에서도 동일하게 작업할 수 있습니다!** 🎉
