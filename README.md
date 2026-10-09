# SI-Posture — Windows AI Posture Monitoring Application

A Windows desktop application that continuously monitors sitting posture using a remote Vision Language Model (VLM) hosted by llama.cpp.

## Features

- **Forward Head Detection**: Detects head moving forward relative to shoulders
- **Forward Torso Detection**: Detects upper body leaning toward the screen
- **Remote AI Analysis**: Uses remote llama.cpp VLM (no local model required)
- **System Tray Operation**: Runs in background with Windows system tray
- **Real-time Monitoring**: Configurable capture intervals and alert thresholds
- **Multi-platform Settings**: Windows notifications and optional Telegram alerts
- **First-launch Wizard**: Guided setup for camera, AI server, and calibration

## Technology Stack

- **Language**: Python 3.12+
- **GUI**: PySide6 / Qt Widgets
- **Camera**: OpenCV
- **AI Backend**: Remote llama.cpp (OpenAI-compatible REST API)
- **HTTP Client**: httpx
- **Data Validation**: Pydantic
- **Settings**: JSON configuration
- **History**: SQLite
- **Notifications**: Qt System Tray / Windows notifications
- **Telegram**: Telegram Bot HTTP API
- **Packaging**: PyInstaller

## Project Structure

```
src/si_posture/
├── main.py              # Application entry point
├── models.py            # Pydantic models and enums
├── ai/
│   └── client.py        # Remote llama.cpp API client
├── camera/
│   └── __init__.py      # Camera capture and enumeration
├── monitoring/
│   ├── evaluator.py     # Posture evaluation engine
│   └── scheduler.py     # Monitoring scheduler
├── notifications/
│   └── __init__.py      # Windows and Telegram notifications
├── storage/
│   └── __init__.py      # Settings and SQLite storage
└── ui/
    ├── main_window.py   # Main application window
    ├── wizard.py        # Setup wizard
    ├── settings.py      # Settings dialog
    └── __init__.py      # UI module exports
```

## Installation

### Prerequisites

- Python 3.12+
- Windows OS
- Webcam (laptop or external)
- Remote llama.cpp server with OpenAI-compatible API

### Setup

#### Using pip:
```bash
pip install -e ".[dev]"
python -m si_posture.main
```

#### Using uv:
```bash
uv sync
uv run python -m si_posture.main
```

## First Launch Setup

The application launches a setup wizard on first run:

1. **Camera Setup**: Select webcam and verify framing
2. **AI Server Configuration**: Enter API URL, key, and select model
3. **Posture Calibration**: Capture reference posture image
4. **Monitoring Preferences**: Configure intervals and thresholds

## Configuration

Settings are stored in `.\.si_posture\settings.json`:

- Camera index
- AI server URL and API key
- Model selection
- Capture interval (default: 15 seconds)
- Alert threshold (default: 3 consecutive alerts)
- Notification preferences

## AI Comparison

The application sends two images to the remote VLM:
1. Reference posture (calibration)
2. Current webcam frame

The model returns structured JSON analysis:
- Visibility assessment
- Head position relative to shoulders
- Torso position relative to reference
- Change magnitude
- Visual evidence

## Alert Logic

Alerts are triggered when:
- Sufficient visibility confirmed
- At least MODERATE change detected
- Forward head OR forward torso identified
- Minimum duration threshold met (default: 45 seconds)
- Alert threshold reached (default: 3 in window)

Cooldown period prevents repeated notifications (default: 15 minutes).

## Privacy & Security

- No continuous photo/video recording
- Images sent only to configured inference endpoint
- No Base64 image data logged
- API keys stored separately (can use Windows credential store)
- No automatic cloud uploads
- Complete data deletion available

## Development

Run tests:
```bash
pytest
```

Run with debug mode:
```bash
DEBUG=1 python -m si_posture.main
```

## Building for Distribution

Create `SI-Posture.spec` file and build with PyInstaller:
```bash
pyinstaller --onefile --windowed --name "SI-Posture" SI-Posture.spec
```

## License

Proprietary application for internal use.
