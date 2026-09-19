# Аудит переноса AI Host в OpenAI skills

Проверено 8 сентября 2026 года. Это инженерный отчёт для ревью PR, а не инструкция,
которую нужно загружать при создании каждого видео.

## Вывод

Предыдущий перенос был неполным: Python-помощники зависели от другого способа доставки
и исполнения, а часть инструкций продолжала обещать их работу. Исправленная версия
использует существующие MCP-инструменты, установленный Higgsedit и короткие команды
для конкретного эпизода. Все 29 Python-файлов, включая тесты помощников, удалены.
В конечном diff остаются только Markdown и `agents/openai.yaml` трёх скиллов.

Отсутствие Python у соседей само по себе не запрещает scripts в формате skill.
Ошибка была в несовместимости перенесённого исполнения с выбранным OpenAI окружением.
Здесь выбран именно вариант без поставляемого исполняемого пакета. Установленная
библиотека faster-whisper может использоваться через task-specific sandbox-команду;
это не добавление Python-файлов, MCP-инструментов или серверных ресурсов в репозиторий.

Не заявляем готовность к поставке: штатные упаковщик/playground/preflight всё ещё
ожидают фиксированный набор из 15 скиллов и отклоняют 18. Их исправление находится
вне разрешённых `skills/openai`, поэтому оно не включено. Платная сквозная генерация
и проверка фактического hosted sandbox не выполнялись.

## Проверенные ревизии

- Исходник Higgs-Pi: свежий `origin/develop`
  `5073f3a09d3f6b0469db9ff7e8a9df0d339f743a`, AI Host **1.2.1**.
  Путь: `apps/higgsfield/src/skills/workflow-generation/ai-host-video`.
- Отдельные исходные craft-скиллы: `apps/higgsfield/src/skills/media/motion-craft`
  и `apps/higgsfield/src/skills/media/youtube-script`. Между предыдущей проверкой
  `57c7f31c3` и свежим develop они не менялись.
- База локальной ветки FNF: `50d1d1bb275f4629eb1fb44428c662b4d59fa0fe`,
  существующий OpenAI `video-editing`, native Higgsedit **0.14.0**.
- Дополнительно fetched/reviewed FNF `origin/develop`
  `272eaab534f15067b95b949233365ed0f73a3a2a`. Новые изменения добавляют website workflow
  tools и маркетинговый widget; они не меняют проверенные generation/media/renderer
  контракты и не подключают AI Host. Website-only workflow loader не может доставить
  произвольный новый creative skill.

Репозиторий Higgs-Pi не изменён. Ветка для ревью:
`skills/openai-ai-host-video-develop`, PR #929 в `develop`; слияние не выполняется.

## Как собраны соседние OpenAI skills

Инвентаризация охватила все 15 существовавших скиллов и три добавленных. В базе было
169 файлов и ни одного `.py`. Обычная структура — `SKILL.md` с YAML frontmatter,
`agents/openai.yaml` для карточки, тематические `references/`, иногда `assets/`.
Наличие дополнительных ресурсов не означает, что они автоматически устанавливаются
в удалённый sandbox. Скиллы обращаются к реальным MCP API и установленным утилитам.

В качестве главного технического образца использован существующий `video-editing`:
121 строка entrypoint, 13 тематических справочников и карточка. Его ссылки на native
help/types, ephemeral sandbox и reserve → PUT → confirm перенесены в контракт AI Host.
Творческие требования сохранены в справочниках, runtime-операции переписаны.
Обязательный OpenAI runtime contract расположен непосредственно в `SKILL.md`,
как у `ad-multiplier`; отдельный runtime reference удалён, входящие ссылки обновлены.

| Skill | Строк в SKILL.md | Markdown references | Всего файлов | Python |
|---|---:|---:|---:|---:|
| `ad-multiplier` | 257 | 2 | 4 | 0 |
| `ai-host-video` | 288 | 26 | 28 | 0 |
| `brand-asset-creation` | 168 | 24 | 26 | 0 |
| `faceless-video` | 618 | 13 | 16 | 0 |
| `motion-craft` | 46 | 8 | 10 | 0 |
| `narrator` | 244 | 1 | 4 | 0 |
| `product-photoshoot` | 246 | 15 | 17 | 0 |
| `subtitles` | 292 | 0 | 3 | 0 |
| `thumbnail-generation` | 414 | 2 | 4 | 0 |
| `ugc-product-video` | 233 | 4 | 6 | 0 |
| `ugc-review-video` | 325 | 6 | 8 | 0 |
| `ugc-try-on-video` | 230 | 5 | 7 | 0 |
| `ugc-tutorial-video` | 209 | 5 | 7 | 0 |
| `ugc-unboxing-video` | 216 | 5 | 7 | 0 |
| `ugc-website-video` | 225 | 7 | 9 | 0 |
| `video-editing` | 121 | 13 | 15 | 0 |
| `website-builder` | 234 | 34 | 36 | 0 |
| `youtube-script` | 147 | 12 | 14 | 0 |

У новых скиллов валидные `name`/`description`, description не превышает 1024 символа,
карточка использует `$skill-name`, `policy.allow_implicit_invocation: true`.
Нет Higgs-Pi `ui.yaml`, нового tool manifest, `type:` в карточке или переименования
identity. `video-editing` используется как существующая зависимость, не копируется.
`video-caption-titler` не переносится.

## Найденные ошибки и исправления

| Область | Дефект предыдущего переноса | Исправление |
|---|---|---|
| Исполнение | Вызовы недоставленных Python-помощников | Удалён весь `scripts/`; операции описаны через существующие инструменты/CLI |
| Запросы | Внутренние `output_slot`, `duration_policy`, вложенные model params | План отделён от запроса; single `{params: request}`, batch `{requests:[{index,params}]}` |
| Медиа | Backend role aliases вместо OpenAI enum | Канонические `image`, `video`, `audio` и допустимые source ids; другие роли только по схеме модели |
| Batch | Риск повторной отправки успешных соседей | Не более 6 запросов, стабильные индексы, `count:1`, фиксация частичных результатов |
| Poll/display | Статус lookup смешивался с отказом генерации | Группы до 8, реальные интервалы; permanent lookup отдельно; показ набора до 24 ids |
| Retry | Разные пределы повторов, URL-less и ASR mismatch как причины reroll | Одна политика: принятые jobs не повторяются; творческая замена отдельным индексом с сохранением оригинала |
| Модели | Угаданные aliases/options, неподтверждённые «4K на 3% лучше» | Live catalog/schema; фактические ограничения duration и настроек |
| Состояние | Предположение о постоянном sandbox и custom checkpoint service | Реальная ZIP-процедура с reserve/PUT/confirm в производящем вызове, без повторного ZIP на каждом status poll |
| Upload | Риск отправки локального пути как attachment или неверного чтения response | Настоящий attachment descriptor; confirmed URLs из `results`; id/type/MIME из ответа |
| Тайминги | Автоматические bounds/spine/anchors без работающего resolver | Явная транскрипция с word timestamps, проверка trims и формула source → master |
| ASR | Повторная транскрипция при исправлении phrase selector | Переиспользование transcript; новая транскрипция только для новых/изменённых источников либо реального сбоя |
| Runtime modes | Ветки `platform_resolved`, внутренние callback/shared-editor | Убраны из рабочего протокола, граница явно описана |
| Native API | Старые engine/browser ограничения, compose dry-run, двойной render | Help/types текущего native CLI; build отдельно, один render; реальные кадры вместо выдуманного API |
| Музыка | `p.cut` на отдельный track, которого его API не принимает | Подготовленный WAV импортируется один раз; native `place` на новую аудиодорожку по measured spans |
| Уровень музыки | Риск двойной аттенюации/двойного bed | Gain применяется один раз до native placement; альтернатива FFmpeg только как отдельный раскрытый fallback |
| Motion timing | 96–98% lifetime давал промежутки без видимого значения | Непрерывные границы соседних состояний; source/child/master time разделены |
| Review | Выдуманный reviewer tool, creative prompt для scene-analysis | Собственная проверка доступных evidence; только реальные аргументы video-analysis и честное описание непроверенного |
| Proof | Обещания automatic proof/blank/static reports без помощников | Агент извлекает кадры и excerpts из конкретного encoded master; никаких выдуманных verdicts |
| Approval | Безусловное ожидание script approval и служебные отчёты | Только явно запрошенный checkpoint, настоящая host selection и реальные billing choices |
| Зависимости | Craft как вложенные скиллы в references | `motion-craft` и `youtube-script` самостоятельны, выборочная загрузка техники/жанра |

## Учтённое обновление исходника 1.2.1

Свежие `eba254bce` / `5f05349e3` (PR Higgs-Pi #2420) сверены отдельно от предыдущего
переноса. Сохранено поведение, применимое к OpenAI:

- targeted reads/patches, переиспользование результата после resume;
- один процесс транскрипции/рендера; timeout не означает завершение процесса;
- обложка запускается во время генерации, её job хранится отдельно от build inputs;
- pending cover не задерживает выдачу видео, не вызывает повторную генерацию/рендер
  и не сопровождается обещанием незапланированного follow-up;
- draft только когда нужен для конкретной проверки, без обязательного лишнего render;
- default cap 3 workers при поддержке CLI, финал запрашивает 10-bit при поддержке
  и проверяет реальный результат; деградация явно сообщается;
- подготовленный bed размещается native `place` на отдельной дорожке.

Не перенесены внутренние Python locks/cache/proof helpers и worker callbacks.
Их поведение не выдаётся за существующую автоматизацию: нужные действия агент
выполняет явно. Это функциональная адаптация, а не побайтовое зеркало исходника.

## Что проверено

1. `quick_validate` всех трёх скиллов, frontmatter, YAML-карточки, имена и prompts.
   Относительные файлы и heading anchors проверены автоматически; JSON code blocks
   разбираются. Проверены типы конечных файлов и отсутствие вложенных craft-пакетов.
2. Четыре полных документированных запроса проверены на реальных Zod input schemas
   single и batch API: **8 проверок прошли**. Placeholders заменены тестовыми значениями;
   provider callbacks не вызывались. Это проверка MCP формы, не live model catalog.
3. Существующий `src/tools/generation/openai-tool-schema.test.ts`: **9/9 passed**
   в изолированной локальной копии с mocked provider. Проверяет schemas, batch indices,
   частичные результаты, lookup errors и scene-analysis source XOR.
4. Native Higgsedit 0.14.0 из repository template: синтетический audiovisual source
   30 fps, source trim 0.5–3.5 сек, original-source монтаж, motion и text. Финал:
   **320×180, 3.000 сек, 72 кадра, 24 fps, AAC**. Кадр просмотрен; frame/excerpt
   extraction из encoded MP4 выполнены. Это технический smoke, не оценка AI presenter.
5. Подготовка supplied bed с crossfade, trim, однократным gain и fades; импорт и
   native `place` на отдельную аудиодорожку. Повторный тест соответствующей новой
   функции дал **HEVC, yuv420p10le, 24 fps, 72 кадра, AAC, 3.000 сек**.
   Отдельно проверен FFmpeg mix fallback с копированием video stream.
6. ZIP с originals/project/assets восстановлен в другую директорию; native frame
   успешно построен из восстановленного проекта. Hosted reserve/PUT/confirm не вызывались.
7. `git diff --check` и границы конечного PR diff: только три каталога скиллов,
   без изменений сервера, инструментов, зависимостей и runtime template.

Старые 145 тестов Python-помощников не являются проверкой новой версии и здесь не
используются как доказательство. Временные fixture/test files находятся вне репозитория.

## Оставшиеся ограничения и блокеры

**Упаковка — подтверждённый блокер, не успешно пройденная проверка.**
`package.ts --bundle <текущие skills/openai>` воспроизводимо падает на exact-list
assertion: добавились `ai-host-video`, `motion-craft`, `youtube-script`. Аналогичный
фиксированный список используется в playground validation, preflight и catalog tests.
Потребуется отдельное согласованное изменение этих списков вне `skills/openai`.
В рамках текущего ограничения такие файлы не менялись. Ручная загрузка трёх папок
не доказывает работоспособность штатной упаковки или их появление в marketplace.

**Hosted runtime не проверен end-to-end.** Наличие faster-whisper в template не
гарантирует доступный ASR model, скорость длинного эпизода или полную video/audio
inspection в конкретном host. Поэтому preflight проверяет реальные возможности;
ограничения не маскируются фиктивным PASS. Платная генерация, lip-sync, произношение,
identity consistency и качество конкретного эпизода не были протестированы.

**Локальный shader smoke не прошёл.** Native GLES binary из временной установки
не загружается на этом Mac (`slice is not valid mach-o file`). CPU graphics,
video/audio и HEVC 10-bit smoke прошли; это не доказывает shader support в hosted
sandbox. Skill использует shader только при работающем native runtime и маленьком
реальном preflight. Shared runtime не обновлялся и не патчился.

**Контекст и детерминизм.** AI Host сохраняет подробные творческие справочники.
Root не импортирует весь пакет, а craft dependencies самостоятельны и читаются по
необходимости. Проза не заменяет автоматические гарантии удалённых скриптов:
точные timestamps, requests и проверки теперь зависят от явных действий агента.
Нельзя обещать прежнюю надёжность/латентность только по успешной статической проверке.
