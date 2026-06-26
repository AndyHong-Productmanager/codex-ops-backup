---
name: hospital-seo-planner
description: >
  병의원 홈페이지 제작 전 SEO/AEO/GEO 설계 문서를 자동 생성하는 스킬.
  단계적 질문으로 병원 정보를 수집한 뒤, URL 구조, 사이트맵, 메타 태그 템플릿,
  JSON-LD(FAQ·Organization·Person 포함), robots.txt, llms.txt, 내부 링크 맵,
  저자·E-E-A-T 설계, 콘텐츠 전략을 한 번에 출력한다.
  트리거: "병원 홈페이지 설계", "SEO 설계", "사이트 구조 설계",
  "홈페이지 만들기 전에", "URL 구조 짜줘", "병원 사이트 기획",
  "SEO plan", "hospital seo plan", "홈페이지 SEO 가이드",
  "sitemap 설계", "JSON-LD 설계", "llms.txt 만들어줘",
  "병원 홈페이지 구조", "의원 홈페이지 설계", "클리닉 사이트 기획",
  "홈페이지 만들어줘 SEO", "병원 사이트맵", "의료 SEO",
  "FAQ 스키마", "Organization 스키마", "E-E-A-T 설계", "저자 페이지".
  병원/의원/클리닉 홈페이지를 새로 만들거나 리뉴얼할 때 반드시 이 스킬을 사용한다.
---

# Hospital SEO Planner v2

> **핵심 원칙**: SEO는 나중에 붙이는 기능이 아니다. URL·콘텐츠·내부 링크·sitemap·JSON-LD가 처음부터 맞물려야 강해진다.

## 실행 흐름

```
STEP 0:  질문으로 정보 수집 (3라운드)
STEP 1:  검색 의도 매핑
STEP 2:  URL 구조 + 사이트맵
STEP 3:  메타 태그 템플릿
STEP 4:  JSON-LD 전체 (FAQ·Organization·Person 포함)
STEP 5:  robots.txt
STEP 6:  llms.txt / llms-full.txt
STEP 7:  내부 링크 맵
STEP 8:  저자·E-E-A-T 설계
STEP 9:  콘텐츠 전략
STEP 10: 최종 Plan 문서(.md) 출력
```

---

## STEP 0: 단계적 질문

3라운드로 나눠서 질문한다. `ask_user_input_v0` 적극 활용.

### 라운드 1: 기본 정보 (필수)

```
Q1. 병원명 (한글 + 영문)
Q2. 의과 타입 → single_select: 치과 / 정형외과 / 피부과 / 한의원 / 내과 / 기타
Q3. 주소 (도로명)
Q4. 전화번호
Q5. 대표 진료과목 (최대 8개, 쉼표 구분)
Q6. 진료시간 (평일/토/일/공휴일)
Q7. 브랜드 USP (핵심 차별점 1~2가지)
```

**의과 타입 → 자동 세팅:**

| 의과 | JSON-LD @type | 시드 파일 |
|------|-------------|----------|
| 치과 | Dentist | references/seeds-dental.md |
| 정형외과 | MedicalClinic | references/seeds-ortho.md |
| 피부과 | MedicalClinic | references/seeds-derma.md |
| 한의원 | MedicalClinic | references/seeds-tcm.md |
| 내과/기타 | MedicalClinic | 사용자에게 직접 질문 |

### 라운드 2: SEO 전략 (중요)

```
Q8.  타겟 지역 리스트 (시/구/동)
Q9.  대표 의료진 정보 (이름, 학력, 경력, 전문분야) — 최소 1명
Q10. 예약 채널 → multi_select: 네이버 예약 / 카카오톡 / 전화만 / 기타
Q11. 소셜 미디어 URL (블로그, 인스타, 유튜브 등) — 없으면 "없음"
Q12. 경쟁사 URL (벤치마킹용) — 없으면 스킵
```

### 라운드 3: 콘텐츠 자산 (선택 — 전부 스킵 가능)

```
Q13. 시설 사진 보유 여부 → single_select: 있음 / 준비 중 / 없음
Q14. 비포/애프터 케이스 보유 여부
Q15. 특별 콘텐츠 계획 (AI 증상체커, 비용 계산기, 원장 컬럼 등)
```

---

## STEP 1: 검색 의도 매핑

```
검색 의도         예시 키워드                         대응 페이지
───────────────────────────────────────────────────────────────
① 브랜드        {병원명}, {대표원장명}                / (홈)
② 지역          {지역} {의과}                        /area/{지역}-{진료}
③ 진료          {진료1}, {진료2}                     /treatments/{슬러그}
④ 증상          {증상1}, {증상2}                     /symptoms/{슬러그}
⑤ 정보          {질환} 원인, {시술} 부작용            /encyclopedia/{슬러그}
⑥ 전환          비용, 예약, 오시는 길                 /pricing, /reservation, /directions
```

증상 키워드는 의과별 `references/seeds-{의과}.md`에서 로드한다.

---

## STEP 2: URL 구조 + 사이트맵

### URL 트리

URL은 영문 소문자 + 하이픈만. 깊이 최대 3단계.

```
/                              ← 홈
/treatments/                   ← 전체 진료
/treatments/{진료1-slug}
/symptoms/{증상1-slug}
/doctors/
/doctors/{의료진1-slug}
/authors/                      ← 저자 프로필 (E-E-A-T)
/authors/{저자1-slug}
/encyclopedia/
/encyclopedia/{용어1-slug}
/area/{지역1}-{진료1}           ← Q8 × Q5 조합
/faq/
/faq/{진료1-slug}
/blog/
/pricing
/directions
/reservation
/column/
/video/
```

### 사이트맵 Index

```xml
<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap><loc>https://{도메인}/sitemap-main.xml</loc></sitemap>
  <sitemap><loc>https://{도메인}/sitemap-treatments.xml</loc></sitemap>
  <sitemap><loc>https://{도메인}/sitemap-symptoms.xml</loc></sitemap>
  <sitemap><loc>https://{도메인}/sitemap-area.xml</loc></sitemap>
  <sitemap><loc>https://{도메인}/sitemap-encyclopedia.xml</loc></sitemap>
  <sitemap><loc>https://{도메인}/sitemap-blog.xml</loc></sitemap>
  <sitemap><loc>https://{도메인}/sitemap-faq.xml</loc></sitemap>
</sitemapindex>
```

**URL 수량 계산**: 지역SEO = 지역수 × 진료수, 메인 = 고정 + 의료진 + 저자, 총 = 합계 + 백과사전 시드수

---

## STEP 3: 메타 태그 템플릿

**변수를 치환한 완성본으로 출력한다.**

| 페이지 | title | H1 |
|--------|-------|----|
| 홈 | {병원명} \| {지역} {진료1}·{진료2}·{USP} | {지역} {병원명} \| {USP} |
| 진료 | {지역} {진료명} 잘하는 곳 \| {세부USP} — {병원명} | {지역} {진료명} |
| 증상 | {지역} {증상} 원인과 치료 \| {병원명} | {증상} 원인과 치료 |
| 백과사전 | {용어}란? \| 뜻, 비용, 과정 — {병원명} | {용어}란? |
| 지역 SEO | {지역} {진료} 추천 \| {USP} — {병원명} | {지역} {진료} |
| FAQ | {진료} 자주 묻는 질문 \| 비용, 기간 — {병원명} | {진료} 자주 묻는 질문 |
| 의료진 | {의사명} \| {전문분야} — {병원명} | {의사명} 원장 |
| 저자 | {저자명} \| {전문분야} 콘텐츠 감수 — {병원명} | {저자명} |

**description**: title과 동일 구조 + 전화번호. 160자 이내.
**H 규칙**: H1 1개만, H2 → H3 순서, H2 없이 H3 금지.

---

## STEP 4: JSON-LD 전체 템플릿

> **핵심 원칙: JSON-LD에 넣은 내용은 반드시 실제 페이지 본문에도 보여야 한다.**

수집 정보를 치환하여 **복사-붙여넣기 가능한 완성 코드블록**을 페이지별로 출력한다.

### 4-1. 홈 — 메인 의료 스키마

```json
{
  "@context": "https://schema.org",
  "@type": "{Dentist|MedicalClinic}",
  "name": "{병원명}",
  "alternateName": "{영문병원명}",
  "url": "https://{도메인}",
  "logo": "https://{도메인}/images/logo.png",
  "image": "https://{도메인}/images/exterior.webp",
  "telephone": "{전화번호}",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "{도로명주소}",
    "addressLocality": "{시군구}",
    "addressRegion": "{시도}",
    "postalCode": "{우편번호}",
    "addressCountry": "KR"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": "{위도}",
    "longitude": "{경도}"
  },
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"],
      "opens": "{평일시작}", "closes": "{평일종료}"
    },
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": "Saturday",
      "opens": "{토시작}", "closes": "{토종료}"
    }
  ],
  "medicalSpecialty": ["{진료1}", "{진료2}"],
  "availableService": [
    {"@type": "MedicalProcedure", "name": "{진료1}"},
    {"@type": "MedicalProcedure", "name": "{진료2}"}
  ],
  "sameAs": ["{네이버블로그}", "{인스타}", "{유튜브}", "{카카오채널}"]
}
```

### 4-2. 홈 — Organization (Brand MID)

검색 엔진과 AI가 병원을 명확히 식별하기 위한 구조화 데이터. **필수 필드: name, address, contactPoint, sameAs.**

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "{병원명}",
  "url": "https://{도메인}",
  "logo": "https://{도메인}/images/logo.png",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "{도로명주소}",
    "addressLocality": "{시군구}",
    "addressRegion": "{시도}",
    "postalCode": "{우편번호}",
    "addressCountry": "KR"
  },
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "{전화번호}",
    "contactType": "customer service",
    "availableLanguage": "Korean"
  },
  "sameAs": ["{네이버블로그}", "{인스타}", "{유튜브}", "{카카오채널}", "{네이버플레이스}"]
}
```

`sameAs` 규칙: Q11 소셜 URL 전부 포함. 네이버 플레이스 필수 권장. 빈 문자열 금지.

### 4-3. 홈 — WebSite + SiteNavigationElement

```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "{병원명}",
  "url": "https://{도메인}",
  "potentialAction": {
    "@type": "SearchAction",
    "target": "https://{도메인}/search?q={search_term_string}",
    "query-input": "required name=search_term_string"
  }
}
```

```json
{
  "@context": "https://schema.org",
  "@type": "SiteNavigationElement",
  "name": "주요 메뉴",
  "hasPart": [
    {"@type": "SiteNavigationElement", "name": "진료 안내", "url": "https://{도메인}/treatments/"},
    {"@type": "SiteNavigationElement", "name": "의료진", "url": "https://{도메인}/doctors/"},
    {"@type": "SiteNavigationElement", "name": "비용 안내", "url": "https://{도메인}/pricing"},
    {"@type": "SiteNavigationElement", "name": "오시는 길", "url": "https://{도메인}/directions"},
    {"@type": "SiteNavigationElement", "name": "예약", "url": "https://{도메인}/reservation"}
  ]
}
```

### 4-4. 진료 페이지 — MedicalWebPage + MedicalProcedure + FAQ + Breadcrumb

```json
[
  {
    "@context": "https://schema.org",
    "@type": "MedicalWebPage",
    "name": "{지역} {진료명}",
    "url": "https://{도메인}/treatments/{슬러그}",
    "lastReviewed": "{YYYY-MM-DD}",
    "author": {"@type": "Person", "name": "{저자명}", "url": "https://{도메인}/authors/{slug}"},
    "reviewedBy": {"@type": "Physician", "name": "{감수의사}", "url": "https://{도메인}/authors/{slug}"}
  },
  {
    "@context": "https://schema.org",
    "@type": "MedicalProcedure",
    "name": "{진료명}",
    "procedureType": "http://schema.org/NoninvasiveProcedure",
    "bodyLocation": "{시술부위}"
  },
  {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {"@type": "ListItem", "position": 1, "name": "홈", "item": "https://{도메인}/"},
      {"@type": "ListItem", "position": 2, "name": "진료 안내", "item": "https://{도메인}/treatments/"},
      {"@type": "ListItem", "position": 3, "name": "{진료명}", "item": "https://{도메인}/treatments/{슬러그}"}
    ]
  }
]
```

### 4-5. FAQ 스키마 — FAQPage (HIGH: AI Overview 우선 인용)

**적용 대상**: 모든 진료 페이지, 증상 페이지, FAQ 허브, 홈(대표 3~5개)
**답변 규칙**: 표 또는 리스트 형식 사용. 첫 문장은 질문에 직접 답변. JSON-LD 개수 = 본문 FAQ 개수 1:1 대응.

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "{진료명} 비용은 얼마인가요?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "{진료명} 비용은 {가격대}입니다. <ul><li>기본: {가격1}</li><li>프리미엄: {가격2}</li></ul> 정확한 비용은 진료 후 결정됩니다."
      }
    },
    {
      "@type": "Question",
      "name": "{진료명} 기간은 얼마나 걸리나요?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "평균 {기간}이 소요됩니다. <table><tr><th>단계</th><th>기간</th></tr><tr><td>상담</td><td>1회</td></tr><tr><td>시술</td><td>{N}회</td></tr></table>"
      }
    }
  ]
}
```

진료과목별 FAQ 시드는 `references/seeds-{의과}.md`에서 로드.

### 4-6. 증상 페이지 — MedicalCondition

```json
[
  {
    "@context": "https://schema.org",
    "@type": "MedicalWebPage",
    "name": "{증상명} 원인과 치료",
    "url": "https://{도메인}/symptoms/{슬러그}",
    "lastReviewed": "{YYYY-MM-DD}",
    "author": {"@type": "Person", "name": "{저자명}", "url": "https://{도메인}/authors/{slug}"},
    "reviewedBy": {"@type": "Physician", "name": "{감수의사}"}
  },
  {
    "@context": "https://schema.org",
    "@type": "MedicalCondition",
    "name": "{증상/질환명}",
    "signOrSymptom": {"@type": "MedicalSignOrSymptom", "name": "{증상}"},
    "possibleTreatment": [
      {"@type": "MedicalTherapy", "name": "{치료1}"},
      {"@type": "MedicalTherapy", "name": "{치료2}"}
    ]
  }
]
```

### 4-7. 의료진 — Physician

```json
{
  "@context": "https://schema.org",
  "@type": "Physician",
  "name": "{의사명}",
  "image": "https://{도메인}/images/doctors/{slug}.webp",
  "jobTitle": "{직책}",
  "medicalSpecialty": "{전문분야}",
  "alumniOf": {"@type": "EducationalOrganization", "name": "{출신대학}"},
  "worksFor": {"@type": "{Dentist|MedicalClinic}", "name": "{병원명}"},
  "url": "https://{도메인}/doctors/{slug}"
}
```

### 4-8. 백과사전 — DefinedTerm

```json
[
  {
    "@context": "https://schema.org",
    "@type": "MedicalWebPage",
    "name": "{용어}란?",
    "url": "https://{도메인}/encyclopedia/{slug}",
    "lastReviewed": "{YYYY-MM-DD}",
    "author": {"@type": "Person", "name": "{저자명}", "url": "https://{도메인}/authors/{slug}"},
    "reviewedBy": {"@type": "Physician", "name": "{감수의사}"}
  },
  {
    "@context": "https://schema.org",
    "@type": "DefinedTerm",
    "name": "{용어}",
    "description": "{정의 1~2문장}",
    "inDefinedTermSet": "https://{도메인}/encyclopedia/"
  }
]
```

### 4-9. 저자 — Person (E-E-A-T)

STEP 8에서 설계하는 `/authors/{slug}` 페이지에 적용.

```json
{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "{저자명}",
  "jobTitle": "{직함}",
  "image": "https://{도메인}/images/authors/{slug}.webp",
  "url": "https://{도메인}/authors/{slug}",
  "worksFor": {"@type": "{Dentist|MedicalClinic}", "name": "{병원명}", "url": "https://{도메인}"},
  "alumniOf": {"@type": "EducationalOrganization", "name": "{출신대학}"},
  "knowsAbout": ["{전문분야1}", "{전문분야2}"],
  "sameAs": ["https://{도메인}/doctors/{slug}", "{외부프로필URL}"]
}
```

---

## STEP 5: robots.txt

변수 치환 후 **완성본** 출력.

```
# {병원명} - robots.txt
# https://{도메인}

User-agent: *
Allow: /
Disallow: /admin/
Disallow: /auth/
Disallow: /api/
Disallow: /components/
Disallow: /*.json$
Disallow: /manifest.json
Disallow: /_next/

User-agent: Googlebot
Allow: /
Crawl-delay: 1

User-agent: Googlebot-Image
Allow: /images/
Allow: /treatments/
Disallow: /admin/

User-agent: Googlebot-Video
Allow: /video/
Disallow: /admin/

User-agent: Googlebot-News
Allow: /blog/
Allow: /column/

User-agent: Yeti
Allow: /
Crawl-delay: 2

User-agent: Daum
Allow: /

User-agent: Bingbot
Allow: /
Crawl-delay: 2

# AI/LLM 크롤러
User-agent: GPTBot
Allow: /
Disallow: /admin/
Disallow: /auth/

User-agent: ChatGPT-User
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: GoogleOther
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Applebot
Allow: /

User-agent: FacebookBot
Allow: /

Sitemap: https://{도메인}/sitemap.xml
```

---

## STEP 6: llms.txt / llms-full.txt

### llms.txt (요약본)

```markdown
# {병원명}

> {지역} 소재 {USP}. {핵심 차별점 1~2문장}.
> {진료과 나열}. {전문의 정보}. {전화번호}.

## 핵심 페이지
- [{진료1}](https://{도메인}/treatments/{slug1}): {한줄 설명}
- [{진료2}](https://{도메인}/treatments/{slug2}): {한줄 설명}
- [의료진](https://{도메인}/doctors/): {한줄 설명}
- [비용 안내](https://{도메인}/pricing): {한줄 설명}
- [오시는 길](https://{도메인}/directions): {한줄 설명}

## 콘텐츠
- [FAQ](https://{도메인}/faq): 자주 묻는 질문
- [백과사전](https://{도메인}/encyclopedia/): {N}개 전문 용어
- [블로그](https://{도메인}/blog/): 건강 정보 콘텐츠

## 기본 정보
- 주소: {도로명주소}
- 전화: {전화번호}
- 진료시간: {요약}
- 예약: {네이버 예약 URL}
```

### llms-full.txt (상세본)

```markdown
# {병원명} — 상세 안내

> (llms.txt와 동일한 요약)

## 진료 안내

### {진료1}
{진료1 설명 2~3문장. 대상 환자, 장비/시설 특징.}
URL: https://{도메인}/treatments/{slug1}

### {진료2}
{진료2 설명 2~3문장.}
URL: https://{도메인}/treatments/{slug2}

## 의료진
- {의사1}: {학력}, {전문분야}, {경력 요약}

## 자주 묻는 질문
- Q: {질문1}
  A: {답변1}
- Q: {질문2}
  A: {답변2}

## 연락처
- 주소: {전체 주소}
- 전화: {전화번호}
- 네이버 예약: {URL}
- 카카오톡: {URL}
- 진료시간: 평일 {시간}, 토 {시간}, 일 {시간}
```

---

## STEP 7: 내부 링크 맵

### 정방향 퍼널

```
증상 → 백과사전(질환 이해) → 진료(전환) → 의료진 → FAQ → 예약
```

### 역방향 연결

```
진료 → "이런 증상이 있다면" → 증상
진료 → "용어 설명" → 백과사전
의료진 → "전문 분야" → 진료
FAQ → "더 자세히" → 진료/백과사전
지역 → "인기 진료" → 진료
블로그/백과사전 → "작성자" → /authors/{slug}
```

### 토픽 클러스터

각 진료과목이 **허브**, 관련 증상/백과사전/FAQ/지역/블로그가 **스포크**.

**어떤 페이지에서든 2~3번 클릭 안에 예약 페이지 도달.**

---

## STEP 8: 저자·E-E-A-T 설계

의료 콘텐츠는 YMYL이므로 **저자 신뢰 신호가 특히 중요**.

### 8-1. /authors/{slug} 페이지 필수 요소

- 프로필 사진, 이름, 직함
- 학력/경력 요약, 전문분야 태그
- 해당 저자가 작성/감수한 콘텐츠 목록 (자동 연결)
- 외부 프로필 링크 (학회, LinkedIn)

Q9 의료진은 자동으로 저자 후보에 포함.
`/doctors/{slug}`와 `/authors/{slug}`가 동일 인물이면 `sameAs`로 상호 연결.

### 8-2. 바이라인 (Byline)

모든 의료 콘텐츠(백과사전, 블로그, 증상, 진료)에 삽입.

```html
<div class="byline">
  <img src="/images/authors/{slug}.webp" alt="{저자명}" />
  <span>작성: <a href="/authors/{slug}">{저자명}</a> · {직함}</span>
  <time datetime="{YYYY-MM-DD}">최종 검토: {날짜}</time>
</div>
```

### 8-3. 콘텐츠 → 저자 JSON-LD 연결

MedicalWebPage에 author + reviewedBy + lastReviewed + dateModified 추가.
(STEP 4-4, 4-6, 4-8 템플릿에 이미 반영됨)

---

## STEP 9: 콘텐츠 전략

### 백과사전 시드

의과별 `references/seeds-{의과}.md`에서 로드. 최소 50개 용어 선정.

| # | 용어 | URL 슬러그 | 연결 진료 | 우선순위 |

### 블로그 키워드 시드

최소 20개. 패턴: "{진료} 비용", "{진료} 후기", "{증상} 원인", "{진료} vs {진료}", "{지역} {진료} 추천"

---

## STEP 10: 최종 출력

모든 STEP을 하나의 마크다운으로 합쳐 출력.

**파일명**: `{병원명}_seo_plan.md` → `/mnt/user-data/outputs/`

```markdown
# {병원명} SEO 설계 문서
> 생성일: {날짜} | 스킬: hospital-seo-planner v2.0

## 1. 병원 기본 정보
## 2. 검색 의도 매핑
## 3. URL 구조
## 4. 사이트맵 구조
## 5. 메타 태그 (페이지별 완성본)
## 6. JSON-LD (페이지별 완성 코드블록)
### 6-A. FAQ 스키마 (진료·증상별)
### 6-B. Organization 스키마
### 6-C. Person 스키마 (저자별)
## 7. robots.txt (완성본)
## 8. llms.txt (완성본)
## 9. llms-full.txt (완성본)
## 10. 내부 링크 맵
## 11. 저자·E-E-A-T 설계
## 12. 콘텐츠 전략
## 13. 구현 체크리스트
### FAQ: [ ] 진료 페이지 FAQPage 적용 / [ ] 답변 표/리스트 / [ ] 개수 1:1 대응
### Organization: [ ] 홈에 배포 / [ ] name,address,contactPoint,sameAs 포함
### E-E-A-T: [ ] /authors/ 생성 / [ ] 바이라인 / [ ] Person Schema / [ ] author/reviewedBy 연결
```

`present_files`로 전달.

---

## 분리 유지 파일

| 파일 | 용도 |
|------|------|
| `references/seeds-dental.md` | 치과 증상 키워드 + 백과사전 용어 시드 |
| `references/seeds-ortho.md` | 정형외과 시드 |
| `references/seeds-derma.md` | 피부과 시드 |
| `references/seeds-tcm.md` | 한의원 시드 |

해당 의과일 때만 읽는다. 나머지 모든 로직·템플릿·규칙은 이 SKILL.md 안에 있다.
