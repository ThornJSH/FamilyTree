# GitHub 버전관리 설정 가이드

## 1단계: Git 설치 (필수)

### Git 다운로드 및 설치
1. https://git-scm.com/download/win 접속
2. "Click here to download" 클릭하여 Git 설치 프로그램 다운로드
3. 설치 프로그램 실행
4. 기본 설정으로 "Next" 클릭하여 설치 완료

### 설치 확인
PowerShell을 **새로 열어서** 다음 명령어 실행:
```bash
git --version
```
- 버전 정보가 나오면 설치 성공

---

## 2단계: Git 초기 설정

### 사용자 정보 설정 (최초 1회만)
```bash
git config --global user.name "ThornJSH"
git config --global user.email "redcry@gmail.com"
```

**예시:**
```bash
git config --global user.name "Gyo"
git config --global user.email "gyo@example.com"
```

---

## 3단계: Git 저장소 초기화

### familytree 폴더로 이동
```bash
cd c:\Users\Gyo\Documents\Project\familytree
```

### Git 저장소 초기화
```bash
git init
```

### 파일 추가 및 첫 커밋
```bash
# 모든 파일 추가 (.gitignore에 의해 불필요한 파일은 자동 제외됨)
git add .

# 첫 커밋 생성
git commit -m "Initial commit: Family Tree Desktop Application v0.42"
```

---

## 4단계: GitHub 저장소 생성

### GitHub 웹사이트에서
1. https://github.com 접속 및 로그인
2. 오른쪽 상단 "+" 클릭 → "New repository" 선택
3. Repository 정보 입력:
   - **Repository name**: `FamilTree` (또는 원하는 이름)
   - **Description**: `오프라인 가계도 그리기 데스크톱 애플리케이션`
   - **Public** 또는 **Private** 선택
   - ⚠️ **"Initialize this repository with"는 모두 체크 해제** (이미 로컬에 코드가 있으므로)
4. "Create repository" 클릭

---

## 5단계: GitHub에 코드 업로드

### GitHub 저장소 연결
생성된 저장소 페이지에서 표시되는 명령어 사용:

```bash
# 원격 저장소 추가 (YOUR-USERNAME을 본인 GitHub 계정으로 변경)
git remote add origin https://github.com/YOUR-USERNAME/family-tree-desktop.git

# 메인 브랜치 이름 설정
git branch -M main

# 코드 업로드
git push -u origin main
```

**예시:**
```bash
git remote add origin https://github.com/Gyo/family-tree-desktop.git
git branch -M main
git push -u origin main
```

### 로그인 요청 시
- GitHub 사용자명과 비밀번호 입력
- 또는 Personal Access Token 사용 (권장)

---

## 이후 변경사항 업로드 (일상적인 사용)

### 코드 수정 후 GitHub에 업로드
```bash
# 변경된 파일 확인
git status

# 모든 변경사항 추가
git add .

# 커밋 메시지와 함께 커밋
git commit -m "수정 내용 설명"

# GitHub에 업로드
git push
```

**예시:**
```bash
git add .
git commit -m "Save prompt 기능 추가"
git push
```

---

## 유용한 Git 명령어

### 상태 확인
```bash
git status          # 현재 상태 확인
git log --oneline   # 커밋 기록 간단히 보기
```

### 변경사항 되돌리기
```bash
git diff            # 변경 내용 확인
git restore 파일명   # 특정 파일 변경 취소
```

### 다른 PC에서 코드 받기
```bash
# 처음 받을 때
git clone https://github.com/YOUR-USERNAME/family-tree-desktop.git

# 이후 업데이트 받을 때
git pull
```

---

## 문제 해결

### "fatal: not a git repository"
- `git init`을 실행하지 않았거나 잘못된 폴더에 있음
- familytree 폴더로 이동 후 `git init` 실행

### "Permission denied" 또는 로그인 실패
- Personal Access Token 사용 권장
- GitHub 설정 → Developer settings → Personal access tokens → Generate new token

### .gitignore가 작동하지 않음
- 이미 추적 중인 파일은 제외되지 않음
- 다음 명령어로 캐시 삭제:
```bash
git rm -r --cached .
git add .
git commit -m "Apply .gitignore"
```

---

## 요약: 빠른 시작

```bash
# 1. Git 설치 (git-scm.com에서)

# 2. 사용자 정보 설정
git config --global user.name "이름"
git config --global user.email "이메일"

# 3. 저장소 초기화 및 첫 커밋
cd c:\Users\Gyo\Documents\Project\familytree
git init
git add .
git commit -m "Initial commit"

# 4. GitHub에서 저장소 생성 후

# 5. 연결 및 업로드
git remote add origin https://github.com/계정명/저장소명.git
git branch -M main
git push -u origin main
```

---

**이제 GitHub으로 버전관리를 시작할 수 있습니다!** 🚀
