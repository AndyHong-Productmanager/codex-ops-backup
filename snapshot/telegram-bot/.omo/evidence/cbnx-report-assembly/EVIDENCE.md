# CBNX 보고서 조립 증거

산출물 루트: `/home/ubuntuhong/dev/codex-telegram-bot/.omo/ulw-research/20261004-174805/`.

현재 ulw-loop attempt 조회는 `ULW_LOOP_PLAN_MISSING`을 반환했다. 따라서 이 검증 기록은 `.omo/evidence/cbnx-report-assembly/`에 기록한다. 본문 및 캡처는 의뢰받은 조사 디렉터리에 둔다.

| 성공 기준 | 실제 시나리오와 실행 | 이진 관찰값 | 캡처 증거 |
|---|---|---|---|
| 한국어 HTML·PDF·종합·주장 그래프 | `node .omo/ulw-research/20261004-174805/assemble.mjs`, 주장 그래프 편집 | 요청 산출물 존재, 빈 파일 아님 | report.html, report.pdf, SYNTHESIS.md, claim-graph.md |
| A4, 한국어 고딕체 | `pdfinfo report.pdf`, `pdffonts report.pdf` | A4, 7 pages, NotoKRPDF 글꼴 모두 embedded yes | 이 디렉터리 pdfinfo.txt, pdffonts.txt |
| 정확히 두 개의 코드 도표 | omowright에서 document.images와 naturalWidth 확인 | 두 이미지 모두 complete true, 자연 크기 양수 | 조사 디렉터리 asset-manifest.json, assets/timeline.svg, assets/relationship.svg |
| 정적·배치 검사 | `node /home/ubuntuhong/.codex/plugins/cache/sisyphuslabs/omo/5.1.15/skills/ulw-research/scripts/report-tools.mjs check report.html --design-spec design-spec.md --layout boxes-1280.json` | status pass, layout pass, defects 0 | 조사 디렉터리 defects.json, boxes-1280.json |
| 화면 폭 대응 | `node capture-layout.mjs`, 위 check를 boxes-375.json 및 boxes-768.json에 실행 | 각 폭 status pass, layout pass, defects 0 | boxes-375.json, boxes-768.json, defects-375.json, defects-768.json, screen-375.png, screen-768.png, screen-1280.png |
| Chrome 인쇄 | `google-chrome --headless --no-sandbox --disable-gpu --no-pdf-header-footer --print-to-pdf=<조사 디렉터리>/report.pdf file://<조사 디렉터리>/report.html` | 프로세스 exit 0, 유효 PDF 생성 | report.pdf, 이 디렉터리 pdfinfo.txt |
| 모든 페이지 재렌더 | `pdftoppm -png -r 150 report.pdf pages-final/page` | PNG 7장, 페이지 수와 일치 | pages-final/page-1.png 부터 page-7.png |
| 내용 제한 | 본문·주장 그래프 대조 | 법적 승계·독점권·특허·이행·공매 결과를 미확인으로 분리 | claim-graph.md의 C02 및 U01~U05, report.pdf p.5 |
| 근거 인용 | 모든 논거별 S 인용과 전체 목록 검사 | 출처 장부 20항목, 모든 URL과 열람일 포함 | sources-ledger.md, report.pdf p.6~7 |

## 직접 확인한 페이지

최초 렌더에서 연표 도표만 다음 페이지로 밀려 빈 공간이 크게 남는 결함을 발견했다. 연표 열 폭을 조정하고 전체를 재인쇄하여 7쪽으로 수정했다. 두 번째 검수에서는 과도하게 단정적인 소유 관련 소제목을 발견해 ‘투자협약은 확인, 소유는 미확인’으로 고쳤다.

최종 캡처 전 페이지는 눈으로 확인했다. 관계도와 시계열 도표, 한글 본문, 표, 출처 링크가 렌더링되며 빈 페이지·잘린 행·깨진 한글 글리프는 보이지 않는다. 이후 책임자가 두 독립 검수자에게 전 페이지를 전달했다. 무결성 검수는 PASS/APPROVE, 한글 검수는 PDF PASS를 반환했다. 무결성 검수 원문은 `/home/ubuntuhong/dev/codex-telegram-bot/.omo/evidence/cbnx-visual-integrity-fresh-gate-review.md`이다.

## 제한

정적 검사와 화면 배치 검사는 통과했다. 법적 사실을 실행 코드로 검증했다는 주장은 하지 않는다. 기사는 기사 내용 존재와 독립 자료의 범위 안에서만 사용했다. PDF는 독립 시각 검수를 통과했다. 모바일 HTML 도표는 확대가 필요하며, PDF 7쪽 S12 URL의 마지막 글자만 다음 줄로 내려가는 미관상 한계가 있다. 책임자는 PDF 전용 범위에서 이 항목을 비차단으로 수용하고 현재 산출물을 유지하도록 지시했다. 별도 proofread 도구가 없어 해당 gate는 not_run으로 기록했다.

## 최종 manifest

`outcome verify`: ok true, problems 빈 배열. `outcome finish`: 2026-10-04T09:23:23.241Z, elapsedMinutes 35, sources total 20/domains 15. `outcome.json`의 gate는 static/layout/visual pass, proofread not_run이다. 정확한 브리핑은 이 디렉터리의 `closing-briefing.txt`에 기록했다.

최종 파일 해시와 캡처 해시는 `sha256.txt`에 기록했다.
