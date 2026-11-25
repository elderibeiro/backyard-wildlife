# Privacy and ethics

This kit is for watching *animals*, not people.

## What the software does

- The species prompt asks the model to set `contains_person` and not to
  describe a person's face, clothing, or identity.
- Recent Visits, the SQLite log used for the gallery, and the daily digest
  drop frames that contain a person, a vehicle-only scene, or no animal.
- Crops and stills are stored locally (`data/visits/` on a Pi,
  `/media/llmvision/snapshots/` in Home Assistant). Nothing in this
  repository uploads those files to a social network or a second cloud.
- The gallery binds to `127.0.0.1` by default.

## What it cannot promise

- If you use Gemini, OpenAI, or xAI, each analyzed frame is sent to that
  provider. A cloud model has already seen a person by the time
  `contains_person` comes back. To avoid that, trigger only on a **local**
  animal detector (Frigate, or a Pi-side model) or run **Ollama** on a
  machine you control.
- Gemini's free tier may use prompts and responses, including images, to
  improve Google's products. See [costs.md](costs.md).
- Bounding boxes can miss, especially at night. The fallback is the full
  frame, so a person at the edge of an "animal" crop can still appear. When
  in doubt, delete the still.
- Named "regulars" are for distinctive cats and larger wildlife. They are
  not a facial-recognition system and must never be used to identify people.

## Practical rules

1. Point cameras at a yard, feeder, garden bed, or parking lot — not a
   sidewalk, window, or neighbor's house.
2. Do not publish raw clips. If you post a caption, use a crop that contains
   only the animal, and no location more specific than a generic backyard.
3. Do not commit `.env`, `config.yaml`, database files, or real snapshots.
4. If you adapt the same pattern for a storefront or parking lot, tell
   customers that a camera may send a still to a vision model, keep the
   retention short, and still skip people in any public gallery.
5. Follow local recording-consent and workplace-camera rules. This software
   is not a security system and is not accurate enough to be one.

## Ethics in short

Use this to learn which animals share a garden, or to spot pests on a plant.
Do not use it to track people, to name neighbors, or to automate a punitive
decision.
