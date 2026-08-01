# Observation Manifest

| observation_id | source | evidence layer | observer group | independence basis | observer | observed_at | valid_at | artifact | anchor | contamination notes |
|---|---|---|---|---|---|---|---|---|---|---|
| O-01 | 사용자 제공 서울시 민원 안내 URL | primary administrative | parent | 서울시 원문 | parent | 2026-07-30 | current check pending | pending | pending | 없음 |
| O-02 | 서울시 조직도 검색 | primary administrative | seoul_forms | 서울시 조직도 원문 | seoul_forms | 2026-07-30 | 2026-07-30 | URL recorded in wave report | 민원처리2팀·02-2133-7922 | 신규 담당 연락처 확인 |
| O-03 | 국가법령정보센터 「신문 등의 진흥에 관한 법률」 | primary legal | statutory | 현행 법령 원문 | statutory | 2026-07-30 | 2025-10-01 시행 | https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq=277349 | 제9조·제39조 등 | 없음 |
| O-04 | 국가법령정보센터 「신문 등의 진흥에 관한 법률 시행령」 | primary legal | statutory/current_form | 현행 법령·별지 서식 | statutory,current_form | 2026-07-30 | 2026-03-24 시행 | https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq=284795 | 제2조·제4조·별지 제1호 | 별지 표기는 2019 개정이나 현행 배포본 |
| O-05 | 서울시 민원편람 연결 HWP 2건 | primary administrative | seoul_manual,expand_seoul_intake | 실제 다운로드 응답 | seoul_manual,expand_seoul_intake | 2026-07-30 | 2026-07-30 | request log | 법정서식·작성예시 | 두 파일 모두 HTTP 500, 내용 미인용 |
| O-06 | 정부24 신문·인터넷신문 사업 등록 | primary administrative | expand_tax | 정부24 민원 안내 | expand_tax | 2026-07-30 | 2026-07-30 | https://www.gov.kr/mw/AA020InfoCappView.do?CappBizCD=13700000050 | 수수료 없음·처리 안내 | 없음 |
| O-07 | 서울 ETAX 등록면허세 안내 | primary tax | expand_tax | 서울시 세무 안내 | expand_tax | 2026-07-30 | 2026-07-30 | https://etax.seoul.go.kr/jsp/LcnsTaxMnAction.tran?gl_gubun=g&gnb_id=020202&lnb_id=020202 | 제4종 27,000원 | 납세지·정기분은 세법으로 교차 확인 |
| O-08 | 지방세법·시행령 별표 | primary tax | expand_tax | 현행 법령 원문 | expand_tax | 2026-07-30 | current | links recorded in wave report | 면허분 분류·납부 시점 | 없음 |
| O-09 | 헌법재판소 결정례 | primary judicial | statutory | 결정례 원문 | statutory | 2026-07-30 | historical | PDF 근거 목록 11번 | 과거 5인 요건의 위헌 배경 | 현행 요건 판단에는 O-04 우선 |
