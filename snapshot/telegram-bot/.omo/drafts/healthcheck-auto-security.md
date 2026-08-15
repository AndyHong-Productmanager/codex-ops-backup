---
slug: healthcheck-auto-security
status: awaiting-approval
intent: clear
review_required: false
pending-action: write .omo/plans/healthcheck-auto-security.md
approach: "민감 의료정보를 처리하는 로컬 Electron 앱의 최소 보안기준을 권한·데이터·감사·운영 통제로 분리해 단계 도입한다."
---

# Draft: healthcheck-auto-security

## Components (topology ledger)
| id | outcome (one line) | status | evidence path |
| --- | --- | --- | --- |
| 1 | 처리 범위·보존기간·외부 AI 전송 여부를 확정하고 식별정보를 최소화한다. | active | `src/main.js:218-284`, `src/core/reading-engine.js:352-401` |
| 2 | 직원·의료인·조직관리자·운영관리자 권한을 분리하고 최종확정은 검증된 의료인만 수행하게 한다. | active | `scripts/setup-supabase.sql:1-26`, `src/main.js:754-763` |
| 3 | 로컬 원본·이력·학습 코퍼스·내보내기와 전송 경로를 암호화·통제한다. | active | `src/main.js:46-59`, `616-694`; `src/core/auth-session-store.js:15-117` |
| 4 | 조회·변경·내보내기·관리자 행위의 위변조 방지 감사증적을 남긴다. | active | `src/main.js:264-284`, `scripts/setup-supabase.sql:1-26` |
| 5 | Electron·배포·운영 통제를 강화하고 보안 검증과 대응 절차를 갖춘다. | active | `src/main.js:69-70`, `324-328`; `package.json:26-38` |

## Open assumptions (announced defaults)
| assumption | adopted default | rationale | reversible? |
| --- | --- | --- | --- |
| 데이터 성격 | 실제 환자 식별정보와 건강검진·판독 정보를 처리한다고 본다. | 현재 코드가 원본 CSV, 판독문, 결과·이력을 보관한다. | 예 |
| 배포 모델 | 병원 내부 PC 단독 설치이되 인터넷 기반 Supabase·Claude 기능은 유지 중으로 본다. | 실제 HTTPS/Supabase와 Claude CLI 흐름이 존재한다. | 예 |
| 의료인 인증 | '최종 소견 확정' 권한에만 의료인 검증을 묶고, 일반 입력 권한과 분리한다. | 자격 확인은 일반 PIPA 요건보다 임상 책임 통제에 가깝다. | 예 |

## Findings (cited - path:lines)

- `history.json`과 백업에 `results`, `mappingResults`, `rawRecords`를 평문 저장한다. 세션 토큰만 OS 안전저장소로 암호화한다: `src/main.js:218-284`; `src/core/auth-session-store.js:15-117`.
- 저장소와 작업 산출물에 실제 환자 데이터로 명시된 테스트·골든·데모 파일이 있어, 운영 앱뿐 아니라 개발·테스트 환경도 같은 민감정보 통제 범위다: `docs/reports/staff-check-verification-2026-07-01.md:8-12,27-31`; `docs/reports/2026-07-10-ecg-data-crosscheck.md:4-9,51-54`.
- CSV/XLSX 원본, 렌더러 상태, 클립보드·HTML/CSV/XLSX 내보내기·인쇄가 별도 유출면을 만든다: `src/main.js:483-578`, `616-694`; `src/preload.js:29-34`.
- Supabase는 이메일/비밀번호 인증과 전역 규칙 읽기 RLS만 있으며 역할·의료인 자격·조직 분리·관리자 권한이 없다: `src/core/supabase-client.js:28-93`; `scripts/setup-supabase.sql:9-26`.
- 최종확정 IPC는 인증·자격·역할을 강제하지 않는다. 현재 `doctor_confirm`은 권한증명이 아닌 워크플로우 메타데이터다: `src/main.js:754-763`; `docs/rules/04-ai-reading-rules.md:49-51,78-89`.
- CT/초음파 판독문과 기존 예시가 Claude CLI 프롬프트에 들어간다. stdin·비영구 세션 옵션은 적용되어 있으나 외부 처리·보존 통제는 구현되지 않았다: `src/main.js:715-735`; `src/core/reading-engine.js:213-256,352-401`.
- 감사 로그 저장소와 접근기록 보존·위변조 방지 구현이 없다: `scripts/setup-supabase.sql:1-26`; `src/main.js:264-284`.
- Electron은 `contextIsolation`과 `nodeIntegration: false`는 적용했지만 GPU sandbox를 비활성화한다. 배포 파일에 `.env`가 포함된다: `src/main.js:69-70,324-328`; `package.json:26-38`.
- 개인정보 보호법 제16조는 목적상 최소 수집을, 제29조 및 시행령 제30조는 권한 제한·인증·안전한 저장/전송·접속기록 보관·물리적 조치를 요구한다. 건강정보는 민감정보이며 의료법은 의료인이 업무 중 알게 된 정보를 누설하지 못하게 한다.

## Decisions (with rationale)

1. **로컬 설치형도 적용 대상이다.** 설치 위치가 아닌 개인정보 처리 여부가 기준이며, 이 앱은 건강정보와 환자 식별정보를 로컬에 보관·조회한다.
2. **P0은 외부 AI 전송 통제와 평문 이력 차단이다.** 현재 기능은 실질적으로 인터넷 연결형이며, TLS만으로 외부 처리 적법성·계약·보존 통제가 충족되지는 않는다.
3. **RBAC·관리자 통제·접근로그는 필요하다.** 다만 단일 PC·단일 사용자 버전은 병원 OS 계정과 앱 사용자 1:1 결합으로 시작할 수 있고, 공유 설치·다중 사용자 버전에는 서버 강제 RBAC가 필수다.
4. **의료인 인증은 조건부 필수다.** 단순 보조 도구라면 일반 개인정보보호 의무와 별개지만, 의사 이름으로 최종확정·서명·진료기록 반영을 허용한다면 자격 검증과 승인 흔적이 필요하다.
5. **전자 의무기록 해당성은 운영정책 확인이 필요하다.** 이 앱이 법정 진료기록의 원본을 작성·보관하는지 여부에 따라 의료법·EMR 고시 적용 범위가 확대된다.

## Scope IN

- 데이터 항목·보존·파기·AI 전송·수탁/국외 이전 판단을 포함한 처리대장과 최소화 정책
- 사용자·조직·의료인·관리자 역할 모델, 자격 검증 원천, 권한 변경/회수 및 최종확정 권한 게이트
- 로컬 저장 암호화, 키 관리, 파일/내보내기/클립보드 통제, HTTPS·인증서 검증·외부 AI 전송 차단 또는 비식별화
- 접근·감사 로그의 이벤트 모델, 위변조 방지·보존·조회 권한, 관리자 행위 감시
- Electron 샌드박스·IPC·배포 비밀·OS/설치 환경·백업/복구·사고 대응과 보안 테스트
- 저장소·개발 PC의 실환자 데이터 및 파생 산출물 인벤토리, 격리·파기 또는 승인된 비식별 테스트셋 전환

## Scope OUT (Must NOT have)

- 진단 정확도·의료적 유효성 검증 자체
- 실제 환자 데이터를 사용한 테스트·마이그레이션
- 법률자문을 대체하는 적법성 최종 판정

## Open questions

1. 이 앱은 **법정 진료기록/전자의무기록의 원본**을 작성·보관합니까, 아니면 EMR 입력 전 보조 도구입니까?
2. Claude 기능에 **식별 가능한 판독문·검사 결과를 외부 전송**하는 것을 허용합니까? 허용 시 이용 병원·국가·계약/처리방침을 확정해야 합니다.
3. 실제 운영은 **단일 PC·단일 사용자**입니까, 아니면 한 병원 내 여러 PC·직원/의사가 함께 사용합니까?

## Approval gate
status: awaiting-approval

승인 시 위 5개 컴포넌트에 대해 P0/P1/P2 순서, 파일별 변경 지점, 마이그레이션·검증·롤백 기준을 담은 실행 계획을 `.omo/plans/healthcheck-auto-security.md`에 작성한다.
