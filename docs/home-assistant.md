# Home Assistant setup

Two install paths ship in `homeassistant/`:

1. **Blueprint** (easiest): one camera at a time.
2. **Package**: helpers, counters, a three-camera example automation, and a
   dashboard view.

Both assume [LLM Vision](https://github.com/valentinfrlch/ha-llmvision)
(HACS / Marketplace). That integration is what the reference household setup
used as of November 2026, because it can analyze a short clip, return
structured JSON, expose a key frame, and keep a timeline.

## 1. Install LLM Vision and a provider

1. Install LLM Vision, then restart Home Assistant.
2. Settings → Devices & services → Add integration → LLM Vision.
3. Add a provider:
   - **Gemini (default):** LLM Vision's Google Gemini provider and a key from
     [Google AI Studio](https://aistudio.google.com/apikey). A practical
     default model is `gemini-3.5-flash-lite` (this is what the reference
     setup used when `gemini-2.5-flash` was not available to new keys).
   - **OpenAI:** the OpenAI provider, paid.
   - **xAI:** LLM Vision's xAI provider, or its Custom OpenAI option pointed
     at `https://api.x.ai/v1`. Keep this as a rollback if you started there.
   - **Ollama:** a local vision model, no cloud key. Needs a machine large
     enough to run it; a Home Assistant Green is usually too small.
4. Copy the provider **id** from the LLM Vision entry (it is not the API
   key). Paste it into `input_text.wildlife_provider_id` or the blueprint
   input.

Do **not** call `google_generative_ai_conversation.generate_content`. That
action was deprecated and is removed in Home Assistant 2026.4. If you want
the official Home Assistant AI path instead of LLM Vision, use
`ai_task.generate_data` and the snapshot blueprint
`backyard_wildlife_ai_task.yaml`. Official AI Task entities are provided by
integrations such as OpenAI and Ollama; Google Gemini exposes conversation,
TTS, and (on versions that offer it) an AI Task entity as well. AI Task
looks at a single still and does not fill the LLM Vision timeline.

Never use `llmvision.stream_analyzer` in this kit. It records a live stream
and is easier to over-call.

## 2. Helpers and the package

Copy `homeassistant/packages/backyard_wildlife.yaml` to
`config/packages/backyard_wildlife.yaml` and enable packages:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

Edit the example entities at the top of the package
(`binary_sensor.backyard_motion`, `camera.backyard`, and the matching
garden / porch names) so they match your cameras. Create one
`input_datetime.wildlife_last_<camera>` per camera id.

Defaults after you load the package:

- Cooldown: 300 seconds per camera (`input_number.wildlife_cooldown_seconds`)
- Daily cap: 150 (`input_number.wildlife_daily_cap`), reset at midnight
- Frame width: 1024 pixels
- Notifications: off (`input_boolean.wildlife_notifications`)

For doorbell-style cameras that write a recording a few seconds after
motion, raise the delay in the automation (the reference setup waited 20
seconds, then skipped stale clips). The generic package uses an 8-second
delay, which is enough for a simple snapshot camera.

## 3. Blueprint

Copy `homeassistant/blueprints/backyard_wildlife.yaml` to
`config/blueprints/automation/backyard_wildlife.yaml`, reload automations,
and create one automation per camera. You still need the daily-cap and
cooldown helpers from the package (or equivalent ones you create yourself).

## 4. Recent Visits dashboard

1. Copy `homeassistant/www/wildlife-visits-card.js` to
   `config/www/wildlife-visits-card.js`.
2. Add a Lovelace resource: `/local/wildlife-visits-card.js`, type `module`.
3. The card extends LLM Vision's timeline card. Install that card first.
4. Use `homeassistant/lovelace/backyard-wildlife-dashboard.yaml` as a
   starting view.

The automation writes a `[crop:ymin,xmin,ymax,xmax]` tag (0-1000 coordinates)
onto animal events only. The card crops on screen. If the model omits the
box — common for small animals in infrared — the full key frame is shown.
People, vehicles, and empty results are never written to the timeline, so
the panel stays animal-only.

## 5. Optional: video clips

If your camera integration exposes a fresh recording URL, you can switch the
package's `llmvision.image_analyzer` call to `llmvision.video_analyzer` with
`video_file` set to that URL, `max_frames: 3`, and `target_width: 1024`.
Only do this when the URL is a **new** clip. Re-sending an old recording
wastes quota and can recount a visit.

## 6. Optional: named regulars

Twelve `input_text.wildlife_regular_*` helpers are included. When a cat or a
larger mammal has distinctive markings, the model can match or create a
short name. Squirrels, rabbits, and birds are counted by species only. This
is best-effort and will mix up look-alikes; it does not identify people.
