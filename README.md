# 🚀 ZOA (Zotero-Obsidian-AI Summary)

> **Zotero × Obsidian × 다중 AI(Gemini, Claude, OpenAI, DeepSeek) 연동 학술 논문 자동 요약 파이프라인**  
> 로컬 Zotero 라이브러리에서 논문을 가져와 PDF 본문을 추출하고, 사용자가 선택한 최신 AI 모델(Gemini, Claude, OpenAI, DeepSeek)을 통해 핵심 요약 노트를 생성한 뒤, 옵시디언(Obsidian) 보관소에 위키링크(`[[...]]`)를 포함한 마크다운 문서로 자동 저장해 주는 편리하고 강력한 프로그램입니다.

---

## 📋 시작 전 준비물 (Prerequisites)

ZOA를 사용하려면 아래 준비물들이 필요합니다.

| 준비물 | 용도 | 비고 |
|--------|------|------|
| [Zotero](https://www.zotero.org/) | 논문 라이브러리 관리 | PDF 저장 플러그인으로 [Zotmoov](https://github.com/wileyyugioh/zotmoov) 사용 권장 |
| [Obsidian](https://obsidian.md/) | 요약 노트 저장 및 열람 | 무료 |
| **AI API Key** | AI 요약 생성 | **Gemini, Claude, OpenAI, DeepSeek** 중 **최소 하나** 필요 |

> 💡 **Zotmoov 권장 이유**: Zotero에 추가한 논문 PDF를 지정한 폴더에 자동으로 정리해 주는 플러그인입니다. ZOA가 PDF를 찾을 때 이 폴더를 참조하므로, Zotmoov로 PDF를 한 폴더에 모아두면 전체 본문 기반 요약 정확도가 높아집니다.

---

## 📥 다운로드 및 실행 (Download)

**[⬇️ 최신 버전 다운로드 받기](../../releases/latest)**

| 운영체제 | 파일 | 비고 |
|----------|------|------|
| Windows | `ZOA.exe` | 더블클릭으로 즉시 실행 |
| macOS | `ZOA-macOS.zip` | 압축 해제 후 `ZOA.app` 실행 |

* 별도의 Python 설치나 개발 환경 세팅 없이 파일 하나만으로 즉시 작동합니다.
* **Windows**: 처음 실행 시 "Windows의 PC 보호" 보안 경고가 뜰 수 있습니다. **추가 정보 → 실행** 을 클릭하면 됩니다.
* **macOS**: 처음 실행 시 "개발자를 확인할 수 없음" 경고가 뜰 수 있습니다. `ZOA.app`을 **우클릭 → 열기**로 실행하면 됩니다.

---

## ⚡ 빠른 시작 (Quick Start)

### 1단계. 전용 폴더 만들기
`ZOA.exe` (또는 `ZOA.app`)를 **별도의 빈 폴더**에 넣어주세요. (예: `문서/ZOA/`)

> ⚠️ 첫 실행 시 설정 파일(`.env`)이 실행 파일과 **같은 폴더에 자동 생성**됩니다. 바탕화면이나 다운로드 폴더에 그냥 두면 설정 파일이 섞이므로, 반드시 전용 폴더를 만들어 넣어주세요.

### 2단계. API Key 준비
활용하고 싶은 서비스의 API 키를 준비합니다.
* [Google AI Studio](https://aistudio.google.com/app/apikey) (Gemini)
* [Anthropic Console](https://console.anthropic.com/) (Claude)
* [OpenAI Platform](https://platform.openai.com/) (GPT)
* [DeepSeek Platform](https://platform.deepseek.com/) (DeepSeek V3 / R1)

### 3단계. 앱 실행 및 설정 마법사 진행
실행 파일을 더블클릭하면 첫 실행 시 **설정 마법사(Setup Wizard)**가 나타납니다.  
가지고 계신 API 키를 자유롭게 입력하고 (최소 1개 필수) 폴더 경로들을 선택하면 세팅 완료!

*모든 설정 정보는 인터넷에 업로드되지 않고, 실행 파일이 있는 폴더의 `.env` 파일로 오직 내 컴퓨터에만 저장됩니다.*

---

## 🛠️ 주요 기능 (Features)

| 기능 | 설명 |
|---|---|
| **설정 마법사 제공** | 처음 실행할 때 API 키들과 폴더 경로를 GUI 창으로 쉽게 입력 가능 |
| **다중 AI 연동 및 모델 자동 전환** | **Google, Anthropic, OpenAI, DeepSeek**를 모두 지원하며, 제공사를 변경하면 해당 제공사의 최신 모델 목록(gpt-5.5, claude-opus-4-7, deepseek-reasoner 등)이 동적으로 갱신됩니다. |
| **Zotero 컬렉션 선택** | 내 로컬 Zotero의 폴더 구조(Collection)를 실시간 검색하고 체크박스로 다중 선택 가능 |
| **로컬 DB 직접 조회** | 온라인 싱크 대기 없이 로컬 SQLite DB를 직접 읽어 즉각적으로 논문 정보 조회 |
| **지능형 PDF 매칭** | 저자, 발행 연도, 제목 키워드를 조합하여 내 컴퓨터에 저장된 논문 PDF 본문을 자동 매칭 |
| **지능형 논문 전체 요약** | 논문 전체 본문을 기반으로 연구 목적, 방법론, 핵심 결과, 주요 기여점 등을 정밀 분석 요약 |
| **자동 위키링크 연결** | 요약 노트 내의 저자, 학술지, 태그, 키워드를 `[[위키링크]]` 형태로 변환해 옵시디언 지식 그래프 구축 |
| **중복 처리 및 필터링** | 이미 요약된 논문 건너뛰기/덮어쓰기 기능 및 '최근 N일 이내에 추가된 논문만 처리' 필터 제공 |
| **실시간 진행률 표시** | 실시간 상태 로그 및 진행바(Progress Bar)를 통해 요약 진행 상황을 직관적으로 확인 |

---

## 📂 저장되는 요약 노트 구조 (Markdown)

옵시디언으로 내보내지는 마크다운 노트는 아래와 같이 옵시디언의 기능을 100% 활용할 수 있는 깔끔한 템플릿 구조를 따릅니다.

```markdown
---
title: "논문 제목"
authors:
  - Last, First
date: 2026
journal: "학술지명"
has_pdf: true
zotero_link: zotero://select/items/0_XXXXXXXX
---

# 논문 제목 (Title)

## Bibliographic Info
- **Authors**: Last, First
- **Journal**: 학술지명
- **Date**: 2026
- **Zotero Link**: [Open in Zotero](zotero://select/items/0_XXXXXXXX)
- **PDF Status**: PDF Found
- **Zotero Tags**: 태그1, 태그2
- **URL**: https://...

## 🤖 AI 핵심 요약 (Summary)
> (선택한 AI가 PDF 전체 텍스트 또는 초록을 기반으로 작성한 상세 연구 목적, 방법론, 핵심 결과, 한계점 및 향후 연구 방향이 정돈되어 기록됩니다.)

## 📝 원문 초록 (Abstract)
> (Zotero에 등록되어 있는 영문/국문 원문 초록이 그대로 보존됩니다.)
```

---

## ❓ 자주 묻는 질문 (FAQ)

**Q. Zotmoov가 반드시 필요한가요?**  
아닙니다. Zotmoov 없이도 ZOA는 정상 작동합니다. 다만 Zotmoov를 사용하면 Zotero에 추가한 논문 PDF가 지정한 폴더에 자동으로 정리되기 때문에, ZOA가 PDF를 찾는 성공률이 크게 높아집니다. Zotmoov가 없거나 PDF를 찾지 못한 경우에는 Zotero에 등록된 초록(Abstract)을 기반으로 요약이 생성됩니다.

**Q. API 사용 비용이 발생하나요?**  
각 인공지능 제공업체 정책에 따라 무료 한도 제공 혹은 사용량 비례 과금이 발생할 수 있습니다. 각 서비스 공식 홈페이지에서 정확한 API 요금제 및 크레딧 제공 정책을 확인하시는 것을 추천해 드립니다.

**Q. Zotero SQLite 파일 위치를 모릅니다.**  
설정 마법사의 해당 항목을 비워두면 됩니다. Zotero를 기본 위치에 설치했다면 ZOA가 자동으로 감지합니다. Zotero를 커스텀 경로에 설치한 경우에만 직접 경로를 입력하면 됩니다.

---

## 🔒 개인정보 및 보안 (Security & Privacy)

* **안전한 로컬 저장**: 사용자의 API Key들과 설정 경로는 외부 서버에 절대 전송되지 않고, 실행 파일 옆에 `.env` 파일로 **오직 사용자 로컬에만 저장**됩니다.
* **안전한 통신**: 논문 텍스트는 오직 사용자가 지정한 공식 AI 제공사 API 서버로의 직접 통신을 통해서만 전송되며, 그 외의 제3자 서버나 마케팅 목적으로는 공유되거나 수집되지 않습니다.

---

## 📝 버전 기록 (Version History)

* **v1.0 (ZOA 정식 릴리즈)**
  * 기존 GOZ 파이프라인 전면 개편 및 다중 API 연동 구조 구현
  * Google Gemini, Anthropic Claude, OpenAI, DeepSeek 4대 인공지능 엔진 종합 지원
  * 제공사 변경 시 적용 가능한 최신 모델로 동적 콤보박스 전환 연동
  * 파이썬 표준 라이브러리(urllib) 기반 REST 클라이언트 적용으로 패키징 최적화 및 경량화 성공

---

## 🐛 버그 제보 및 기능 건의 (Support)

ZOA 앱을 사용하시던 중 버그가 발생하거나 기능 개선이 필요하다면 아래의 이슈 링크를 통해 제보해 주세요.
* **[에러 및 피드백 제보하기 (GitHub Issues)](https://github.com/idlhy0218/GOZ-gemini-obsidian-zotero/issues)**
* *제보 시 에러가 발생한 화면 스크린샷과 앱 하단 **Execution Log**의 내용을 함께 적어주시면 더욱 빠른 해결이 가능합니다!*
