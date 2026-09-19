---
name: product-photoshoot
description: >
  Create finished product photography and product-led brand stills: studio
  packshots, Shopify or catalog images, lifestyle scenes, product-with-person
  closeups, Pinterest pins, hero banners, social carousels, static ad packs,
  virtual-model try-ons, conceptual CGI imagery, and restyles. Use for product
  photoshoots, packshots, e-commerce imagery, and product campaign stills. Do
  not use for Amazon-compliance sets, thumbnails, video ads, portraits, or UGC.
---

# Product Photoshoot

Produce final, polished product stills with the product as the visual hero.
Select one mode, read its local reference plus the shared craft references,
build structured prompts, generate indexed images, optionally inspect them, and show only the final
ledger. Refine observed defects or specific user-requested changes.

## OpenAI runtime contract

- Use only tools exposed by the current OpenAI host and Higgsfield MCP.
- Use `ask_user_input` when that exact callable is exposed,
  `ask_user_input_v3` only when that exact variant is exposed, otherwise ask one
  concise normal-chat question. Never use legacy elicitation names.
- Make at most one intake call containing one to three questions. Keep every
  header at most 12 characters, every prompt to one short sentence, and every
  option label to one to five words. Offer two or three mutually exclusive
  options, put the recommended option first, and rely on the host's free-text
  `Other`; do not add a duplicate Other option.
- Import each user-provided ChatGPT image attachment exactly once with
  `media_upload_and_confirm({type:"image",file:<attachment>})`; reuse the returned
  confirmed `media_id` and do not call `media_confirm` afterward.
- An authorized HTTPS product-image URL may be passed directly as an image
  media value; the generation route imports and confirms it. Reuse a completed
  generation job ID directly when it is already in the current session.
- Use `generate_image_batch` with stable indices and at most six requests per
  call. Every `params.count` is `1`; distinct variants always use distinct
  prompts.
- Wait through `jobs_wait` in groups of at most eight with
  `timeout_seconds:15`. Re-call it only for active or retryable lookup-failed
  jobs; never use a singleton status tool or sandbox sleep.
- Never pass a `submission_failed` entry without a job ID to `jobs_wait`. Retry
  only rejected or failed indices.
- An `unlim_choice` result submitted no job. Ask its exact message and resubmit
  the unchanged request with the user's chosen `use_unlim` value.
- After every final index is terminal, call `show_generation_by_ids` exactly
  once with only the final indexed jobs in order.

## Modes

| Mode | Intent | Read |
|---|---|---|
| `product-shot` | Neutral or styled studio packshot, catalog, Shopify | `references/product-shot.md` |
| `lifestyle-scene` | Product in a real environment or in use | `references/lifestyle-scene.md` |
| `closeup-product-with-person` | Tight product + hands or partial face | `references/closeup-product-with-person.md` |
| `pinterest-pin` | Pinterest-native vertical still | `references/pinterest-pin.md` |
| `hero-banner` | Wide web, email, or campaign header | `references/hero-banner.md` |
| `social-carousel` | 3–10 connected product slides | `references/social-carousel.md` |
| `ad-creative-pack` | Coordinated static paid-social variants | `references/ad-creative-pack.md` |
| `virtual-model-tryout` | Product worn or used by a generated adult model | `references/virtual-model-tryout.md` |
| `conceptual-product` | Surreal, floating, splash, sculptural, CGI-style still | `references/conceptual-product.md` |
| `restyle` | Change an existing image's aesthetic while preserving subject | `references/restyle.md` |

Do not absorb adjacent workflows. Amazon main images, listing infographics, and
A+ content need a compliance-specific workflow. A moving product ad remains a
video-generation request. A YouTube or Instagram video cover belongs to
`thumbnail-generation`. Creator-led reviews, unboxings, tutorials, and video
try-ons belong to the matching UGC skill.

## Intake

Parse the brief before asking: product description or confirmed image,
mode/use case, variant or slide count, visual direction, aspect ratio, exact
text, brand palette, and hands-off intent.

If the user says `full auto`, `auto approve`, `no questions`, `just do it`,
`go ahead`, or equivalent and supplies either a product image or usable product
description, ask nothing. Silently resolve omitted values to:

- 3 variants;
- `clean-studio` for an otherwise unspecified product shot;
- `1:1` when the use case implies no other ratio;
- colors visible on the product or stated in conversation, otherwise neutral;
- matching craft descriptors from `references/photographer-references.md`.

State the resolved recipe in one sentence and proceed. Do not phrase it as a
question.

Ask only for a user-owned gap that blocks useful generation, in this order:

1. `product`: no confirmed product image and no usable visual description;
2. `style`: cannot infer a suitable preset from product or destination;
3. `count`: quantity materially changes the deliverable;
4. `ratio`: the named destination is genuinely ambiguous;
5. `revision`: a rejection names no defect.

Default omitted count to 3, omitted generic ratio to `1:1`, and omitted palette
to product-derived or neutral. Never ask about model, resolution, prompt
structure, negative prompts, refinement, photographers, lenses, Kelvin,
f-stop, lighting terminology, or internal brand context.

## Input media

- A text-only product is allowed when category, form, packaging, material,
  color, label treatment, and distinctive features are sufficiently described.
- `restyle`, `virtual-model-tryout`, and
  `closeup-product-with-person` require a concrete product/image reference; do
  not invent one.
- Use brand and product facts already present in conversation. Do not search
  for a local `.memory` directory or invent claims, materials, pricing, colors,
  label copy, or product features.

## Route and read references

Select mode by deliverable intent. Platform or format beats environment:
Pinterest pin over lifestyle, banner over lifestyle, carousel over scene, and
closeup-with-person over generic lifestyle. `restyle` applies only when subject
and composition should remain substantially unchanged.

Read these files from this installed skill before prompting:

1. the selected `references/<mode>.md`;
2. `references/typography.md`;
3. `references/photography-vocabulary.md`;
4. `references/photographer-references.md`;
5. `references/negative-prompts.md`;
6. `references/refinement-pass.md`.

Do not read all ten mode files.

## Prompt contract

Before the first submission, call `models_get({model_id:"nano_banana_pro"})`
once to verify image-reference and 2K support. If either is unsupported, stop
and report the mismatch; do not switch model or drop the product reference.
Use `medias[].role:"image"` for product images and refinements.

- Always use `model:"nano_banana_pro"`; never substitute another model.
- Assemble each prompt in English from the selected mode's named-section
  template. Preserve exact requested on-image text in its original language.
- Set `resolution:"2k"`, `count:1`, and end every prompt with the literal line
  `resolution: 2k`.
- Append the applicable blocks from `references/negative-prompts.md`.
- Follow the typography three-case rule. Do not reserve fake empty bands unless
  the user explicitly asks for overlay space.
- Make variants materially distinct in composition, preset, hook, or scene.

Photographer, publication, retailer, competitor, and third-party studio names
are internal craft anchors. Convert them to concrete lighting, palette,
composition, surface, and photographic-register language before generation.
Never expose those names in prompts, questions, progress, errors, logs, or
delivery notes. A user's own brand name may appear only when it is literal text
on the product being preserved.

Before every submission verify that no prompt contains a photographer name,
publication title, retailer or competitor name, or internal preset/mode
codename.

## Keep one product identity across the set

When the user requests several views of one text-only product, generate the
first requested image (index 0) first and wait for completion. If an existing
viewer is available, inspect it as described under Optional visual QA. Reuse
that completed image's job ID as the image reference for every remaining first-pass variant.
Do not generate a separate reference image. Change only the scene, lighting,
and camera across the set. With a supplied product image, use that
same reference for all first passes instead. For a new unrelated product, start
a separate set rather than borrowing another product's reference.

## Generate and refine

Every first-pass item has this shape; omit `medias` for a valid text-only
product:

```json
{
  "index": 0,
  "params": {
    "model": "nano_banana_pro",
    "prompt": "<assembled mode prompt>\n\nresolution: 2k",
    "aspect_ratio": "<mode ratio>",
    "resolution": "2k",
    "count": 1,
    "medias": [{"value": "<media_id, completed job id, or authorized HTTPS URL>", "role": "image"}]
  }
}
```

Submit complete ready groups with `generate_image_batch`, then poll only active jobs. Never resubmit a queued job; a wait timeout is not
a generation failure. Freeze completed indices.

Use `references/refinement-pass.md` for an observed quality-gate failure or a
specific user-requested correction. Refine only that index: reuse its stable
index and aspect ratio, attach the latest completed job ID for that index as the single
`image` reference, and write a focused correction that preserves the product,
composition, and all passing qualities. Run at most two refinements per index.
When viewing a carousel or ad pack, audit set coherence first and refine only
broken indices.

Deliver the first pass when no observed defect or specific correction requires
a refinement. If a user requests an unspecified refinement and you cannot view
the image, ask what to change instead of inventing a defect.

## Waiting and stopping

Keep an indexed ledger of submitted job IDs and their last observed status.
Use `timeout_seconds:15` during active polling and respect `poll_after_seconds`
when the host can delay. Do not use sandbox sleep or invent a delay tool. After
12 active `jobs_wait` calls for this requested set, stop polling, retain the
existing IDs, and tell the user which outputs are still pending. Resume those
same jobs only on a later user turn; never submit replacements for slow jobs.
A timeout or retryable lookup error is not permission to regenerate. Retry a
terminal technical failure or rejected submission at most once per index;
stop on safety, permission, quota, or billing errors instead of retrying them.
Count failed submissions and refinements toward a total of three generation
submissions per index. Do not reset this budget by rebuilding the prompt.

## Optional visual QA

Viewing is optional, not a prerequisite for generation or delivery. If the host
already provides an image viewer and the result is accessible, use it to inspect
the completed image and its source reference. Do not install tools or block
delivery to obtain a viewer. If fetching or viewing is unavailable, skip the
audit and explicitly state that the outputs were not visually inspected.

Only actual image content supports a visual audit; a URL, widget, status, or
prompt does not. Compare product shape, markings, colors, materials, composition,
and requested text with the brief and reference. Do not claim tiny text or
full-resolution sharpness is verified from a thumbnail. Without pixels, never
claim quality gates passed or spend credits on speculative visual refinements.
A specific user-requested correction may still be applied without viewing it.

Each refinement references the latest completed job for that SAME index,
never another variant or an older superseded attempt. Re-inspect the refinement
if viewing is available; otherwise disclose that its visual result is unverified.
When the budget is exhausted, deliver the best available completed version with
any known remaining limitation. If an index has no completed result, report it
as failed or pending; never claim the requested set is complete.

## Delivery

Show one final ordered gallery containing exactly one job per requested index.
Return one compact sentence naming the mode, preset, ratio, and any correction
applied. Disclose unverified visual QA. Hide model names, job IDs, internal craft references, and
pipeline mechanics. On vague rejection, ask one short triage question; on a
specific rejection, change only the named defect.
