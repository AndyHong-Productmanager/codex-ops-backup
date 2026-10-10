# ULW-Research Synthesis: 산비오의원 지역 검색 미노출

## Executive summary

산비오의원은 외부에서 보이는 범위에서는 크롤링 차단 또는 자바스크립트 빈 페이지 문제가 아니다. `sitemap.xml`의 35개 URL은 200, `index,follow`이며 대표 진료 페이지의 본문도 서버 HTML에 있다. 그러나 홈을 제외한 34개 URL이 모두 홈 `https://sanbo.co.kr/`를 canonical·`og:url`로 선언하고 같은 title/description을 출력한다. 이는 각 진료 페이지가 홈의 중복본이라는 강력한 신호다. Google이 실제로 어떤 URL을 canonical로 선택했는지는 Search Console에서만 확정할 수 있지만, 이 설정은 가장 먼저 고쳐야 할 P0 결함이다. [S1][S3][S4]

두 진료과를 운영하는 사실만으로 교란/패널티가 발생했다는 근거는 없다. 다만 한 홈 페이지가 세 의도(비뇨기과, 산부인과, 부부클리닉)를 모두 대신하고 각 하위 페이지의 식별 신호가 사라져, 지역·진료 조합의 관련성을 축적하기 매우 어렵다. 현 시점의 비개인화되지 않은 Naver 관측에서는 `잠실 비뇨기과` Place 블록에 산비오의원이 보였고 `잠실 산부인과` 초기 Place 블록에는 없었으며, `잠실 부부클리닉`에는 홈과 상담 페이지가 보였다. 이는 “완전 미색인”과 모순되며, 위치·개인화에 따라 바뀌는 순위 관측일 뿐이다.

## Findings by theme

### P0: 색인·정규화

- 35/35 sitemap URL은 200/index-follow이지만, 34개 하위 URL은 홈 canonical, 홈 og:url, 같은 title/description을 선언한다. Google은 잘못된 canonical을 canonicalization 문제로 명시한다. [S1][S3][S4]
- `http`, `https`, `www`, non-`www`가 모두 200이다. canonical 태그가 있어도 서버 301/308 단일화가 더 강한 일관된 신호다. [S4]
- 존재하지 않는 `content.php?co_id` 및 게시글 ID도 200 + 자바스크립트 오류를 반환한다. soft-404 후보이며, 존재하지 않는 리소스는 실제 404/410이어야 한다. [S7]
- sitemap은 35개 URL과 동일 lastmod만 실으며 일부 링크된 페이지/게시글이 빠져 있다. 직접 링크가 있으면 발견은 가능하지만 URL 집합과 수정일을 정확히 유지해야 한다. [S8][S9]

### P1: 지역 의도·콘텐츠

- 홈 H1은 비어 있고, `women`, `treatment`, `examination` 등 하위 페이지 H1은 내부 식별자다. 각 페이지에 단 하나의 자연스러운 한국어 H1과 고유 title/description이 필요하다.
- 현 홈 JSON-LD MedicalClinic은 기관 엔터티용으로는 유효한 방향이지만, 모든 서비스 URL이 같은 기관 정보/메타를 재사용한다. 서비스별 URL에는 본문과 일치하는 `MedicalWebPage`, 의료진 검수/수정일, FAQ·Breadcrumb를 추가한다.
- Naver Place의 주 카테고리는 비뇨의학과다. 산부인과 질의와의 비대칭을 설명할 수 있는 엔터티 단서이지만, 두 과목 운영의 페널티 증거는 아니다. 하나의 실제 장소에 중복 Place를 만들지 말고, 허용되는 대표/부가 진료 정보와 웹사이트·예약·SNS의 NAP를 일치시킨다.

### P2: 성능·사용성

- 브라우저 실측 첫 홈 로드는 최소 25.5 MB/135개 리소스였다. 팝업 PNG와 4개 Pretendard WOFF가 큰 비중을 차지하고 이미지 lazy loading이 없었다. 첫 방문 팝업은 데스크톱/모바일의 핵심 콘텐츠를 덮는다.
- 그러나 서비스 본문은 HTML에 있고, 390px 화면에서 검증한 4개 페이지에는 가로 오버플로·깨진 이미지가 없었다. 구형 GNUboard는 직접 원인이 아니며, 공통 head 템플릿과 자산 운영 방식이 문제다.
- PageSpeed API가 429여서 실제 CWV 실패는 판정하지 않았다. CWV 개선은 전환/UX에 중요하지만 순위 보장을 의미하지 않는다. [S5]

## Prioritized remediation plan

1. **P0, 배포 즉시:** 공통 head의 하드코딩된 canonical/title/description/og:url을 제거한다. 홈은 홈만 self-canonical, `women`, `man`, `treatment`, `faq`, 의료진 등은 각각 현재의 절대 self-canonical을 출력한다. 배포 후 `curl -sS URL | grep -i canonical`으로 최소 10개 URL이 자신을 가리키는지 검증한다.
2. **P0, 동시:** 웹서버에서 모든 `http`와 `www` 요청을 경로·쿼리를 보존하여 `https://sanbo.co.kr$request_uri`로 한 번의 301/308 리다이렉트한다. 없는 DB 레코드는 404/410으로 수정한다.
3. **P0, 1주:** `잠실 비뇨기과`, `잠실 산부인과`, `잠실 부부클리닉`에 각각 고유한 랜딩 URL·title·H1·본문·FAQ·의료진 검수 표기를 만든다. 한 홈의 키워드 나열로 세 검색의도를 대신하지 않는다. 페이지끼리는 상호 링크하되 canonical을 공유하지 않는다.
4. **P1:** 실제 공개 URL만 담고 self-canonical URL과 일치하는 sitemap을 재생성한다. robots의 `/data/`는 공개 팝업/이벤트 이미지 22개를 막지만 진료 페이지 이미지 전체를 막는 것은 아니다. 사내 파일 인벤토리 후 정확한 파일 또는 공개 전용 디렉터리만 Allow한다. [S2][S6]
5. **P1:** Naver Place/Booking/웹사이트/Instagram의 병원명·주소·유선전화·대표 URL을 한 번에 대조한다. Place의 산부인과 정보가 실제 진료와 일치하게 보이는지 플랫폼 정책 범위 안에서 보완한다. 중복 Place 생성은 금지한다.
6. **P1:** 홈의 과도한 팝업을 작은 공지 배너로 축소하고, hero/팝업 이미지를 WebP/AVIF와 적정 크기로 교체한다. 폰트는 WOFF2 서브셋·필요 웨이트만 사용하고, 지도/비주요 이미지/비활성 팝업을 지연 로드한다.

## Verification protocol

Search Console에서 홈·women·man·treatment·새 부부클리닉 URL 각각의 사용자 선언 canonical과 Google 선택 canonical, 색인 상태, 마지막 크롤링을 확인한다. 수정 뒤 중요 URL부터 색인 재요청한다. Google은 canonical 재평가가 최대 약 2주 걸릴 수 있다고 안내한다. [S4]

Naver Search Advisor에는 수정 sitemap을 제출하고, Naver Place는 잠실 인근 비로그인·시크릿 환경과 모바일에서 별도 재관측한다. 같은 SERP를 외부 위치에서 본 이번 조사 수치는 절대 순위로 사용하지 않는다.

## Gaps and access required

- Search Console URL Inspection/Page indexing/CWV 및 Google Business Profile 소유자 접근 없이는 실제 Google 선택 canonical·제외 사유·필드 CWV를 확정할 수 없다.
- Naver와 Google의 지역화·개인화로 한 번의 SERP는 순위 확정 자료가 아니다.
- `/data/` 디렉터리 공개/비공개 파일 분류는 서버/CMS 접근으로만 안전하게 결정할 수 있다.

## Expansion trace

- Wave 1: crawl/index, native SERP/entity, rendered mobile/performance.
- Wave 2: `/data/` 공개 미디어 범위 확인. 진료 콘텐츠의 핵심 원인은 아님으로 축소.
- Wave 3: CSS 배경 이미지 영향은 주 원인 결론을 바꾸지 않는 보조 리드로 종료 대기.

## Sources

[S1] https://sanbo.co.kr/sitemap.xml
[S2] https://sanbo.co.kr/robots.txt
[S3] https://sanbo.co.kr/bbs/content.php?co_id=women
[S4] https://developers.google.com/search/docs/crawling-indexing/canonicalization-troubleshooting
[S5] https://developers.google.com/search/docs/appearance/page-experience
[S6] https://developers.google.com/search/docs/crawling-indexing/robots/intro
[S7] https://developers.google.com/crawling/docs/troubleshooting/http-status-codes
[S8] https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
[S9] https://searchadvisor.naver.com/doc/wmt_guide_ps_websearch.pdf
## Evidence and sources
## Prioritized remediation plan
## Verification protocol
## Gaps and access required
## Expansion trace
