# ZOA (Zotero-Obsidian-AI Summary) v1.0-beta

![Downloads](https://img.shields.io/github/downloads/idlhy0218/ZOA-zotero-obsidian-ai/total?style=flat-square&color=615478)
[![지원 플랫폼](https://img.shields.io/badge/플랫폼-Windows%20%7C%20macOS-A40808?style=flat-square)](#설치-및-실행)
[![파이썬 버전](https://img.shields.io/badge/파이썬-3.11+-615478?style=flat-square)](#설치-및-실행)
[![Download Latest Release](https://img.shields.io/badge/Download-Latest%20Release-615478?style=for-the-badge&logo=github)](https://github.com/idlhy0218/ZOA-zotero-obsidian-ai/releases/latest)

Zotero, Obsidian, 그리고 다중 AI(Gemini, Claude, OpenAI, DeepSeek)를 연동하는 학술 논문 자동 요약 파이프라인입니다. 로컬 Zotero 라이브러리에서 논문 정보를 조회하고 PDF 본문을 추출하여, 선택한 AI 모델로 구조화된 요약 마크다운 문서를 생성한 후 Obsidian 보관소에 자동 저장합니다.

> ### 🚀 [최신 버전 다운로드 (ZOA.exe / ZOA-macOS.zip)](https://github.com/idlhy0218/ZOA-zotero-obsidian-ai/releases/latest)
>
> English README: [README.md](README.md)

---

https://github.com/user-attachments/assets/3697a18f-aa96-4cc1-a27d-a22d59f4feaa

---

## 준비물

| 준비물 | 용도 |
|--------|------|
| Zotero | 학술 논문 라이브러리 관리 (`zotero.sqlite` 로컬 직접 조회) |
| Obsidian | 요약 마크다운 문서 저장 및 관리 |
| AI API Key | 논문 요약 생성 — 최소 하나의 키 필요 |
| PDF 파일 폴더 | Zotero PDF 저장 폴더 (하위 폴더 포함 재귀 탐색) |

---

## 설치 및 실행

[GitHub Releases](https://github.com/idlhy0218/ZOA-zotero-obsidian-ai/releases)에서 원하는 형식을 다운로드하고 아래 안내에 따라 실행하세요.

### 1. Windows 실행 파일 (`ZOA.exe` - 추천)
1. **다운로드 및 배치**: `ZOA.exe`를 다운로드하여 전용 폴더(예: `ZOA/`)를 생성한 뒤 그 안에 넣습니다.
2. **앱 실행**: `ZOA.exe`를 더블클릭하여 시작합니다. (스마트스크린 경고 시 '추가 정보' → '실행' 클릭)
3. **설정 완료**: 실행 시 자동으로 나타나는 설정 마법사에 따라 API 키와 경로를 등록하면 실행 준비가 끝납니다.

---

### 2. macOS 실행 파일 (`ZOA-macOS.zip`)
1. **압축 해제**: `ZOA-macOS.zip`을 다운로드하고 압축을 풀어 `ZOA.app`을 전용 폴더에 넣습니다.
2. **보안 예외 허용**: 최초 실행 시 Gatekeeper 차단 메시지가 뜨면 **시스템 설정 → 개인정보 보호 및 보안 → 보안** 섹션에서 ZOA 옆의 **"확인 없이 열기"**를 클릭하고 인증합니다.
3. **설정 완료**: 실행 후 나타나는 설정 마법사에 설정을 입력하면 홈 경로(`~/.zoa/.env`)에 환경설정이 안전하게 저장됩니다.

---

### 3. 소스 코드 직접 실행 (`Source code.zip` - 파이썬 3.11+ 환경)
1. **압축 해제**: `Source code.zip`을 다운로드받아 원하는 경로에 압축을 풉니다.
2. **의존 라이브러리 설치**: 터미널을 열고 다음 명령어를 실행합니다:
   ```bash
   pip install google-generativeai pypdf pillow
   ```
3. **프로그램 구동**: 윈도우는 `ZOA.bat`를 더블클릭하고, macOS/Linux는 `python zoa.py` 명령어로 실행합니다.

> **보안 안내**: 모든 API Key는 외부로 절대 전송되지 않으며, 앱/스크립트가 위치한 폴더 내 로컬 `.env` 파일(macOS는 `~/.zoa/.env`)에만 안전하게 저장됩니다.

---

## 주요 기능

| 기능 | 설명 |
|------|------|
| **다중 AI 지원** | Google Gemini, Anthropic Claude, OpenAI, DeepSeek — Settings에서 제공사와 모델을 자유롭게 전환 |
| **컬렉션 선택기** | Zotero 컬렉션을 실시간 검색하고 다중 선택 |
| **PDF 전체 본문 요약** | 저자/연도/제목 기반 자동 PDF 매칭, 최대 N페이지 추출(설정 가능) |
| **초록 폴백** | PDF를 찾지 못할 경우 Zotero 초록 기반 요약으로 자동 전환 |
| **구조화 요약 출력** | 모든 요약을 4개 섹션으로 정리: 연구 목적, 방법론, 핵심 결과, 키워드 |
| **AI 프롬프트 커스텀** | Settings 패널에서 프롬프트 템플릿 직접 수정; `{title}`, `{content_source}`, `{keyword_count}`, `{text}` 플레이스홀더 지원 |
| **Obsidian 위키링크** | 저자, 학술지, 태그를 자동으로 `[[위키링크]]` 형식으로 변환 |
| **파일명 포맷 선택** | 4가지 방식 중 선택 (Classic, Title, Year-Author-Title, Author-Year-Title) |
| **중복 문서 처리** | 기존 요약 노트에 대해 덮어쓰기, 건너뛰기, 병합 중 선택 |
| **최근 논문 필터** | 최근 N일 이내 추가/수정된 논문만 처리 |
| **⚙ Settings 패널** | 우측 상단 톱니바퀴 아이콘 — 파일 직접 수정 없이 모든 설정을 GUI에서 관리 |

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
각 제공사(Google, Anthropic, OpenAI, DeepSeek)의 과금 정책에 따라 다릅니다. 일부는 무료 한도를 제공하므로 각 플랫폼을 확인하세요.

---

## 버그 제보

**[→ GitHub Issues에서 제보하기](https://github.com/idlhy0218/ZOA-zotero-obsidian-ai/issues)**  
스크린샷과 앱 하단 **Execution Log**의 내용을 함께 첨부해 주시면 빠른 해결이 가능합니다.

---

## 라이선스

[MIT 라이선스](LICENSE) — Copyright (c) 2026 Heeyoung Lee.
