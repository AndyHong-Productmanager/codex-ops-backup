# Telegram Codex 라우터 디버깅 이력

기준 시각: 2026-07-30 09:32 KST

## 증상

- Telegram 장기 폴링에서 과거 `HTTP 409 Conflict`가 반복되었습니다.
- Codex 세션의 컨텍스트가 가득 차면 응답이 실패했고, 이후 요청이 같은 실패 세션을 다시 재개할 수 있었습니다.
- 작업 중 들어온 추가 메시지는 빠른 별도 응답 경로를 사용하며, 동시에 하나만 실행되어야 합니다.

## 확인한 사실

- 단일 폴러 잠금 파일은 `/run/user/1000/codex-telegram-bot.poller.lock`이며, 실행 중인 라우터 PID와 일치했습니다.
- Telegram `getMe`과 `getWebhookInfo` 호출은 모두 정상 응답을 반환했고, 대기 업데이트 수는 0이었습니다.
- 로그에는 `context full even on fresh session` 뒤에 실패한 새 세션 ID를 `resume(...)`하는 흐름이 남아 있었습니다.
- 2026-07-30 09:14:27 KST에 수정된 소스로 라우터가 재기동됐습니다. 현재 PID는 `var/router.pid`에서 확인합니다.

## 원인

`run_codex()`는 기존 세션에서 컨텍스트 초과가 발생하면 세션 파일을 지우고 새 세션으로 한 번 재시도합니다. 그러나 그 새 세션도 컨텍스트 초과로 실패하면, 새로 생성된 세션 ID가 `var/codex.session`에 남았습니다. 다음 요청은 이 실패 세션을 다시 재개하므로 동일한 장애를 반복할 수 있었습니다.

## 수정

- `telegram_codex_bot.py`
  - 새 세션 재시도도 컨텍스트 초과로 실패하면 `var/codex.session`을 삭제하도록 변경했습니다.
- `test_telegram_codex_reliability.py`
  - 재시도 실패 뒤 세션 파일이 남지 않는 회귀 테스트를 추가했습니다.

## 검증

- `python3 -m unittest -q`
  - 3개 테스트 모두 통과했습니다.
- `python3 -m py_compile telegram_codex_bot.py telegram_media.py test_telegram_codex_reliability.py test_telegram_media.py`
  - 문법 검사에 통과했습니다.
- Telegram API 상태 점검
  - 봇 식별 및 웹훅 상태 조회가 정상 응답을 반환했습니다.
- 재기동 점검
  - 사용자 systemd 일회성 작업이 성공했고, 수정된 라우터가 2026-07-30 09:14:27 KST에 시작된 것을 로그에서 확인했습니다.

## 운영 메모

- `409 Conflict`는 둘 이상의 `getUpdates` 클라이언트가 동시에 폴링할 때 발생합니다. 현재는 파일 잠금으로 단일 라우터 실행을 보장합니다.
- 컨텍스트 초과가 한 번 발생하면 다음 메시지는 새 세션에서 처리됩니다. 새 세션도 실패한 경우에도 실패 세션을 보존하지 않습니다.
- 긴 작업 중 추가 메시지는 본 작업과 분리된 빠른 응답으로 처리되며, 동시 실행 수는 1개로 제한됩니다.
