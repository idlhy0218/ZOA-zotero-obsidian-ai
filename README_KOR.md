# ZOA (Zotero-Obsidian-AI Summary)

![Downloads](https://img.shields.io/github/downloads/idlhy0218/ZOA-zotero-obsidian-ai/total?style=flat-square)

Zotero, Obsidian, 그리고 다중 AI(Gemini, Claude, OpenAI, DeepSeek) 연동을 지원하는 학술 논문 자동 요약 파이프라인입니다. 로컬 Zotero 라이브러리에서 논문 정보를 조회하고 PDF 본문을 추출하여, 사용자가 선택한 AI 모델을 통해 요약 마크다운 문서를 생성한 후 Obsidian 보관소에 자동으로 저장합니다.

---

https://github.com/user-attachments/assets/3697a18f-aa96-4cc1-a27d-a22d59f4feaa

---

## 준비물

ZOA를 사용하려면 아래의 도구들이 설치되어 있어야 합니다.

| 준비물 | 용도 | 비고 |
|--------|------|------|
| Zotero | 학술 논문 라이브러리 관리 | 로컬 데이터베이스(`zotero.sqlite`)를 통해 메타데이터를 연동합니다. |
| Obsidian | 요약 마크다운 문서 저장 및 관리 | 무료 다운로드 및 사용이 가능합니다. |
| AI API Key | 논문 요약 생성 | Gemini, Claude, OpenAI, DeepSeek 중 최소 하나의 API Key가 필요합니다. |
| PDF 파일 폴더 | 논문 본문 텍스트 추출 | Zotero가 PDF를 저장하는 폴더(기본 `storage` 폴더 또는 Zotmoov 등으로 지정한 폴더) |

> 💡 **PDF 본문 분석 활성화 안내:** Zotmoov 같은 플러그인을 사용하여 PDF 파일을 특정 폴더로 자동 이동/분류하고 계시거나, 혹은 Zotero 기본 스토리지에 PDF가 흩어져 있더라도 상관없습니다. ZOA는 지정한 폴더 하위를 **재귀적(Recursive)으로 탐색**하기 때문에, PDF 파일들이 들어있는 가장 상위 폴더(예: Zotero의 기본 `storage` 폴더 등)를 지정해주기만 하면 완벽히 매칭 및 분석됩니다.

---

## 설치 및 실행

### 📥 최신 버전 다운로드
* **[ZOA 최신 정식 버전 다운로드 (GitHub Releases)](https://github.com/idlhy0218/ZOA-zotero-obsidian-ai/releases)**
* 운영체제에 맞는 최신 정식 빌드 파일(Windows: `ZOA.exe`, macOS: `ZOA-macOS.zip`)을 위 링크에서 손쉽게 내려받으실 수 있습니다.

https://github.com/user-attachments/assets/8ceca447-8950-432c-9446-bd815b829593

### 1. 전용 ZOA 폴더 생성 및 실행 파일 배치
반드시 **ZOA**라는 이름의 전용 폴더를 새로 생성하고, 다운로드한 ZOA 실행 파일(Windows: `ZOA.exe`, macOS: `ZOA-macOS.zip`)을 그 안에 넣어줍니다.
* **[매우 중요]** 실행 파일과 최초 실행 시 생성되는 설정 파일인 `.env`는 **항상 같은 폴더 안에 함께 있어야 합니다.** 실행 파일만 바탕화면 등으로 이동하거나 `.env` 파일과 분리될 경우, 프로그램이 설정을 인식하지 못해 정상적으로 작동하지 않습니다.
* **[윈도우 스마트스크린 보안 경고]** `ZOA.exe`를 최초 실행할 때 Windows Defender에서 **"Windows의 PC 보호"** 경고창이 나타날 수 있습니다. 이는 디지털 서명이 되지 않은 커스텀 실행 파일에서 보안 경고를 띄우는 일반적인 현상입니다. **"추가 정보(More info)"** 버튼을 누르신 후 나타나는 **"실행(Run anyway)"** 버튼을 클릭하시면 안전하게 정상 사용이 가능합니다.
* **[맥 최초 실행 시 차단 오류 해결 방법]** macOS에서 `ZOA` 앱을 최초 실행할 때 **"확인되지 않은 개발자가 배포하여 실행이 차단되었습니다"**라는 메시지가 뜨며 앱이 실행되지 않을 수 있습니다. 이는 다음과 같이 시스템 설정에서 간단히 허용하실 수 있습니다:
  1. Mac 화면 좌측 상단 Apple 메뉴() > **[시스템 설정]**(또는 시스템 환경설정)을 엽니다.
  2. **[개인정보 보호 및 보안]** 탭으로 이동합니다.
  3. 아래로 스크롤하여 **'보안'** 섹션을 찾습니다.
  4. 차단된 ZOA 앱 이름 옆의 **[확인 없이 열기]** 버튼을 클릭합니다.
  5. Mac 비밀번호 또는 Touch ID로 인증한 후 실행합니다.


### 2. API Key 발급
사용하고자 하는 인공지능 서비스의 공식 플랫폼에서 API Key를 발급받습니다.
* Google AI Studio (Gemini)
* Anthropic Console (Claude)
* OpenAI Platform (GPT)
* DeepSeek Platform (DeepSeek)

### 3. 설정 마법사 진행 및 보안 안내
ZOA 실행 파일을 더블클릭하여 구동합니다. 최초 실행 시 나타나는 설정 마법사(Setup Wizard) 안내에 따라 API Key 및 파일 경로를 입력하면 모든 설정이 완벽히 완료됩니다.

> **⚠️ API Key 보안 관련 절대 보장**
> `.env` 파일에 적혀있는 API Key는 오직 사용자의 컴퓨터 내부(로컬)에서만 안전하게 사용 및 보관되며, **외부의 그 누구와도 절대 공유되거나 전송되지 않습니다.** 안심하고 사용해 주십시오.

---

## 주요 기능

* **설정 마법사 제공**: GUI 기반의 초기 설정을 통해 초보자도 메모장 수동 편집 없이 키 값과 폴더 경로를 안전하게 구성할 수 있습니다.
* **다중 AI 지원 및 모델 동적 전환**: Google Gemini, Anthropic Claude, OpenAI, DeepSeek API를 종합 지원합니다. 선택한 AI 제공사에 맞게 최신 모델 리스트가 동적으로 갱신됩니다.
* **Zotero 컬렉션 다중 선택**: 로컬 조테로의 폴더 구조(Collection)를 실시간 검색하고 원하는 폴더들만 다중 선택하여 요약을 시작할 수 있습니다.
* **로컬 DB 연동 및 초고속 조회**: 온라인 동기화 지연 없이 로컬 SQLite DB(`zotero.sqlite`)를 직접 조회하여 데이터를 즉각 식별합니다.
* **지능형 PDF 매칭 및 전체 본문 요약**: 논문 저자명, 연도, 키워드를 활용해 내 컴퓨터 속 PDF 본문을 자동 매칭합니다. 본문이 매칭되면 최대 30페이지 분량의 PDF 전체 텍스트를 읽어 정밀 요약을 생성하며, 미매칭 시 초록(Abstract) 기반 요약으로 자동 전환됩니다.
* **구조화된 학술 요약 포맷**: AI가 연구 목적(Research Objective), 방법론(Methodology), 핵심 결과(Key Results), 키워드(Keywords) 4개 섹션으로 체계화된 요약을 생성합니다. 앱에서 키워드 개수(1~10개, 기본값 5개)를 직접 설정할 수 있습니다.
* **사용자 정의 AI 프롬프트 에디터**: UI에 내장된 접이식 에디터를 통해 논문 요약에 사용되는 AI 프롬프트 템플릿을 자유롭게 수정하고 적용할 수 있습니다. `{title}`, `{content_source}`, `{keyword_count}`, `{text}`와 같은 동적 변수를 지원하며, 커스텀 템플릿은 `prompt_template.txt` 파일로 로컬에 영구 저장됩니다.
* **자동 위키링크 및 태그 연결**: 요약 내 포함된 저자, 학술지, 태그 등을 옵시디언 고유의 `[[위키링크]]` 형태로 자동 치환하여 유기적인 지식 그래프 구축을 지원합니다.
* **필터링 및 중복 처리**: 최근 N일 이내에 추가된 논문만 골라 요약하는 필터와, 이미 요약된 문서에 대한 건너뛰기/덮어쓰기/새로운 논문만 업데이트 기능을 세부적으로 제공합니다.

---

## 저장되는 요약 마크다운 구조

생성되어 Obsidian으로 저장되는 마크다운 문서는 아래와 같은 표준적인 템플릿 구조를 지닙니다.

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

## AI Summary (Full PDF Content)

### 1. Research Objective
(연구 질문 및 연구 대상/맥락)

### 2. Methodology
(데이터 출처, 주요 변수, 분석 모델)

### 3. Key Results
(주요 발견 사항, 효과의 방향 및 크기 포함)

### 4. Keywords
#Keyword1 #Keyword2 #Keyword3 #Keyword4 #Keyword5

---
## Original Abstract
> (Zotero 라이브러리에 등록되어 있는 영문/국문 원본 초록 정보가 보존됩니다.)
```

---

## 자주 묻는 질문 (FAQ)

**Q. Zotmoov 플러그인을 반드시 사용해야 하나요?**  
아닙니다. Zotmoov를 쓰지 않더라도 Zotero의 기본 PDF 저장 경로(예: Zotero 데이터가 담긴 기본 `storage` 폴더)를 ZOA 앱에 지정해주면 문제없이 작동합니다. ZOA는 지정한 폴더 하위의 모든 디렉토리를 깊숙이 재귀적으로 탐색하여 PDF 본문을 자동으로 매칭합니다. PDF가 없거나 찾지 못한 논문의 경우에는 등록된 초록(Abstract)을 바탕으로 안전하게 요약본을 생성합니다.

**Q. API 호출 요금이 부과됩니까?**  
사용하시는 개별 AI 서비스(Google, Anthropic, OpenAI, DeepSeek)의 과금 정책에 따라 요금이 부과되거나 무료 한도가 제공될 수 있습니다. 자세한 요금은 각 서비스의 공식 개발자 플랫폼 홈페이지를 참고해 주십시오.

**Q. Zotero SQLite 데이터베이스 경로를 모르는 경우에는 어떻게 합니까?**  
설정 마법사의 해당 필드를 빈칸으로 두고 진행하시면 됩니다. 조테로가 기본 폴더 경로에 설치되어 있다면 프로그램이 실행되는 즉시 위치를 자동으로 탐색하여 감지합니다.

---

## 개인정보 및 보안 정책

* **로컬 보안 저장**: 사용자의 중요 자산인 API Key 및 연동 설정 데이터는 인터넷 상의 어떠한 외부 서버로도 전송되지 않으며, 오직 실행 파일이 위치한 경로 내의 `.env` 파일에 로컬 저장되어 완벽히 보호됩니다.
* **직접 통신**: 논문 정보 및 PDF 추출 텍스트는 오직 사용자가 명시한 공식 AI API 서버(Google, Anthropic, OpenAI, DeepSeek)로만 암호화 전송되며, 어떠한 제3자 서버나 마케팅 용도로 수집 또는 공유되지 않습니다.

---

## 버전 기록 (Version History)

* **v1.0-beta (ZOA 초기 베타 릴리즈)**
  * 기존 GOZ 파이프라인 전면 개편 및 다중 API 연동 구조 구현
  * Google Gemini, Anthropic Claude, OpenAI, DeepSeek 4대 인공지능 엔진 종합 지원
  * 제공사 변경 시 적용 가능한 최신 모델로 동적 콤보박스 전환 연동
  * 파이썬 표준 라이브러리(urllib) 기반 REST 클라이언트 적용으로 패키징 최적화 및 경량화 성공
  * 학술 전문 AI 요약 프롬프트 적용: Research Objective / Methodology / Key Results / Keywords 4개 섹션 구조화 출력
  * UI에서 키워드 개수 설정 기능 추가 (1~10개, 기본값 5개)

---

## 버그 제보 및 기능 건의 (Support)

ZOA 앱을 사용하시던 중 버그가 발생하거나 기능 개선이 필요하다면 아래의 이슈 링크를 통해 제보해 주십시오.
* **[에러 및 피드백 제보하기 (GitHub Issues)](https://github.com/idlhy0218/ZOA-zotero-obsidian-ai/issues)**
* 제보 시 에러가 발생한 화면 스크린샷과 앱 하단 **Execution Log**의 텍스트 내용을 함께 기재해 주시면 더욱 신속한 오류 해결이 가능합니다.

---

## 라이선스 (License)

본 프로젝트는 [MIT 라이선스](LICENSE)를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하십시오.  
Copyright (c) 2026 Heeyoung Lee. All rights reserved.
