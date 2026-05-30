# ZOA (Zotero-Obsidian-AI Summary) v1.0-beta

> ## [최신 버전 다운로드 (ZOA.exe / ZOA-macOS.zip)](https://github.com/idlhy0218/ZOA-zotero-obsidian-ai/releases/latest)

Zotero, Obsidian, 그리고 다중 AI(Gemini, Claude, OpenAI, DeepSeek)를 연동하는 학술 논문 자동 요약 파이프라인입니다. 로컬 Zotero 라이브러리에서 논문 정보를 조회하고 PDF 본문을 추출하여, 선택한 AI 모델로 구조화된 요약 마크다운 문서를 생성한 후 Obsidian 보관소에 자동 저장합니다.

---

https://github.com/user-attachments/assets/fe30c80c-78e3-46b9-9714-18456d1b109a

---

## 준비물

| 준비물        | 용도                                                       |
| ------------- | ---------------------------------------------------------- |
| Zotero        | 학술 논문 라이브러리 관리 (`zotero.sqlite` 로컬 직접 조회) |
| Obsidian      | 요약 마크다운 문서 저장 및 관리                            |
| AI API Key    | 논문 요약 생성 — 최소 하나의 키 필요 (로컬 `.env`에만 저장되며 절대 유출되지 않음) |
| PDF 파일 폴더 | Zotero PDF 저장 폴더 (하위 폴더 포함 재귀 탐색)            |

---

## 설치 및 실행

[GitHub Releases](https://github.com/idlhy0218/ZOA-zotero-obsidian-ai/releases)에서 원하는 형식을 다운로드하거나 아래 방식들을 통해 시작해 보세요.

### 1. AI 코딩 에이전트 자동 설치 (Claude Code, Antigravity 등)
1. **에이전트에 지시**: 사용 중인 AI 에이전트 채팅창에 본 저장소 링크를 주며 설치 및 구동을 명령합니다:
   > "https://github.com/idlhy0218/ZOA-zotero-obsidian-ai 이 프로젝트 내 PC에 설치하고 실행 환경 세팅해줘."
2. **자동 구성**: 에이전트가 알아서 저장소 복제(Clone), 가상환경 구성 및 파이썬 패키지 설치를 마칩니다.
3. **설정 입력**: 에이전트가 요구하는 API 키와 파일 경로에 답변만 하면 설정 파일(`.env`) 생성부터 앱 실행까지 알아서 완료해 줍니다.

---

### 2. Windows 실행 파일 (`ZOA.exe` - 무설치 완제품)
1. **다운로드 및 배치**: `ZOA.exe`를 다운로드하여 전용 폴더(예: `ZOA/`)를 생성한 뒤 그 안에 넣습니다.
2. **앱 실행**: `ZOA.exe`를 더블클릭하여 시작합니다. (스마트스크린 경고 시 '추가 정보' → '실행' 클릭)
3. **설정 완료**: 실행 시 자동으로 나타나는 설정 마법사에 따라 API 키와 경로를 등록하면 실행 준비가 끝납니다.

---

### 3. macOS 실행 파일 (`ZOA-macOS.zip` - 무설치 완제품)
1. **압축 해제**: `ZOA-macOS.zip`을 다운로드하고 압축을 풀어 `ZOA.app`을 전용 폴더에 넣습니다.
2. **보안 예외 허용**: 최초 실행 시 Gatekeeper 차단 메시지가 뜨면 **시스템 설정 → 개인정보 보호 및 보안 → 보안** 섹션에서 ZOA 옆의 **"확인 없이 열기"**를 클릭하고 인증합니다.
3. **설정 완료**: 실행 후 나타나는 설정 마법사에 설정을 입력하면 홈 경로(`~/.zoa/.env`)에 환경설정이 안전하게 저장됩니다.

---

### 4. 소스 코드 직접 실행 (`Source code.zip` - 파이썬 3.11+ 환경)
1. **압축 해제**: `Source code.zip`을 다운로드받아 원하는 경로에 압축을 풉니다.
2. **의존 라이브러리 설치**: 터미널을 열고 다음 명령어를 실행합니다:
   ```bash
   pip install google-generativeai pypdf pillow
   ```
3. **프로그램 구동**: 윈도우는 `ZOA.bat`를 더블클릭하고, macOS/Linux는 `python zoa.py` 명령어로 실행합니다.

> **보안 안내**: 모든 API Key는 외부로 절대 전송되지 않으며, 앱/스크립트가 위치한 폴더 내 로컬 `.env` 파일(macOS는 `~/.zoa/.env`)에만 안전하게 저장됩니다.

---

## 주요 기능

| 기능                   | 설명                                                                                                                      |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| **다중 AI 지원**       | Google Gemini, Anthropic Claude, OpenAI, DeepSeek — Settings에서 제공사와 모델을 자유롭게 전환                            |
| **컬렉션 선택기**      | Zotero 컬렉션을 실시간 검색하고 다중 선택                                                                                 |
| **PDF 전체 본문 요약** | 저자/연도/제목 기반 자동 PDF 매칭, 최대 N페이지 추출(설정 가능)                                                           |
| **초록 폴백**          | PDF를 찾지 못할 경우 Zotero 초록 기반 요약으로 자동 전환                                                                  |
| **구조화 요약 출력**   | 모든 요약을 4개 섹션으로 정리: 연구 목적, 방법론, 핵심 결과, 키워드                                                       |
| **AI 프롬프트 커스텀** | Settings 패널에서 프롬프트 템플릿 직접 수정; `{title}`, `{content_source}`, `{keyword_count}`, `{text}` 플레이스홀더 지원 |
| **Obsidian 위키링크**  | 저자, 학술지, 태그를 자동으로 `[[위키링크]]` 형식으로 변환                                                                |
| **파일명 포맷 선택**   | 4가지 방식 중 선택 (Classic, Title, Year-Author-Title, Author-Year-Title)                                                 |
| **중복 문서 처리**     | 기존 요약 노트에 대해 덮어쓰기, 건너뛰기, 병합 중 선택                                                                    |
| **최근 논문 필터**     | 최근 N일 이내 추가/수정된 논문만 처리                                                                                     |
| **⚙ Settings 패널**    | 우측 상단 톱니바퀴 아이콘 — 파일 직접 수정 없이 모든 설정을 GUI에서 관리                                                  |

---

## 저장되는 마크다운 구조

```markdown
---
title: "논문 제목"
authors:
  - Last, First
date: 2026
journal: "학술지명"
zotero_link: zotero://select/items/0_XXXXXXXX
---

# 논문 제목

## Bibliographic Info

- **Authors**: Last, First
- **Journal**: 학술지명
- **Date**: 2026
- **Zotero Link**: [Open in Zotero](zotero://select/items/0_XXXXXXXX)
- **PDF Status**: PDF Found
- **Zotero Tags**: 태그1, 태그2

## AI Summary (Full PDF Content)

### 1. Research Objective

### 2. Methodology

### 3. Key Results

### 4. Keywords

#Keyword1 #Keyword2 #Keyword3

---

## Original Abstract

> (Zotero에 등록된 원본 초록)
```

---

## 자주 묻는 질문

**Q. Zotmoov 플러그인이 없어도 되나요?**  
네. Zotero 기본 `storage` 폴더를 PDF 경로로 지정하면 됩니다. ZOA가 하위 폴더까지 재귀 탐색하여 PDF를 자동 매칭합니다.

**Q. Zotero 데이터베이스 경로를 모르면 어떻게 하나요?**  
설정 마법사의 해당 항목을 빈칸으로 두고 진행하세요. Zotero가 기본 경로에 설치되어 있으면 자동으로 감지됩니다.

**Q. API 호출 요금이 발생하나요?**  
네, 하지만 비용이 극도로 저렴합니다. 일반적인 **30페이지 분량의 학술 논문 (~25,000 토큰)** 기준, 각 제공사별 엔트리(최저가) 모델의 1회 요약 예상 비용은 다음과 같습니다.
*   **Google Gemini** (Gemini 2.0/2.5 Flash): **무료** (Google AI Studio Free Tier 활용 시) 또는 **약 4원** ($0.003)
*   **DeepSeek** (DeepSeek-V3): **약 5원** ($0.0037)
*   **OpenAI** (gpt-4o-mini): **약 6원** ($0.004)
*   **Anthropic Claude** (Claude 3.5/4.5 Haiku): **약 30원** ($0.02)
*(2026년 기준. Claude 4.6 Sonnet 이나 GPT-4o 같은 고성능 플래그십 모델은 1회당 약 90원~110원 수준입니다.)*

**Q. 입력한 API Key가 외부로 유출될 위험이 있나요?**  
아니요. 모든 API Key는 외부 서버로 절대 전송되지 않으며, 사용자 PC 내부의 로컬 `.env` 파일(macOS의 경우 `~/.zoa/.env`)에만 안전하게 저장됩니다. 안심하고 사용하셔도 됩니다.

---

## 버그 제보

**[→ GitHub Issues에서 제보하기](https://github.com/idlhy0218/ZOA-zotero-obsidian-ai/issues)**  
스크린샷과 앱 하단 **Execution Log**의 내용을 함께 첨부해 주시면 빠른 해결이 가능합니다.

---

## 라이선스

[CC BY-NC 4.0 라이선스](LICENSE) — Copyright (c) 2026 Heeyoung Lee.
