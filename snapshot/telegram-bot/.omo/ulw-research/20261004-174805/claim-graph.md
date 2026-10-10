# 주장 그래프

관찰 기준일: 2026-10-04. 출처는 sources-ledger.md, O 번호는 observation-manifest.md에 대응한다. 동일 문서 복제본과 같은 당사자의 페이지를 독립 근거로 중복 계산하지 않는다.

## verified-claims

| claim_id | 허용 명제 | 상태 | 범위 제한 |
|---|---|---|---|
| C01 | CBNX ASIA가 아시아 대표 및 과거 JV 관계를 공개적으로 설명한다. | supported | 계약·독점 범위는 U01 |
| C03 | 법원 기록에 Ardmore의 과거 Cokonyx 제조 사실관계가 있다. | supported | 현재 CBNX 실적 아님 |
| C04 | GFEZ가 2017-04-24 투자협약을 기록한다. | supported | 소유·이행은 U04 |
| C05 | WV Commerce가 2013-11-21 Millwood 계획을 발표했다. | supported | 가동 완료 아님 |
| C06 | 경매업체 기고가 Millwood 미점화 설비와 공매 계획을 서술한다. | supported | 보도 존재, 사업 결과는 partial |
| C07 | 현재 carbonyx.com은 Carbonyx Minerals를 소개한다. | supported | 법적 무관계까지 단정하지 않음 |
| C08 | 과거 아카이브에 CASP·Cokonyx와 Plano·Ardmore 소개가 있다. | supported | 역사적 자기소개 |
| C09 | SEC Form D 발행인은 Carbonyx International USA, Inc.다. | supported | 신고 내용, SEC 보증 아님 |
| C10 | Carbonyx Inc.의 파산 문서와 확인명령 복제문이 있다. | supported | 문서 확인, CBNX 승계 아님 |
| C11 | 그룹 소개가 설립연도와 인물을 설명한다. | supported | 자기소개 존재만 확정 |

## 노드 공통 필드

claim type: 비코드 공개자료 명제. risk tier: high. observed_at: 2026-10-04. independent observation groups는 조사자 수가 아닌 출처 독립성도 함께 평가한다. counter-search는 기존 조사 파동의 반증 대조를 의미하며 조립 단계에서 새 검색을 실행했다는 뜻이 아니다. 아래 문서 존재 명제에 대한 단일 1차 예외를 법적 실질 명제의 검증으로 확대하지 않는다.

## C01: 대표·JV 공개 설명
- statement/scope: 현행 CBNX ASIA와 과거 아카이브의 관계 설명 존재.
- valid_at: 현행 관찰일, 2024-03-19 아카이브. intent ids: I-01,I-03.
- supporting observations: O001,O003,O007,O019. contradicting: 없음, 대표와 JV 표현의 차이는 존재.
- groups: root-primary,official-identity,rendered-web-trace. domains: cbnxasia.com,web.archive.org. 같은 당사자 내용으로 실질 독립 아님.
- convergence: 단일 1차 예외. 발언의 존재를 검증하므로 당사자 원문이 적합.
- counter-search: 정부·법원·SEC 대조는 계약이나 지분을 증명하지 못함.
- primary backing: S1,S3,S7/S19. dependencies: 없음. status: supported(자칭 사실),partial(실질 관계). final synthesis location: 요약·식별.

## C02: 법적 동일·후신 관계
- statement/scope: CBNX GROUP LLC가 Carbonyx International Inc.의 법적 후신이라는 주장.
- valid_at: 현행. intent ids: I-01,I-03. supporting: O003. contradicting: O008,O010,O013은 다른 명칭과 승계 연결 부재를 보여줌.
- groups: official-identity,registry-history,root-legal. domains: cbnxasia.com,sec.gov,law.justia.com,casemine.com.
- convergence: 불충족. counter-search: 법인명과 파산·IP 처리 대조로 후신 연결을 확보하지 못함.
- primary backing: S3 당사자 주장; 변경·양도 원본 없음. dependencies: U02,U05. status: unresolved. final synthesis location: 미해결 부록.

## C03: Ardmore 역사적 제조
- statement/scope: 법원 의견이 2010년 Ardmore Cokonyx 제조 사실관계를 서술.
- valid_at: 2014년 의견의 2010년 사실관계. intent ids: I-02. supporting: O009,O020. contradicting: 없음.
- groups: root-legal,registry-history. domains: law.justia.com,govinfo.gov. 같은 의견이므로 하나의 원천.
- convergence: 법원 의견 단일 1차 예외. counter-search: Millwood 미가동 보도는 다른 시설이므로 반박이 아님.
- primary backing: S20 공식 보관, S9 복제. dependencies: 없음. status: supported. final synthesis location: 연표·상세.

## C04: 한국 투자협약
- statement/scope: GFEZ의 Carbonyx International 협약 기록.
- valid_at: 2017-04-24. intent ids: I-02,I-03. supporting: O018,O004; O001 맥락 보조. contradicting: 없음.
- groups: rendered-web-trace,root-primary. domains: gfez.go.kr,cbnxasia.com.
- convergence: 정부 기록 단일 1차 예외. counter-search: 기록의 당사자에 CBNX ASIA 소유권이 있는지 대조, 증거 없음.
- primary backing: S18; S4 경로를 보완. dependencies: 없음. status: supported(기록),unresolved(이행). final synthesis location: 연표·상세.

## C05: Millwood 발표
- statement/scope: WV Commerce의 Millwood 계획 발표.
- valid_at: 2013-11-21. intent ids: I-02. supporting: O012,O011,O002. contradicting: 2014년 최초 발표라는 해석.
- groups: registry-history,root-primary. domains: prweb.com,wvlegislature.gov.
- convergence: 기관 발표와 후속 정부 기록. counter-search: 더 이른 S12로 S11의 최초 발표 해석 정정.
- primary backing: S12 기관 작성 배포문, S11,S2 정부 기록. dependencies: 없음. status: supported. final synthesis location: 연표·상충.

## C06: Millwood 경매업체 설명
- statement/scope: 경매업체가 new/never fired 설비와 공매 계획을 서술.
- valid_at: 2022-06-14 기고, 완료일 아님. intent ids: I-02. supporting: O015,O014. contradicting: 정부 계획을 가동으로 읽는 해석.
- groups: registry-history,rendered-web-trace. domains: constructionequipmentguide.com,wvtrades.org.
- convergence: 보도 수준 수렴, 전체 사업 결과 확정 아님. counter-search: S12와 S14,S15 대조, 건설·공매 날짜 차이 미해소.
- primary backing: S15는 경매업체 자기 설명의 원문. dependencies: U03. status: supported(서술 존재),partial(결과). final synthesis location: 연표·상충.

## C07: 현재 도메인
- statement/scope: 현재 carbonyx.com의 Vancouver Carbonyx Minerals 소개.
- valid_at: 2026-10-04 관찰, UBC 프로필 2026-02-10. intent ids: I-01,I-03. supporting: O016,O017. contradicting: 과거와 같은 사업자로 합치는 해석.
- groups: rendered-web-trace,official-identity. domains: carbonyx.com,innovation.ubc.ca.
- convergence: 회사와 외부 대학 프로필. counter-search: O005 아카이브와 사업·장소 설명 대조.
- primary backing: S16,S17. dependencies: 없음. status: supported(현행 식별). final synthesis location: 요약·식별.

## C08: 과거 도메인
- statement/scope: CASP·Cokonyx 및 Plano·Ardmore 소개의 존재.
- valid_at: 2019-01-31 아카이브. intent ids: I-01,I-02. supporting: O005. contradicting: O016 현행 내용과 다름.
- groups: official-identity. domain: web.archive.org. convergence: 자기소개 존재의 단일 1차 예외.
- counter-search: S16 대조로 현재 사실 오인 방지. primary backing: S5. dependencies: 없음. status: supported(소개 존재),partial(실질). final synthesis location: 식별·연표.

## C09: SEC 발행인
- statement/scope: Form D의 발행인과 설립연도·인물 신고 내용.
- valid_at: 2011-02-02 제출, 2010 설립 기재. intent ids: I-01,I-02. supporting: O010. contradicting: O003 명칭과 USA 유무 차이.
- groups: registry-history. domain: sec.gov. convergence: 공시 내용의 단일 1차 예외.
- counter-search: 그룹 페이지 명칭과 대조해 다른 이름을 합치지 않음. primary backing: S10. dependencies: 없음. status: supported(신고 내용). final synthesis location: 식별·연표.

## C10: 파산 문서
- statement/scope: Carbonyx Inc. 사건 문서와 확인명령 복제문 존재.
- valid_at: 2021-06-01,2021-08-11. intent ids: I-02,I-03. supporting: O006,O013. contradicting: 없음.
- groups: registry-history. domains: cdn.pacermonitor.com,casemine.com. convergence: 관련 문서, 모두 제3자 경로.
- counter-search: IP 처리와 CBNX 명칭 대조, CBNX 승계 근거 없음.
- primary backing: 법원 제출·명령 복제, 공식 원본 대조 한계 명시. dependencies: 원본·자산 목록. status: supported(문서 존재),partial(법적 효과). final synthesis location: 연표·상충·부록.

## C11: 설립·인물 설명
- statement/scope: 그룹 소개의 2000년 설립, 현행 CEO 표시.
- valid_at: 현행 페이지의 과거 서술. intent ids: I-01,I-02. supporting: O001,O003,O008. contradicting: 없음.
- groups: root-primary,official-identity,root-legal. domains: cbnxasia.com,law.justia.com.
- convergence: 당사자 발언 존재의 단일 1차 예외, 설립연도 독립 확정 아님.
- counter-search: 법원·SEC 식별 대조, 모든 유사 법인의 설립일로 확장 금지.
- primary backing: S1,S3, 역사적 역할 S8. dependencies: 없음. status: supported(설명 존재),partial(연혁). final synthesis location: 식별·연표.

## 미해결 부록

| id | 주장 | 미해결 이유 | 필요한 근거 | 상태 |
|---|---|---|---|---|
| U01 | 아시아 독점권·JV 범위 | 계약서 없음 | 계약·지분·유효기간 | unresolved |
| U02 | CBNX 법적 후신 | 명칭 차이, 양도 사슬 없음 | 변경·합병·양수도 기록 | unresolved |
| U03 | Millwood 상세 사업 결과 | 날짜 상충, 공적 원장 부족 | 가동·공매·대출 기록 | unresolved |
| U04 | 한국 협약 소유·이행 | 연혁은 체결 기록 | 협약·후속 이행 문서 | unresolved |
| U05 | CASP 현 권리·라이선스 | 특허별 사슬 없음 | 특허 양도·계약 원본 | unresolved |

## 의존 관계

C01 → U01, C02 → U02/U05, C04 → U04, C05+C06 → U03. C03의 Ardmore와 C06의 Millwood는 서로 다른 시설이다. C07과 C08은 관찰 시점이 다르므로 도메인만으로 법적 연속성을 만들지 않는다.
