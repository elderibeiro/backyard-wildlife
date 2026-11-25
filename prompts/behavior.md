# Behavior description

Use this when you already know the species and want a short behavior label
for the journal or a caption. The main species prompt already asks for a
`behavior` field, so this is optional and should not be a second paid call
on every visit.

## Prompt

```
Given this camera frame of a wild animal that has already been identified
as {species}, describe the behavior in one short sentence and a 2-4 word
label. Return JSON: {"behavior": "label", "details": "sentence"}.
Do not mention any person who might appear in the background.
```

Example labels: `foraging`, `perched`, `crossing the path`, `at the feeder`,
`on a leaf`.
