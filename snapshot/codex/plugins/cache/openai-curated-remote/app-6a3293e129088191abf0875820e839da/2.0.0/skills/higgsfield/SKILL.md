---
name: higgsfield
description: Execute a named Higgsfield image or video preset invoked as @Higgsfield /preset-name, such as /main-character, /brand-monument or /reel-cover, browse Viral or Marketing Studio galleries with /effects, /product or /motion, or use a named generation model with /MODEL_NAME. Resolve preset names against the catalog before executing; infer intent for unknown commands. Activate for a request to execute or browse presets; a quoted command to translate, an explanation of a URL, or an explicitly negated preset is not an invocation.
---

# Higgsfield presets

To browse both Viral and Marketing Studio catalogs together, call `get_presets` without `source`.

For `/effects` or a request to browse Viral presets, call `get_presets` with `source: "viral"`. For `/product`, call `get_presets` with `source: "marketing_studio", category: "product-shot"`. For `/motion`, use `source: "marketing_studio", category: "motion"`. For `/marketing-studio` or a request to browse all Marketing Studio templates, use `source: "marketing_studio"`. Browsing itself does not submit a job; Viral includes chain presets only. Do not send these catalog IDs to generate_image or generate_video. The widget handles category changes and pagination.

For other named presets, call `get_preset_instructions` with the user's slash token before interpreting the preset or requesting an image. Resolve unfamiliar names through the same tool. For a request to browse the bundled Control presets specifically, call it without `preset`.

Follow the returned instructions. A catalog listing is not a resolved preset: load the chosen ID before generating. The server supplies the current prompts, parameters and workflow; this skill stores none of them.

When the slash token unambiguously names a supported generation model, use that model directly with the relevant generation tool and the user's prompt/media. If the model is unfamiliar, resolve it through `models_search`; do not invent model IDs.

If `get_preset_instructions` returns `not_found`, infer the intended creation from the command and conversation, choose sensible defaults, and proceed with ordinary generation without asking the user to clarify the command. Use supplied media when relevant; do not claim the unknown preset exists or pass its name as a preset/model ID. For informational or growth commands, follow their returned instructions and explain the result to the user; do not open a gallery or generate unless those instructions require it.

For a resolved Viral or Marketing Studio preset, follow the returned `get_presets` call with its exact `source` and `preset_id` to open its detail. Check `execution.available` before calling `execute_preset`; if false, explain the returned reason and do not submit. When execution is available and requested by the user, collect inputs according to `execution.input_schema` and call `execute_preset` with the resolved source, preset ID and inputs. Treat an error response as an unsuccessful submission; only report submitted jobs when the tool returns job IDs. Informational command instructions are text-only; they do not imply a gallery or a generation.

After a successful execute_preset call, or a widget message reporting submitted job IDs, do not submit the same preset again. For one job, call job_display and wait with jobs_wait. For multiple jobs, wait in groups of at most 8, then display the complete result set with `show_generation_by_ids({jobs: [...]})`, mapping IDs in order to `{index, job_id}` entries (up to 24 per call). Do not use generation history to find these results or assume a preset produces only one output.
