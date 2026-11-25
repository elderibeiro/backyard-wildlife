# Species identification

Use this prompt when a camera frame might contain a wild animal. Ask the model
to return **JSON only**, matching the schema below. A copy of the same text is
wired into the Python app (`backyard_wildlife.prompts`) and the Home Assistant
package.

The reference household setup also asked for a tight bounding box in the same
call so crops cost no extra API request.

## Prompt

```
Identify animals in these outdoor camera frames. Return JSON only.

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

Local tips: {local_tips}

Known regulars: {regulars}
```

## JSON schema

See `src/backyard_wildlife/prompts.py` for the machine-readable schema. Required
fields: `category`, `species`, `count`, `confidence`, `behavior`, `title`,
`description`, `features`, `regular`, `contains_person`, `contains_vehicle`,
`boxes`.

Coordinates follow Gemini's object-detection convention: each value is an
integer from 0 to 1000, in order `ymin, xmin, ymax, xmax`. Scale them to the
pixel size of the original image before cropping.

## Local tips

Do not hard-code a city or a private yard. Put regional hints in
`vision.local_tips` (Python) or `input_text.wildlife_local_tips` (Home Assistant).
Example: "Eastern gray and fox squirrels and eastern cottontail rabbits are the
usual daytime visitors."
