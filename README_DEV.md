# 🛠️ GOZ (Gemini-Obsidian-Zotero) — 개발자 가이드

이 문서는 GOZ 소스 코드를 수정하고 새 버전으로 배포하는 전체 과정을 설명합니다.

---

## 📂 프로젝트 구조

```
GOZ-gemini-obsidian-zotero/
├── goz.py                          # 핵심 소스 코드 (GUI + 비즈니스 로직)
├── GOZ.bat                         # 로컬 실행용 배치 파일 (더블클릭으로 goz.py 실행)
├── app_icon.ico                    # Windows 빌드용 아이콘
├── .env.template                   # 설정 파일 템플릿 (실제 .env는 .gitignore로 제외됨)
├── .gitignore                      # .env, dist/, build/ 등 제외
├── README.md                       # 일반 사용자용 설명서
├── README_DEV.md                   # 본 개발자 문서
└── .github/
    └── workflows/
        └── build.yml               # GitHub Actions 자동 빌드 워크플로우
```

> `.env` 파일은 API 키가 포함되므로 절대 커밋하지 않습니다.  
> `dist/`, `build/` 폴더는 빌드 결과물로, GitHub Actions가 자동 생성하므로 커밋 불필요합니다.

---

## 1단계. 개발 환경 세팅 (최초 1회)

### Python 패키지 설치

```powershell
pip install google-generativeai pypdf pillow pyinstaller
```

### .env 파일 생성

`.env.template`을 복사해서 `.env`로 저장한 뒤, 자신의 경로와 API 키를 입력합니다.

```
GEMINI_KEY=여기에_API_키_입력
PDF_PATH=C:\Users\...\Zotero\storage
OBS_PATH=C:\Users\...\Obsidian Vault\Papers
ZOTERO_DB=C:\Users\...\Zotero\zotero.sqlite
```

---

## 2단계. 코드 수정 후 로컬 테스트

`goz.py`를 수정한 뒤, 빌드 없이 바로 실행해서 테스트합니다.

**방법 A — 배치 파일로 실행 (간편)**

`GOZ.bat` 더블클릭

**방법 B — 터미널로 실행**

```powershell
python goz.py
# 또는
py goz.py
```

로컬 테스트가 완료되면 커밋합니다.

```powershell
git add goz.py
git commit -m "변경 내용 간단히 설명"
git push origin main
```

---

## 3단계. 배포 — GitHub Actions 자동 빌드

코드를 main에 push하는 것만으로는 빌드가 실행되지 않습니다.  
**배포는 버전 태그를 push할 때** 자동으로 시작됩니다.

### 정식 릴리즈 (GOZ.exe + GOZ-macOS.zip 자동 생성)

```powershell
git tag v1.2
git push origin v1.2
```

태그를 push하면 GitHub Actions가 자동으로:
1. Windows VM과 Mac VM을 동시에 실행
2. 각각 `GOZ.exe`, `GOZ-macOS.zip` 빌드
3. GitHub Release 페이지에 두 파일 첨부

결과 확인: `저장소 페이지 → Releases`

### 테스트 빌드 (릴리즈 없이 빌드만 확인)

태그 없이 빌드 결과물만 확인하고 싶을 때는 GitHub Actions 탭에서 수동으로 실행합니다.

1. 저장소 페이지 → **Actions 탭**
2. 왼쪽 목록에서 **Build GOZ** 클릭
3. **Run workflow** 버튼 클릭 → **Run workflow** 실행
4. 빌드 완료 후 해당 실행 항목 클릭 → 하단 **Artifacts**에서 파일 다운로드

수동 실행 시에는 Release 페이지에 올라가지 않으며, 빌드 결과물은 90일 후 자동 삭제됩니다.

---

## 4단계. 빌드 실패 시 확인 방법

Actions 탭 → 실패한 항목 클릭 → 빨간 단계 클릭 → 에러 메시지 확인

자주 발생하는 오류:

| 오류 | 원인 | 해결 |
|------|------|------|
| `ModuleNotFoundError` | `pip install` 목록에 패키지 누락 | `build.yml`의 Install dependencies 단계에 패키지 추가 |
| `GitHub Releases requires a tag` | 수동 실행인데 release job이 실행됨 | 현재 워크플로우는 이미 수동 실행 시 release를 건너뜀 |
| Mac 빌드 실패 | Tkinter 관련 오류 | `macos-latest` → `macos-13`으로 변경 시도 |

---

## (선택) 로컬에서 직접 빌드

GitHub Actions 없이 내 컴퓨터에서 직접 `.exe`를 빌드할 수 있습니다.

```powershell
pyinstaller --clean --onefile --windowed --name "GOZ" --icon="app_icon.ico" goz.py
```

빌드 후 `dist/GOZ.exe`만 남기고 `build/`, `GOZ.spec`은 삭제해도 됩니다.

> 내 컴퓨터 PyInstaller 경로가 다른 경우:
> ```powershell
> & "C:\Users\User\AppData\Local\Python\pythoncore-3.14-64\Scripts\pyinstaller.exe" --clean --onefile --windowed --name "GOZ" --icon="app_icon.ico" goz.py
> ```

---

## 의존 패키지 요약

| 패키지 | 용도 |
|--------|------|
| `google-generativeai` | Gemini API 연동 |
| `pypdf` | PDF 텍스트 추출 |
| `pillow` | 아이콘 처리 (빌드 시 필요) |
| `pyinstaller` | 실행 파일 패키징 (빌드 시 필요) |
| `sqlite3`, `tkinter` | Python 기본 내장 (별도 설치 불필요) |
