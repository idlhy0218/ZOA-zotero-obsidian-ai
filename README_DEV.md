# 🛠️ ZOA (Zotero-Obsidian-AI Summary) — 개발자 가이드

이 문서는 ZOA 소스 코드를 수정하고 새 버전으로 배포하는 전체 과정을 설명합니다.

---

## 📂 프로젝트 구조

```
GOZ-gemini-obsidian-zotero/
├── zoa.py                          # 핵심 소스 코드 (GUI + 비즈니스 로직)
├── ZOA.bat                         # 로컬 실행용 배치 파일 (더블클릭으로 zoa.py 실행)
├── app_icon.ico                    # Windows 빌드용 아이콘
├── .env.template                   # 설정 파일 템플릿 (실제 .env는 .gitignore로 제외됨)
├── .gitignore                      # .env, dist/, build/ 등 제외
├── README.md                       # 일반 사용자용 설명서
├── README_DEV.md                   # 본 개발자 문서
└── .github/
    └── workflows/
        └── build.yml               # GitHub Actions 자동 빌드 워크플로우
```

> `.env` 파일은 다양한 API 키들이 포함될 수 있으므로 절대 커밋하지 않습니다.  
> `dist/`, `build/` 폴더는 빌드 결과물로, GitHub Actions가 자동 생성하므로 커밋 불필요합니다.

---

## 1단계. 개발 환경 세팅 (최초 1회)

### Python 패키지 설치

```powershell
pip install google-generativeai pypdf pillow pyinstaller
```
> 💡 **의존성 경량화 안내**: ZOA는 **Claude, OpenAI, DeepSeek** 연동의 경우 파이썬 표준 라이브러리(`urllib.request`, `json`)를 활용해 커스텀 REST 클라이언트를 내장하고 있습니다. 따라서 구글 Gemini 모델을 전혀 활용하지 않는 사용자의 경우 `google-generativeai` 패키지 설치를 건너뛰어도 무방합니다.

### .env 파일 생성

`.env.template`을 복사해서 `.env`로 저장한 뒤, 자신의 경로와 보유하신 API 키들을 입력합니다.

```
GEMINI_KEY=구글_Gemini_API_키 (선택)
CLAUDE_KEY=앤트로픽_Claude_API_키 (선택)
OPENAI_KEY=오픈AI_API_키 (선택)
DEEPSEEK_KEY=딥시크_API_키 (선택)
API_PROVIDER=gemini (기본 제공사 설정: gemini / claude / openai / deepseek)
PDF_PATH=C:\Users\...\Zotero\storage
OBS_PATH=C:\Users\...\Obsidian Vault\Papers
ZOTERO_DB=C:\Users\...\Zotero\zotero.sqlite
MODEL_NAME=gemini-2.5-flash (기본 모델 설정)
```

---

## 2단계. 코드 수정 후 로컬 테스트

`zoa.py`를 수정한 뒤, 빌드 없이 바로 실행해서 테스트합니다.

**방법 A — 배치 파일로 실행 (간편)**

`ZOA.bat` 더블클릭

**방법 B — 터미널로 실행**

```powershell
python zoa.py
```

---

## 3단계. GitHub Desktop으로 push

1. GitHub Desktop 열기
2. 왼쪽에 변경된 파일 확인
3. 하단 Summary에 커밋 메시지 입력 → **Commit to main**
4. 상단 **Push origin** 클릭

---

## 4단계. 배포 — GitHub 웹에서 Release 생성

push만 해서는 빌드가 실행되지 않습니다. Release를 만들어야 Actions가 자동으로 시작됩니다.

1. GitHub 저장소 페이지 오른쪽 **Releases** 클릭
2. **Draft a new release** 클릭
3. **Choose a tag** 클릭 → 새 버전 입력 (예: `v1.0`) → **Create new tag** 클릭
   - ⚠️ 태그는 반드시 `v`로 시작해야 합니다 (`v1.0` O, `1.0` X)
   - ⚠️ 기존에 동일한 태그명이 원격 서버에 이미 등록되어 있다면 빌드가 무시되거나 트리거되지 않으므로, 충돌 시 기존 원격 태그를 깃허브 웹(또는 `git push origin :refs/tags/v1.0` 명령어)으로 깔끔히 삭제하고 릴리즈를 새로 만드셔야 합니다.
4. Release 제목, 변경사항 간단히 작성
5. **Publish release** 클릭

Publish 버튼을 누르는 순간 GitHub Actions가 자동으로 감지해서 빌드를 시작합니다.

5~10분 후 `ZOA.exe`와 `ZOA-macOS.zip`이 Release에 자동으로 첨부됩니다.

---

## 5단계. 빌드 진행 확인

GitHub 저장소 페이지 → **Actions 탭**

| 상태 | 의미 |
|------|------|
| 🟡 노란 원 | 빌드 진행 중 |
| ✅ 초록 체크 | 빌드 성공, Release에 파일 첨부 완료 |
| ❌ 빨간 X | 빌드 실패 — 클릭해서 에러 로그 확인 |

---

## 빌드 실패 시 확인 방법

Actions 탭 → 실패한 항목 클릭 → 빨간 단계 클릭 → 에러 메시지 확인

자주 발생하는 오류:

| 오류 | 원인 | 해결 |
|------|------|------|
| `ModuleNotFoundError` | `pip install` 목록에 패키지 누락 | `build.yml`의 Install dependencies 단계에 패키지 추가 |
| Mac 빌드 실패 | Tkinter 관련 오류 | `macos-latest` → `macos-13`으로 변경 시도 |

---

## (선택) 테스트 빌드 — 릴리즈 없이 빌드만 확인

Release를 만들기 전에 빌드가 잘 되는지 먼저 확인하고 싶을 때:

1. GitHub 저장소 → **Actions 탭**
2. 왼쪽 목록에서 **Build ZOA** 클릭
3. **Run workflow** 버튼 클릭 → **Run workflow** 실행

빌드 완료 후 해당 실행 항목 클릭 → 하단 **Artifacts**에서 파일 다운로드 가능합니다.

---

## (선택) 로컬에서 직접 빌드

GitHub Actions 없이 내 컴퓨터에서 직접 `.exe`를 빌드할 수 있습니다.

```powershell
pyinstaller --clean --onefile --windowed --name "ZOA" --icon="app_icon.ico" zoa.py
```

> 내 컴퓨터 PyInstaller 경로가 다른 경우:
> ```powershell
> & "C:\Users\User\AppData\Local\Python\pythoncore-3.14-64\Scripts\pyinstaller.exe" --clean --onefile --windowed --name "ZOA" --icon="app_icon.ico" zoa.py
> ```

빌드 후 `dist/ZOA.exe`만 남기고 `build/`, `ZOA.spec`은 삭제해도 됩니다.

---

## 의존 패키지 요약

| 패키지 | 용도 |
|--------|------|
| `google-generativeai` | Gemini API 연동 (Gemini 기능 사용 시에만 필요) |
| `pypdf` | PDF 텍스트 추출 |
| `pillow` | 아이콘 처리 (로컬 빌드 시 필요) |
| `pyinstaller` | 실행 파일 패키징 (로컬 빌드 시 필요) |
| `sqlite3`, `tkinter`, `urllib`, `json` | Python 기본 내장 (별도 설치 불필요) |
