# Fun captions for social posts

Optional. Generate captions from a visit that has already passed the privacy
filter. Never include a location more specific than a generic "backyard" or
"garden," and never attach a frame that contains a person.

## Prompt

```
Write three short, friendly social captions for this wildlife visit.

Species: {species}
Behavior: {behavior}
Confidence: {confidence}

Rules: no location, no address, no people's names, no claims of scientific certainty
when confidence is not "certain". Keep each caption under 140 characters. Return JSON:
{"captions": ["...", "...", "..."]}.
```

## Example (for the synthetic cottontail sample)

```json
{
  "captions": [
    "Morning visitor: an eastern cottontail taking a quiet sit in the grass.",
    "Likely a cottontail, ears up, no rush. Backyard, not a wildlife documentary.",
    "Someone is using the lawn as a break room again."
  ]
}
```
