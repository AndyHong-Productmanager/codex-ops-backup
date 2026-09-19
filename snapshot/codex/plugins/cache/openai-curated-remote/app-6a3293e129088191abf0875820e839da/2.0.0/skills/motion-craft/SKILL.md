---
name: motion-craft
description: >
  Specify native motion for Higgsedit compositions: frame choreography, raw
  property tracks, token text entrances, shared timelines, sampled curves,
  steps and bounded counters. Use when designing how frames or text animate.
  For project assembly, footage editing and rendering, use video-editing.
metadata:
  source_revision: "5073f3a09d3f6b0469db9ff7e8a9df0d339f743a"
---

# Motion Craft

Use native composition motion only. There is no HTML animation, CSS, expression evaluator, runtime callback, or playback physics clock.

## Runtime and loading

Use the installed `$video-editing` skill for project creation, sandbox execution,
media transfer and rendering. Inspect the installed CLI help and `types/fable.d.ts`
before selecting APIs: a newer skill does not update the hosted renderer. Use only
supported native motion; frame choreography and shared timelines below require a
matching CLI. On older versions, use supported raw tracks for equivalent behavior
or explain the specific missing capability. Do not upgrade the shared runtime.

Read only the references needed for the selected motion technique. Start with the
relevant timing or layout contract; do not load all eight references by default.

## Motion APIs

- Frame choreography: set `motion` on `frame(...)` or `<frame motion={...}>`. It supports named `poses`, local `cues`, `enter`, `settle`, `exit`, and literal `motion.timeline` data. Pose fields are `x`, `y`, `scale`, `scaleX`, `scaleY`, `opacity`, and `rotation`.
- Raw tracks: set `animate: [{ property, from, to, at, duration, easing }]` or use `keyframes: [{ at, value, easing? }]`. Use raw tracks for properties outside the frame-pose set.
- Token text motion: `<text motion={{ by: "word", from: { opacity: 0, y: 20 }, at: 0, duration: 0.4, overlap: 0.5, easing: "house" }}>Text</text>`. `by` is `"character" | "word" | "line"`; accepted easing is `"linear" | "ease-out" | "house"`.
- Shared choreography: one timeline leaf can bind the same progress to multiple immediate child frames through `targets`. A pose-only leaf remains continuously interpolated. If any binding is a `counter`, the whole leaf uses held samples at scene fps, including pose bindings, with at most 256 samples.

Choreography compiles into editable native property tracks and bounded text states when the script builds. Rebuilding the script recompiles it; human timeline edits do not rerun choreography.

## References

- [Timing and phases](references/timing.md)
- [Easing and sampled curves](references/easing.md)
- [Token text motion](references/typography.md)
- [Frame layout and transforms](references/composition.md)
- [Timelines, targets, and cues](references/causality.md)
- [Steps and counters](references/stepped.md)
- [Raw animation forms](references/recipes.md)
- [Validation and limits](references/qc.md)
