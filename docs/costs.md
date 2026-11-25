# Costs and rate limits

Figures below were checked on 25 November 2026 against Google's public
pricing and rate-limit pages. They will change. Always re-check:

- [Gemini Developer API pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Gemini API rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- Your project's live quotas in [Google AI Studio](https://aistudio.google.com/)

This kit does **not** invent a daily free-quota number. Google no longer
prints a public per-model RPM / RPD table for the free tier; those values
are shown on your project's rate-limit page and can vary.

## Gemini free tier (default)

As of 25 November 2026, Google's pricing page lists several Flash and
Flash-Lite models as **free of charge** on the free tier for standard input
and output, including image and video input. That is image *understanding*
(send a photo, get JSON back), not image *generation*. Image-generation
models are paid-only.

Models the pricing page listed as free of charge on that date included
`gemini-3.5-flash-lite`, `gemini-3.1-flash-lite`, `gemini-3.6-flash`, and
`gemini-3.8-flash`. The reference household setup used
`gemini-3.5-flash-lite` after `gemini-2.5-flash` was not available to a new
key. Pick whatever Flash or Flash-Lite model your project currently lists.

What the official rate-limit page *does* state:

- Limits are measured as requests per minute (RPM), input tokens per minute
  (TPM), and requests per day (RPD), sometimes with extra dimensions.
- Limits are **per project, not per API key**.
- RPD resets at midnight Pacific time.
- Preview and experimental models are tighter.
- Specified limits are not guaranteed.

A local **150 calls a day** cap and a **5-minute cooldown** are shipped as
defaults so one lingering animal (or a flapping branch) cannot drain your
quota. They are not Google's published quota. Raise or lower them after you
read your own project's limits.

### Free-tier data use and billing gotchas

- On the free tier, Google may use prompts and responses, including camera
  frames, to improve its products. The paid tier is documented as not doing
  that. See the pricing page footnote and the Gemini API terms.
- Linking a billing account moves the project off the free tier. A prepaid
  balance of zero can then reject requests even when you expected a free
  quota. If calls suddenly fail with a credits or billing error, check the
  Cloud / AI Studio billing page before raising the local cap.
- Stay on a dedicated project and key for this kit so a different app cannot
  share (and exhaust) the same quota.

## Other providers

| Provider | Typical cost for this kit | Notes |
| --- | --- | --- |
| Google Gemini Flash / Flash-Lite, free tier | $0 within your project's free limits | Default. Frames may be used to improve Google products. |
| Google Gemini, paid tier | Listed per 1M tokens on the pricing page (`gemini-3.5-flash-lite` was $0.30 input / $2.50 output per 1M tokens on 25 Nov 2026) | A 1024-px snapshot is a tiny fraction of 1M tokens; still cap your calls. |
| OpenAI | Paid; set a usage limit in the OpenAI dashboard | Official Home Assistant OpenAI integration also provides AI Task entities. |
| xAI Grok | Paid; monitor the xAI console | Useful rollback. LLM Vision can use the OpenAI-compatible endpoint. |
| Ollama (local) | Electricity only | Most private option. Needs a machine that can run a vision model. |

## Why the defaults are 5 minutes and 150 / day

The reference setup started at a 10-minute cooldown and 60 calls a day when
it ran on a paid key, then moved to 5 minutes and 150 a day after switching
to Gemini, still as a conservative local cap rather than a claim about
Google's quota. The Python app and the Home Assistant package use those
later defaults. They are easy to change.
