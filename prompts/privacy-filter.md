# Person / privacy filter

Run this as a first pass if you want to avoid sending a frame that clearly
contains a person to a cloud model. The default kit still sends the frame to
the species prompt (which also returns `contains_person`) and then **drops
the visit from the gallery**. A local first pass is stricter.

For even better privacy, trigger only on an on-device animal detector
(Frigate, or a Pi-side model) so people are never uploaded.

## Prompt

```
Look at this camera frame only to decide whether a person is visible.

Return JSON: {"contains_person": true or false, "reason": "short reason with no
physical description of the person"}.

If a person is visible, do not describe their face, clothing, or identity.
This check exists so people are not stored in a wildlife gallery.
```

## After the response

- If `contains_person` is true: do not save a crop, do not increment animal
  counters, do not show the frame in Recent Visits, and do not write a social
  caption.
- Do not log identifying details about the person.
- Prefer on-device storage even for animal frames.
