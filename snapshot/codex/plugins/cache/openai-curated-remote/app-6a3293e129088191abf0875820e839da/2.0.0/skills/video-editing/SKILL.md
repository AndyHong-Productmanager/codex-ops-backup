---
name: video-editing
description: |
  Edit supplied footage or author file-backed motion graphics with Higgsedit.
  Activate only for a requested edit or graphics deliverable: cuts, trims,
  soundtrack changes, native layouts, animated text, shaders, overlays or title
  cards. Do not activate when the user only asks to analyze, summarize, describe,
  critique or review a video or YouTube link, including scene-by-scene breakdowns.
  Timeline inspection is supporting work for a requested edit, not a standalone
  activation trigger. Exclude footage generation, generative restyling,
  transcription, subtitle translation/review and ordinary speech-caption
  burning (use subtitles).
---

# Video editing

Higgsedit runs natively in Node; a project holds `project.json`, `media/`, `renders/`.
Flags come from `higgsedit --capabilities` (schema 1) or, on older builds, `--help`;
`types/fable.d.ts` defines script fields (v0.14.0+). Never add `--engine`; use
`--workers N` or `--concurrency N`, never both. Older builds ignore unknown flags
silently, so success alone does not prove a flag applied.

## OpenAI runtime

`sandbox_exec` provides an ephemeral sandbox per call: input downloads, project
creation, rendering and output PUT belong in one command. `media_upload` reserves
an output; `media_confirm` confirms it after a successful PUT. ChatGPT attachment
ingress uses `media_upload_and_confirm`, not a sandbox-local path.

These APIs need the matching native CLI; older sandbox builds may lack them, and a
local install does not update the hosted sandbox. Bitrate needs `--bitrate` in help.

## Capabilities

| Area     | Features                                                                                 |
| -------- | ---------------------------------------------------------------------------------------- |
| Media    | Import images/video/audio; source trims, cuts, fitting and audio mixing                  |
| Layout   | Persistent frames: column, row, equal-column grid, absolute; fill/hug sizing             |
| Graphics | Text, shaped fonts, rectangles, gradients, paths, Lucide icons, masks and mattes         |
| Motion   | Raw keyframes, frame choreography, shared counters, token text, transitions, 2.5D camera |
| Effects  | Standard filters, shadows, motion blur, custom GLSL, image textures, animated uniforms   |
| Output   | Native PNGs, contact sheets, MP4/MOV/MKV, H.264, H.265/HEVC Main10, AV1, target bitrate, editable projects     |

## Script API

Scripts accept JSX/TSX or supplied node builders; no React or DOM runtime.

| Call                                                                     | Result                      |
| ------------------------------------------------------------------------ | --------------------------- |
| `await project({dir, size, fps, background})`                            | Create/open project         |
| `await p.add(file)`                                                      | Import asset; return handle |
| `p.cut(handle, {from, dur, at, fit})`                                    | Place on lane 0             |
| `p.compose(nodes, {at, dur, name, camera})`                              | Place native graphics/media |
| `p.duration()` / `await p.read()`                                        | Timeline length / document  |
| `await p.frame(time, out)`                                               | PNG                         |
| `await p.render(out, {draft, depth, codec, bitrate, accel, shards, concurrency})` | Encoded movie               |

`from` is source seconds; composition `at` is timeline seconds. Frame children
and animations use local seconds. `cut` and `compose` record work synchronously.

```jsx
export default async ({ project }) => {
  const p = await project({ size: "640x360", fps: 24 });
  p.compose(
    <frame
      width={640}
      height={360}
      padding={40}
      motion={{
        enter: { from: { y: 24, opacity: 0 }, duration: 0.4 },
        exit: { to: { opacity: 0 }, duration: 0.2, anchor: "end" },
      }}
    >
      <rect
        width={400}
        height={80}
        fill="#32acff"
        animate={[{ property: "scaleX", from: 0, to: 1, duration: 0.6 }]}
      />
    </frame>,
    { dur: 2 }
  );
  await p.frame(1, "renders/frame.png");
  await p.render("renders/video.mp4");
};
```

## Commands

```bash
higgsedit build edit.jsx
higgsedit inspect PROJECT --id CLIP_ID --at 1.2
higgsedit frame PROJECT 1.2 --out renders/frame.png
higgsedit sheet PROJECT --times 0.1,1,1.8
higgsedit render PROJECT --depth 10 --codec hevc --bitrate 8M --out renders/master.mp4
higgsedit do PROJECT VERB --help
```

`inspect --at` needs an ID or unambiguous name: evaluated parameters, not execution proof.
`doctor` checks dependencies; `check` validates inputs. `fonts list`, `fonts add` and
`icons QUERY` expose catalogs.

## Boundaries

- Whole-script builds replace the timeline. Existing human/shared edits use fresh
  inspection and bounded `do`/`ops`; canonical connections require host credentials.
- Native HEVC Main10 import needs no compatibility transcode. Ten-bit output may
  contain reported eight-bit compositor fallbacks; GLSL pixels are RGBA8.
- No HTML capture, runtime animation callbacks, native LUT, or shader adjustments.
  Browser shader previews are not universally equivalent to native output.
- The OpenAI tool surface supplies no editable-project publishing service.
  An editable local project is not a hosted editor URL.

## References

- API: [composition](references/compose.md), [geometry](references/clip-geometry.md),
  [timing](references/animation-contract.md), [motion](references/motion-language.md).
- Text: [captions](references/caption-titling.md), [caption layers](references/caption-systems.md),
  [titles](references/title-animation.md).
- Projects: [assembly](references/assembly.md), [patch/sync](references/workflows.md),
  [inspection](references/editor-measured.md), [asset identity](references/provenance.md).
- Reference: [composition patterns](references/shot-blueprints.md), [limits](references/failure-modes.md).
