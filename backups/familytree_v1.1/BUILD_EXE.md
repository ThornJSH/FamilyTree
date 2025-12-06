# 실행 파일 만들기 가이드

이 문서는 Python 코드를 Windows 실행 파일(.exe)로 변환하는 방법을 설명합니다.

## PyInstaller 설치

```bash
pip install pyinstaller
```

## 기본 실행 파일 생성

### 단일 파일로 생성 (권장)

```bash
pyinstaller --onefile --windowed --name="가계도그리기" main.py
```

### 옵션 설명
- `--onefile`: 모든 파일을 하나의 .exe 파일로 묶음
- `--windowed`: 콘솔 창 없이 실행 (GUI 앱용)
- `--name="가계도그리기"`: 실행 파일 이름 지정

## 고급 옵션

### 아이콘 추가 (선택사항)

먼저 .ico 파일을 준비한 후:

```bash
pyinstaller --onefile --windowed --icon=icon.ico --name="가계도그리기" main.py
```

### 더 작은 파일 크기

```bash
pyinstaller --onefile --windowed --name="가계도그리기" --strip --upx-dir=upx main.py
```

## 생성된 파일 위치

```
familytree/
├── build/              # 임시 빌드 파일 (삭제 가능)
├── dist/               # 최종 실행 파일
│   └── 가계도그리기.exe  # 이 파일을 배포
└── 가계도그리기.spec     # PyInstaller 설정 파일
```

## 배포하기

1. `dist/가계도그리기.exe` 파일을 복사
2. 다른 컴퓨터로 전달
3. 더블클릭으로 실행

> **참고**: 실행 파일은 Python이 설치되지 않은 컴퓨터에서도 작동합니다.

## 데이터베이스 파일

실행 파일을 처음 실행하면 `familytree.db` 파일이 자동으로 생성됩니다.
이 파일은 실행 파일과 같은 폴더에 위치합니다.

## 문제 해결

### 실행 파일 크기가 큼
- PyInstaller는 필요한 모든 라이브러리를 포함시키므로 파일이 클 수 있습니다 (약 100-200MB)
- 이는 정상이며, Python 런타임이 포함된 것입니다

### 바이러스 경고
- PyInstaller로 만든 파일은 때때로 백신 프로그램에서 오탐할 수 있습니다
- 이는 흔한 현상이며, 신뢰할 수 있는 출처임을 확인하세요

### 시작 시간이 느림
- `--onefile` 옵션을 사용하면 시작할 때 임시 폴더에 압축을 풀어야 하므로 약간 느릴 수 있습니다
- 더 빠른 시작을 원하면 `--onefile` 옵션을 제거하세요 (대신 여러 파일이 생성됨)

## 빠른 명령어

```bash
# 1. PyInstaller 설치
pip install pyinstaller

# 2. 실행 파일 생성
pyinstaller --onefile --windowed --name="가계도그리기" main.py

# 3. 생성된 파일 확인
dir dist

# 4. 실행 테스트
dist\가계도그리기.exe
```

## 결과

성공적으로 생성되면 `dist` 폴더에 `가계도그리기.exe` 파일이 생성됩니다.
이 파일 하나만 있으면 어떤 Windows 컴퓨터에서도 실행할 수 있습니다!

---

**이제 인터넷 연결 없이 어디서나 가계도를 그릴 수 있습니다!** 🎉
