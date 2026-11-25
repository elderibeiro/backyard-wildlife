"""Prompt text used by the standalone app. Markdown copies live in /prompts."""

from __future__ import annotations

JSON_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "category",
        "species",
        "count",
        "confidence",
        "behavior",
        "title",
        "description",
        "features",
        "regular",
        "contains_person",
        "contains_vehicle",
        "boxes",
    ],
    "properties": {
        "category": {
            "type": "string",
            "enum": [
                "squirrel",
                "opossum",
                "rabbit",
                "bird",
                "cat",
                "other animal",
                "none",
            ],
        },
        "species": {"type": "string"},
        "count": {"type": "integer"},
        "confidence": {"type": "string", "enum": ["certain", "likely", "uncertain"]},
        "behavior": {"type": "string"},
        "title": {"type": "string"},
        "description": {"type": "string"},
        "features": {"type": "string"},
        "regular": {"type": "string"},
        "contains_person": {"type": "boolean"},
        "contains_vehicle": {"type": "boolean"},
        "boxes": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["frame", "box_2d"],
                "properties": {
                    "frame": {"type": "integer"},
                    "label": {"type": "string"},
                    "box_2d": {"type": "array", "items": {"type": "integer"}},
                },
            },
        },
    },
}

SPECIES_PROMPT = """Identify animals in these outdoor camera frames. Return JSON only.

category: exactly one of squirrel, opossum, rabbit, bird, cat, other animal, none.
Pick the main animal if several appear. Use none if no animal is clearly visible.

species: the specific common name when you can tell (for example eastern gray squirrel,
eastern cottontail, northern cardinal, American robin, house sparrow, mourning dove,
blue jay, Virginia opossum). Otherwise use the category word. Use none if category is none.

count: number of animals of that species that are clearly visible. Use 0 if category is none.

confidence: certain if clearly identifiable; likely if reasonably sure; uncertain if the
subject is small, distant, blurry, dark, or partly hidden.

behavior: a few words on what the animal is doing (foraging, perched, crossing the frame,
climbing, watching the camera). Empty if category is none.

title: 2-6 words naming the species, starting with Likely or Uncertain when not certain.
If category is none, name the main subject (Person walking, Car in driveway) or use
No activity observed.

description: one short factual sentence. Do not name or describe a person's face,
clothing that would identify them, or anything written on a uniform.

features: for a cat or a larger mammal (opossum, raccoon, fox, coyote, skunk, deer)
with clearly visible distinctive markings, up to 10 words on coat color, pattern, and
marks. Otherwise empty.

regular: the name of a known regular listed below only if the features clearly match;
new if clearly distinctive but no match; otherwise none.

contains_person: true if a person is visible, even when an animal is also present.
contains_vehicle: true if a car, truck, van, or bicycle is visible.

boxes: for the main animal named in category, one entry per image where it is visible:
frame (1 = first image) and box_2d [ymin, xmin, ymax, xmax] normalized 0-1000, tight
around the animal's body. Use an empty list if category is none.

Never guess an animal from blur, leaves, shadows, or reflections; use none.
Use cat only when feline features are visible (pointed ears, long thin tail, smooth walk).
Raccoon, skunk, dog, rat, or mouse: other animal.

{local_tips}

Known regulars: {regulars}
"""

PRIVACY_PROMPT = """Look at this camera frame only to decide whether a person is visible.

Return JSON: {"contains_person": true or false, "reason": "short reason with no
physical description of the person"}.

If a person is visible, do not describe their face, clothing, or identity.
This check exists so people are not stored in a wildlife gallery.
"""

BEHAVIOR_PROMPT = """Given this camera frame of a wild animal that has already been
identified as {species}, describe the behavior in one short sentence and a 2-4
word label. Return JSON: {"behavior": "label", "details": "sentence"}.
Do not mention any person who might appear in the background.
"""

DIGEST_PROMPT = """Summarize today's backyard wildlife visits for a household journal.

Input is a JSON list of visits with species, count, confidence, behavior, and time.
Write 3-6 short sentences covering: who visited, any notable behavior, quiet periods,
and a single sentence a shop owner could reuse if this were a storefront or garden
camera (without inventing numbers that are not in the data).

Do not mention people. Do not invent visit counts.
"""

CAPTION_PROMPT = """Write three short, friendly social captions for this wildlife visit.

Species: {species}
Behavior: {behavior}
Confidence: {confidence}

Rules: no location, no address, no people's names, no claims of scientific certainty
when confidence is not "certain". Keep each caption under 140 characters. Return JSON:
{"captions": ["...", "...", "..."]}.
"""


def render_species_prompt(local_tips: str = "", regulars: str = "none") -> str:
    tips = local_tips.strip() or "No extra regional hints."
    return SPECIES_PROMPT.format(local_tips="Local tips: " + tips, regulars=regulars or "none")
