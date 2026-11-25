# Daily digest summary

The Python app writes a digest from the local SQLite log **without** calling
an API (`backyard-wildlife digest`). Use this prompt only if you want a
prose rewrite from a model, and feed it the already-filtered JSON (animals
only, no people).

## Prompt

```
Summarize today's backyard wildlife visits for a household journal.

Input is a JSON list of visits with species, count, confidence, behavior, and time.
Write 3-6 short sentences covering: who visited, any notable behavior, quiet periods,
and a single sentence a shop owner could reuse if this were a storefront or garden
camera (without inventing numbers that are not in the data).

Do not mention people. Do not invent visit counts.
```

The built-in digest lists only what is in the log. If the log is empty, it
says so instead of guessing.
