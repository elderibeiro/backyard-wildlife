# The same pattern, used by a small business

The backyard kit is a household project, but the pipeline is not limited to
rabbits. A motion or detection event, a cooldown, a daily cap, a vision
call that returns structured JSON, a privacy filter, a crop, and a local
log are the same steps a shop can use without building a custom platform.

## Storefront or parking-lot visitor tagging

- Trigger on a doorway or lot camera.
- Ask the model for a **category** such as pedestrian, bicycle, delivery
  van, or passenger car — not a person's name, face, or plate.
- Skip frames that contain an identifiable person if all you need is a
  daily count of deliveries vs. walk-ins.
- Keep the 5-minute cooldown so a waiting van is one visit, not fifty.
- Store crops locally and summarize them in the daily digest. Do not
  auto-post the stills.

This is a rough activity tag, not a security or billing system.

## Garden-center pest spotting

- Point a close-up camera at a bench, greenhouse aisle, or a single
  high-value plant.
- Reuse the species prompt with different `local_tips`, for example
  "look for aphids, spider mites, Japanese beetles, and leaf miners."
- The synthetic `samples/06-pest.jpg` frame shows how a "other animal"
  category can carry a specific pest name.
- A "likely" confidence plus a cropped photo is enough to walk the aisle;
  it is not a lab identification.

## What to change, and what not to

- Change the prompt, the category enum, and the dashboard labels.
- Keep the privacy filter, the local cap, and local storage.
- Tell staff and customers that stills may be sent to a vision provider,
  or run Ollama on a machine in the shop instead.
- Do not add face recognition, license-plate recognition, or an alert that
  names a person. That is outside the scope of this project on purpose.
