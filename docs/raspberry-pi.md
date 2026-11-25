# Raspberry Pi setup (standalone, no Home Assistant)

## 1. System packages

On Raspberry Pi OS or Debian:

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip libgl1 libglib2.0-0
```

For a Pi Camera Module, also enable the camera in `raspi-config` and, if you
use `libcamera`, install the Picamera2 stack for your OS version. This app's
`watch` command opens the camera through OpenCV (`type: picamera` uses camera
index `0`; `type: rtsp` uses a URL).

## 2. Install the app

```bash
git clone https://github.com/YOUR_USER/backyard-wildlife.git
cd backyard-wildlife
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
cp config.example.yaml config.yaml
```

Put a Gemini key in `.env` only when you are ready to call the live API.
You can try the kit with no key at all:

```bash
python -m backyard_wildlife analyze --dry-run samples --json
python -m backyard_wildlife digest
python -m backyard_wildlife gallery
```

`--dry-run` uses `samples/manifest.json` and never opens a network socket
for a model call.

## 3. Point it at a camera

Edit `config.yaml`:

```yaml
camera:
  type: rtsp          # or picamera
  url: rtsp://user:password@CAMERA_LAN_IP:554/stream1
limits:
  cooldown_seconds: 300
  daily_cap: 150
  timezone: America/Chicago
vision:
  provider: gemini
  model: gemini-3.5-flash-lite
```

Then:

```bash
python -m backyard_wildlife watch
```

OpenCV watches the stream, a simple frame-diff detector waits for motion,
and only then is a still sent to the vision provider. Cooldown and the daily
cap are stored in `data/visits.sqlite`. Crops and full frames of **animals
only** land under `data/visits/`.

## 4. Run it as a service

A minimal systemd user unit:

```ini
[Unit]
Description=Backyard Wildlife watcher
After=network-online.target

[Service]
Type=simple
WorkingDirectory=/home/pi/backyard-wildlife
Environment=BACKYARD_WILDLIFE_CONFIG=/home/pi/backyard-wildlife/config.yaml
ExecStart=/home/pi/backyard-wildlife/.venv/bin/backyard-wildlife watch
Restart=on-failure

[Install]
WantedBy=default.target
```

Keep `.env` out of git and out of world-readable directories.

## 5. Gallery and digest

```bash
python -m backyard_wildlife gallery          # http://127.0.0.1:8080/
python -m backyard_wildlife digest           # data/digests/YYYY-MM-DD.md
```

The gallery is a local page of cropped animal visits. It does not include
people. Bind it to localhost, or to your LAN only behind a firewall.
