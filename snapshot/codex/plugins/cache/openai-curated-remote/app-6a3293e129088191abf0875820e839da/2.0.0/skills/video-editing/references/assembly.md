# Assembly

Use `higgsedit build edit.jsx` for new, unshared projects: it replaces the timeline.
For linked, human-edited, or canonical projects, inspect fresh state and use bounded
`higgsedit do`/`ops` changes.

## Picture and audio

`p.cut(handle, { from, dur, at, fit })` places source media on lane 0 in deployed
v0.14. `from` is source time; `at` is timeline time. Omitted `at` appends in declaration
order. Keep `from + dur` within source duration.

`p.compose(nodes, { at, dur, name, camera })` places native graphics or media overlays. A composed `media` node is picture-only: `muted` and `volume` do not add its source audio. Keep required audio on the spine, extract it separately, or mux/mix after render.

```js
export default async ({ project, text }) => {
  const p = await project({ size: "1080x1920", fps: 30 });
  const source = await p.add("media/source.mp4");
  p.cut(source, { from: 0, dur: 8 });
  p.compose(text("Caption", { fontSize: 64 }), { at: 1, dur: 2 });
  await p.render("renders/final.mp4", {
    depth: 10,
    concurrency: 3,
    codec: "hevc",
    bitrate: 8_000_000,
  });
};
```

Audio cannot share a visual track; the new script lane API is unreleased. Import a bed
once with `p.add`. For standalone edits, after building use `higgsedit do . place
--assetId <id> --at 0 --duration <seconds>`; omit `--trackIndex` for a free lane.
Inspect the lane before track-specific `duck` gain. For already attenuated beds, keep
baseline volume 1; never duck again. `$ai-host-video` places its prepared bed by its own
assembly rules and preserves existing authored cuts. Place once per rebuild, not per
render retry; never stack another bed. Do not invent `p.over` or a post-build shim.

## Native composition

Persistent `<frame>` supports `layout="column"`, `"row"`, `"grid"`, or `"none"`.
Grid columns are equal; spans/`minmax` are unsupported. Child `at`/`duration` use parent-local time within its
half-open lifetime; keyframes use node-local time. No per-frame callbacks.

`components/*.js` exports `meta` and default `render`. Nodes compile at local zero;
only the root is timeline-placed. Components receive builders, not the project API;
import assets first and pass IDs through declared parameters.

Useful commands:

```bash
higgsedit probe media/source.mp4
higgsedit check .
higgsedit build edit.jsx
higgsedit frame . 1.5 --out renders/frame.png
higgsedit render . --workers 3 --out renders/final.mp4
ffprobe -v error -show_entries stream=codec_type renders/final.mp4
```

For a local diagnostic after building the changed edit, render a separate window:

```bash
higgsedit render . --range 12:16 --workers 3 --out renders/repair-window.mp4
```

This does not overwrite `renders/final.mp4` or replace final rendering. Diagnostic
windows are not manual sharding of the master.

## Export options

`p.render(out, options)` supports `draft`, `shards`, `concurrency`, `depth: 8|10`,
`codec: hevc|av1`, `bitrate`, `accel: auto|cpu|gpu`, and `lossless`. Default depth 8
encodes H.264; depth 10 selects H.265 (HEVC Main10) or AV1. Lossless AV1 selection
uses FFV1 in MKV/MOV. CLI export also accepts `--range START:END`.
Use advertised `--workers 3` or `--concurrency 3`, never both (script `concurrency: 3`).
Inspect memory/decoders before increasing parallelism. Never add `--engine`, even from legacy help.

`bitrate` is a positive integer in bits/second. CLI `--bitrate 8M`, `--bitrate 8000k`
and `--bitrate 8000000` all target 8 Mbps of video. `higgsedit build edit.jsx
--bitrate 8M` sets a default; an explicit `p.render` bitrate overrides it. Omission
keeps automatic quality settings. The target is not constant bitrate or an exact file size;
audio/container bytes are extra. A bitrate is incompatible with `lossless`.
Older CLIs can silently ignore bitrate; confirm `--bitrate` appears in their help.

Main10 input decodes directly. Render reports include diagnostics and per-window
eight-bit `fallbacks`; output depth alone does not establish retained precision.
Project size/fps are fixed at creation. Cost depends on media, resolution, effects
and concurrency; there is no fixed render-time estimate.
