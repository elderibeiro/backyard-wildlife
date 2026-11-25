# Troubleshooting

## Dry-run works, live calls fail

- Confirm the key is in `.env` or in the Home Assistant provider entry, not
  in git.
- For Gemini, open [AI Studio](https://aistudio.google.com/) and check the
  project's rate limits and billing. A prepaid balance of zero, or a project
  that was switched onto billing, can reject requests even when you expected
  the free tier.
- Confirm the model id is one your project can actually call. The default
  `gemini-3.5-flash-lite` was chosen because a newer Flash id was not
  available to a new key in the reference setup. Try a Flash or Flash-Lite
  model listed in AI Studio.

## Home Assistant automation runs but counters never move

- The analyzer response must be parsed from `structured_response` or the
  JSON body. If you changed the prompt and dropped the schema, the package's
  parse step falls back to `none` and will not increment counters.
- Check that `input_text.wildlife_provider_id` is the LLM Vision **provider
  id**, not the API key.
- Look at the automation trace for the `llmvision.image_analyzer` step.
  Timeouts and 429s show up there.

## Everything is "cooldown" or the cap is already full

- The daily counter resets at local midnight in Home Assistant, and at
  midnight in `limits.timezone` in the Python app (default
  `America/Chicago`). It is a local safety cap, not Google's quota.
- Per-camera cooldown defaults to 300 seconds. A second animal on the same
  camera during that window is not counted. A different camera still can be.
- In the Python app, `--dry-run` and `--no-limits` skip these checks so you
  can process the sample folder in one go.

## Recent Visits shows a full frame instead of a crop

- The model sometimes omits `box_2d`, especially for small animals at night.
  The card and the Python cropper then keep the full still. This is
  expected, not a broken install.
- If *no* event appears, confirm `wildlife-visits-card.js` is loaded as a
  module resource and that the LLM Vision timeline card is installed. The
  custom card extends that card and will not register without it.
- Only animal events are written to the timeline. People and empty results
  are supposed to be missing.

## Stale or repeated visits

- Some cameras republish an old recording when they reconnect. The Python
  app only analyzes a fresh motion frame. In Home Assistant, skip clips that
  are older than a couple of minutes, and do not re-run the analyzer on
  every attribute change of the same event.

## OpenCV cannot open the stream

- Test the RTSP URL in VLC on the same network.
- On a Pi Camera, confirm the device appears at index 0 (`libcamera-hello`
  or `rpicam-hello` on recent OS images).
- Install `libgl1` and `libglib2.0-0` if `cv2` fails to import.

## YAML will not load in Home Assistant

- The package uses placeholder cameras (`camera.backyard` and friends). If
  those entities do not exist, create them, or edit the package / use the
  blueprint with your real entity IDs.
- Reload "Input numbers," "Input datetimes," and "Automations" after
  copying the package, or restart Home Assistant.
- Blueprint `!input` tags are normal. They only resolve after you create an
  automation from the blueprint.

## The official Google Gemini integration vs LLM Vision

LLM Vision is the recommended path for this kit because it handles clips,
structured JSON, key frames, and a timeline. The official integration is
still useful for Assist and, on versions that offer it, `ai_task.generate_data`
snapshots. It does not replace the Recent Visits card. See
[home-assistant.md](home-assistant.md).
