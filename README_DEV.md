# 🛠️ GOZ (Gemini-Obsidian-Zotero) — 개발자 가이드 (Developer Guide)

이 문서는 **GOZ** 프로그램의 소스 코드를 실행, 수정하거나 새로운 `.exe` 실행 파일로 직접 빌드하려는 개발자를 위한 안내서입니다.

---

## 📂 프로젝트 구조 (Project Structure)

프로젝트 루트 폴더에는 다음과 같은 핵심 파일들이 존재합니다.

```
zotero-obsidian-summarizer/
├── goz.py            # 핵심 Python 소스 코드 (Tkinter GUI 및 비즈니스 로직)
├── GOZ.bat           # [Git 제외] 로컬 소스 코드를 즉시 실행하기 위한 배치 파일
├── app_icon.ico      # 실행 파일 빌드에 사용되는 테마 아이콘 (책 + AI 별빛)
├── README.md         # 배포용 일반 사용자 설명서
├── README_DEV.md     # 본 개발자 문서
├── .env.template     # 로컬 개발 환경용 설정값 템플릿
├── .gitignore        # 소스 코드 유출 및 API 키 업로드 방지를 위한 제외 설정
└── dist/
    └── GOZ.exe       # [Git 제외] 최종 배포용 윈도우 실행 파일
```

> ⚠️ **보안 참고사항**: 본 프로젝트를 퍼블릭 깃허브(GitHub) 등에 배포할 때 소스 코드 보안을 유지하기 위해 핵심 코드인 `goz.py`, 로컬 구동용 배치 파일인 `GOZ.bat`, 설정 파일인 `.env` 등은 `.gitignore`에 등록되어 Git 추적에서 제외되어 있습니다.

---

## 💻 개발 환경 구축 (Prerequisites)

이 프로그램은 Python 환경에서 실행됩니다. 개발 및 코드를 직접 수정해 보려면 아래 패키지 설치가 필요합니다.

### 1. 의존성 라이브러리 설치 (Dependencies)
Python이 설치된 환경의 터미널(PowerShell 등)에서 아래 명령어를 실행하여 필수 의존성 패키지를 설치합니다.

```bash
pip install google-generativeai pypdf pillow
```

* **`google-generativeai`**: Google Gemini AI 모델 연동용 API 라이브러리
* **`pypdf`**: PDF 본문 텍스트 추출용 라이브러리
* **`pillow`**: 아이콘 파일(`.ico`) 변환 및 이미지 처리용 라이브러리
* **`sqlite3`, `tkinter`**: 파이썬 표준 라이브러리 (별도 설치 불필요)

---

## 🚀 로컬 소스 코드 실행하기 (Run from Source)

코드 수정 사항을 빌드 없이 실시간으로 테스트하고 싶다면 아래 방법으로 소스 코드를 즉시 실행할 수 있습니다.

### 방법 A. 배치 파일로 실행 (간편함)
프로젝트 폴더 내의 **`GOZ.bat`** 파일을 더블클릭합니다.
* 내부적으로 내 PC 환경에 설치된 Python 실행기(`python` 또는 `py` 런처)를 감지하여 자동으로 `goz.py`를 실행해 줍니다.

### 방법 B. 명령어로 실행
PowerShell 또는 CMD 창에서 프로젝트 폴더로 이동한 뒤 아래 명령어를 직접 실행합니다.
```powershell
py goz.py
# 또는
python goz.py
```

---

## 📦 실행 파일(.exe) 빌드 가이드 (Build Executable)

소스를 수정한 뒤, 다른 사람들이 단일 파일로 손쉽게 쓸 수 있도록 **`GOZ.exe`** 파일로 최종 패키징하는 방법입니다.

실행 파일 패키징에는 **`PyInstaller`** 라이브러리가 사용됩니다. 

### 1. 빌드 도구 설치
```bash
pip install pyinstaller
```

### 2. 빌드 명령어 실행 (캐시 초기화 포함)
윈도우 탐색기 캐시 및 PyInstaller 내부 빌드 캐시 간섭을 방지하기 위해 반드시 **`--clean`** 옵션을 적용하여 아래 명령어를 실행해 주세요.

#### 💡 내 컴퓨터에서의 빌드 명령어 (Python core 경로 명시)
```powershell
& "C:\Users\User\AppData\Local\Python\pythoncore-3.14-64\Scripts\pyinstaller.exe" --clean --onefile --windowed --name "GOZ" --icon="app_icon.ico" goz.py
```

#### 🌐 일반적인 환경에서의 빌드 명령어 (환경변수 PATH 등록 기준)
```powershell
pyinstaller --clean --onefile --windowed --name "GOZ" --icon="app_icon.ico" goz.py
```

### 3. 빌드 완료 후 청소
빌드가 성공적으로 완료되면 폴더 내에 생겨난 임시 작업물들을 지워 깨끗한 상태로 복원해 줍니다.
* **임시 폴더 삭제**: `build` 폴더를 통째로 삭제합니다.
* **설정 파일 삭제**: `GOZ.spec` 파일을 삭제합니다.
* **결과물 확인**: 오직 **`dist/GOZ.exe`** 파일만 남겨두시면 됩니다.
