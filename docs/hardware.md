# Hardware

You can run this kit two ways: as a Home Assistant automation on cameras you
already have, or as a standalone Python app on a Raspberry Pi (or any small
Linux computer) that can reach an RTSP stream or a Pi Camera.

## Already in Home Assistant

- Any camera entity Home Assistant can snapshot: a doorbell, a floodlight
  cam, an RTSP camera via the Generic Camera or ONVIF integration, or a
  vendor integration such as Ring or UniFi.
- A motion, person, or animal binary sensor for that camera. Frigate animal
  events are a good trigger if you already run Frigate, because they reduce
  how often people are sent to a cloud model.
- Home Assistant OS, Supervised, Container, or a Home Assistant Green is
  enough for the LLM Vision path. A separate inference PC is only needed if
  you want local Ollama or Frigate with a detector.

## Raspberry Pi standalone

- Raspberry Pi 4 (4 GB or more) or Pi 5, or an equivalent single-board
  computer. A Pi 3 will struggle with OpenCV and a live stream at the same
  time.
- 32 GB or larger microSD, or a USB SSD.
- Power supply rated for the board.
- One of:
  - A USB or CSI camera (Pi Camera Module 2 or 3 works), or
  - A cheap wired or Wi-Fi camera that offers a local RTSP URL.
- Optional: a short weatherproof housing if the board lives outdoors. Keep
  storage and the API key off the camera itself; run the app on the Pi
  indoors and pull the stream.

## Network

- Prefer a local RTSP URL on your LAN. Avoid sending a live stream through a
  vendor cloud if you can use a local one.
- The gallery binds to `127.0.0.1` by default. Do not expose it to the
  public internet.

## What you do not need

- A GPU, unless you run a heavy local vision model.
- A paid API account. The default path is a Gemini free-tier key; see
  [costs.md](costs.md).
- Night-vision accuracy guarantees. Infrared frames of small animals often
  come back `uncertain`, and the bounding box is sometimes missing. The kit
  falls back to the full frame in that case.
