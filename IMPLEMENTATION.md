# SI-Posture — Windows AI Posture Monitoring Application

## Project Objective

Develop a Windows desktop application called **SI-Posture** that continuously monitors a user's sitting posture through a locally connected webcam.

Use a **remote Vision Language Model (VLM)** hosted by llama.cpp to compare current webcam snapshots against a calibrated reference posture.

The first version must focus exclusively on:

1. Forward head posture — head moving forward relative to the shoulders.
2. Excessive forward torso leaning — upper body leaning toward the screen/camera.

Other movements, such as leaning backward, looking sideways, or stretching, must not automatically trigger alerts.

The application must have a proper Windows GUI and operate in the background using the Windows system tray.

**Do not build a Linux GUI or a browser-based frontend.**

## 1. Technology Stack

Use:

| Component | Technology |
|---|---|
| Language | Python 3.12+ |
| Desktop GUI | PySide6 / Qt Widgets |
| Camera | OpenCV |
| AI Backend | Remote llama.cpp |
| API Protocol | OpenAI-compatible REST |
| HTTP Client | httpx |
| Data validation | Pydantic |
| Settings | JSON configuration |
| History | SQLite |
| Notifications | Qt System Tray / Windows notifications |
| Telegram | Telegram Bot HTTP API |
| Packaging | PyInstaller |
| Testing | pytest |

Use an architecture that separates GUI, webcam capture, AI inference, posture evaluation and notifications.

The local Windows machine must **not require an installed AI model, CUDA, Ollama or llama.cpp**.

## 2. First-Launch Setup Wizard

When the application starts for the first time, launch a setup wizard.

### Step 1 — Camera Setup

- Enumerate available webcams.
- Display human-readable camera names where possible.
- Allow selection of laptop webcam or external USB webcam.
- Show a live preview.
- Allow camera switching and refresh.
- Let the user verify that head, shoulders and upper torso are visible.
- Warn when the framing is insufficient for forward-head detection.
- Save the selected camera.

### Step 2 — AI Server Configuration

Provide the following GUI fields:

- API Base URL
- API Key (optional)
- Model selection
- Connection timeout
- Test Connection button
- Refresh Models button

Example API Base URL:

`http://192.168.1.100:8083/v1`

Use `GET /v1/models` to populate the model selector.

Allow manual model ID entry if discovery is unsupported or incomplete.

Validate the selected model's image input capability where metadata is available. Include a test image request to verify actual multimodal inference.

Support server addresses entered with or without `/v1` and normalize them correctly.

Store the selected configuration locally.

### Step 3 — Posture Calibration

Display an instruction screen:

"Sit in a comfortable, upright working position with your head balanced over your shoulders. Keep your shoulders relaxed and look at your normal screen position."

Calibration workflow:

1. Show live camera preview.
2. Ask the user to sit in their preferred neutral posture.
3. Start a 5-second countdown.
4. Capture 3 images over several seconds.
5. Check whether the head, shoulders and upper torso are sufficiently visible.
6. Allow the user to review captured images.
7. Select one representative image as the initial reference.
8. Save the calibration locally after user confirmation.

The reference image represents the user's chosen baseline, **not a medically certified correct posture**.

Do not infer that a position is healthy simply because it matches the baseline.

Provide a Recalibrate button in the main UI and system tray menu.

Changing camera selection or camera placement should require recalibration.

### Step 4 — Monitoring Preferences

Default settings:

| Parameter | Default |
|---|---|
| Capture interval | 15 seconds |
| Consecutive evaluation window | 4 results |
| Alert threshold | 3 confirmed abnormal results in the window |
| Minimum abnormal duration | 45 seconds |
| Alert cooldown | 15 minutes |
| Windows notification | Enabled |
| Telegram notification | Disabled |
| Start minimized to tray | Enabled after setup |
| Start with Windows | Disabled |

All settings should be editable later.

Require calibration and a working AI connection before monitoring can be activated.

## 3. Main Application GUI

Create a modern, clean Windows desktop interface.

### Dashboard

Display:

- Live webcam preview
- Current monitoring status
- AI server connection status
- Selected model
- Last inference time
- Last detected posture change
- Active alert cooldown
- Monitoring Start / Pause button
- Recalibrate button

Monitoring status values:

- GOOD / REFERENCE-LIKE
- HEAD FORWARD
- TORSO FORWARD
- UNKNOWN
- PAUSED
- SERVER OFFLINE
- CAMERA ERROR

Do not show GOOD when the available image is insufficient to assess posture.

### Camera Settings

- Camera selection
- Preview
- Resolution selection where supported
- Frame rotation/mirroring settings
- Camera test
- Recalibration shortcut

### AI Settings

- Remote server URL
- API key
- Model name
- Timeout
- Test connection
- Model refresh
- Test inference
- Display last inference latency
- Show parsing errors without exposing API keys

### Monitoring Settings

- Snapshot interval
- Alert threshold
- Persistence duration
- Alert cooldown
- Monitoring enabled/disabled
- Optional debug mode

### Notification Settings

- Windows notifications
- Telegram Bot Token
- Telegram Chat ID
- Test Notification button
- Test Telegram button

### History

Display a timestamped event history with:

- Posture status
- Detected change
- Whether an alert was triggered
- Inference duration
- Error states

Do not save webcam images by default apart from confirmed calibration references.

Provide Clear History and Delete Calibration options.

## 4. Remote AI Integration

Use the endpoint:

`POST /v1/chat/completions`

For each inference, send:

- Reference image
- Current webcam image
- Structured comparison prompt

Use OpenAI-compatible image content with Base64 JPEG data URIs.

The request content should be ordered as:

1. Text label: "IMAGE_1: Reference posture"
2. Reference image
3. Text label: "IMAGE_2: Current posture"
4. Current image
5. Comparison instructions

Suggested inference parameters:

- temperature: 0
- max_tokens: 200
- stream: false

Use `response_format` with JSON Schema where supported. Fall back to strict JSON prompting and validation if necessary.

The initial target model is:

`Qwen/Qwen3-VL-4B-Instruct-GGUF:Q4_K_M`

Do not hardcode this model. Users must be able to select another compatible vision model from the GUI.

### AI Comparison Prompt

The prompt must first ask the model to report observable differences rather than immediately judging whether posture is good or bad.

Analyze these two images of the same person from a fixed webcam.

IMAGE_1 shows the reference sitting posture.

IMAGE_2 shows the current sitting posture.

Determine:

- Whether the head has moved forward relative to the shoulders.
- Whether the entire upper torso has moved toward the camera.
- Whether the head and torso are simply closer to the camera together.
- Whether the body is reclining backward.
- Whether there is insufficient visual evidence.

Important rules:

- Looking upward is not sufficient evidence of forward head posture.
- A larger head in the image does not prove forward head posture.
- Distinguish isolated head movement from whole-torso movement.
- Do not infer the shape of invisible body parts.
- Account for perspective differences.
- Do not classify normal reclining as bad posture.
- Return UNKNOWN whenever the distinction cannot be established.

### Required Structured Response

Define a Pydantic response model with these fields:

| Field | Allowed values |
|---|---|
| visibility | SUFFICIENT, INSUFFICIENT |
| head_relative_to_shoulders | FORWARD, UNCHANGED, UNKNOWN |
| torso_relative_to_reference | FORWARD, UNCHANGED, BACKWARD, UNKNOWN |
| change_magnitude | NONE, SMALL, MODERATE, LARGE, UNKNOWN |
| possible_camera_change | Boolean |
| visual_evidence | Short text |
| observation_notes | Short text |

Map these observations into application states using deterministic Python logic.

Do not trust an AI-provided alert decision.

Malformed, missing, contradictory or unsupported responses must result in UNKNOWN and must never trigger an alert.

## 5. Posture Evaluation Engine

Create an independent Python evaluation module.

Alert candidates:

**Forward Head**

- `head_relative_to_shoulders = FORWARD`
- Sufficient visibility
- At least MODERATE change
- Persisting across the configured time window

**Forward Torso Lean**

- `torso_relative_to_reference = FORWARD`
- Sufficient visibility
- At least MODERATE change
- Persisting across the configured time window

The model's comparison must provide actual visible evidence.

Do not treat simple proximity to the camera as proof of isolated head movement.

If the camera angle cannot reliably distinguish head movement from torso movement, classify the specific head-posture assessment as UNKNOWN.

### Alert Logic

- Store a rolling window of recent valid assessments.
- Default: at least 3 BAD assessments out of 4.
- Require a minimum elapsed abnormal duration.
- Never trigger from a single frame.
- Do not count UNKNOWN as BAD.
- Do not trigger when visibility is insufficient.
- Suppress repeated notifications during cooldown.
- Require recovery to neutral before treating a persistent unchanged abnormal condition as a new alert episode.
- Pause alert evaluation during server or camera errors.

Allow thresholds to be configured in the GUI.

Implement these rules as pure, unit-testable Python functions.

## 6. Webcam and Background Processing

Use OpenCV to capture webcam frames.

Requirements:

- Capture at configurable intervals.
- Resize images before sending to the remote model.
- Preserve aspect ratio.
- Prefer sufficient upper-body detail over unnecessary high resolution.
- JPEG encode frames in memory.
- Avoid temporary image files.
- Keep camera preview responsive.
- Run network inference outside the GUI thread.
- Never block the Qt event loop.
- Permit only one in-flight inference at a time.
- If inference takes longer than the capture interval, skip the next request rather than queueing stale snapshots.
- Release the webcam on application exit.
- Pause cleanly when camera access fails.

Use Qt worker threads/signals to communicate between the GUI and processing components.

## 7. Windows System Tray Integration

The application should run in the interactive Windows user session.

Implement:

- Tray icon showing monitoring status.
- Double-click to open the main window.
- Start/Pause Monitoring.
- Recalibrate.
- Open Settings.
- Exit.

Closing the main window should minimize to the system tray when background monitoring is enabled.

Exiting from the tray must stop webcam capture, cancel outstanding work and close the application cleanly.

Do not implement a Windows Service in V1. Webcam access and notifications should run in the logged-in user's desktop session.

Add optional Start with Windows, without requiring administrator privileges.

## 8. Notifications

Initial Windows notification examples:

"Your head appears to be moving forward relative to your usual sitting position."

"Your upper body has been leaning forward for approximately one minute."

These are gentle posture reminders, not medical diagnoses.

Support optional Telegram notifications through the Telegram Bot API.

Telegram messages should contain:

- Timestamp
- Detected issue
- Short explanation
- Duration

Do not send webcam images to Telegram automatically.

Implement a configurable alert cooldown.

Notification failure must not interrupt monitoring.

## 9. Persistence and Privacy

Store application configuration in the application directory.

Suggested paths:

- `.\settings.json`
- `.\calibration\`
- `.\history.db`
- `.\logs\`

Requirements:

- No continuous photo or video recording.
- Send image data only to the configured inference endpoint.
- Do not log Base64 image data or credentials.
- Calibration images remain local unless used in an inference request.
- Store API keys and Telegram tokens using Windows-protected credential storage where available, not plaintext JSON.
- Support HTTPS with certificate verification.
- Warn users when sending webcam images over unencrypted HTTP.
- Do not automatically upload data to cloud services.
- Allow complete deletion of calibration data and history.

## 10. Error Handling

Gracefully handle:

- AI server offline
- Server timeout
- Invalid server address
- Authentication failure
- Model unavailable
- Model without vision support
- Invalid JSON response
- Webcam disconnected
- Webcam used by another application
- Missing calibration
- Calibration camera mismatch
- Slow inference
- Telegram API failure

Monitoring must never interpret a network or parsing failure as a posture problem.

Display useful error messages in the GUI.

## 11. Suggested Project Structure

Use a maintainable package structure:

- `src/si_posture/main.py` — application entry point
- `src/si_posture/ui/` — main window, wizard, settings, history
- `src/si_posture/camera/` — capture, enumeration, calibration
- `src/si_posture/ai/` — llama.cpp API client, prompts, response schemas
- `src/si_posture/monitoring/` — scheduler, evaluator, state machine
- `src/si_posture/notifications/` — Windows and Telegram
- `src/si_posture/storage/` — settings, calibration, SQLite
- `src/si_posture/resources/` — icons and assets
- `tests/` — unit and integration tests
- `scripts/` — Windows development and build scripts
- `README.md`
- `pyproject.toml`
- `SI-Posture.spec`

Use clear interfaces and dependency injection where appropriate so API requests and webcam access can be mocked during tests.

## 12. Development Milestones

### Phase 1 — Windows GUI and Camera

- Implement the PySide6 application.
- Camera selection and live preview.
- Settings persistence.
- System tray integration.
- Start/Pause controls.

### Phase 2 — Remote AI Connection

- Configurable llama.cpp endpoint.
- Model discovery.
- Test Connection.
- Send two images to the selected model.
- Validate structured responses.
- Display AI observations in GUI.

### Phase 3 — Calibration and Monitoring

- First-run setup wizard.
- Reference posture capture and storage.
- Periodic frame capture.
- Comparison inference.
- Rolling-window posture evaluation.
- Windows notifications.

### Phase 4 — Improvements

- Telegram integration.
- SQLite history.
- Better error handling.
- Logging and diagnostics.
- Optional start with Windows.

### Phase 5 — Packaging and Testing

- Build Windows executable using PyInstaller.
- Prefer `--onedir` for the initial packaged application.
- Verify OpenCV webcam backend and Qt dependencies are bundled.
- Supply a Windows build script.
- Verify application works without a Python installation.
- Add setup and troubleshooting instructions.

## 13. Testing and Acceptance Criteria

Add automated tests covering:

1. Settings persistence and validation.
2. Endpoint URL normalization.
3. AI response parsing and rejection of invalid JSON.
4. Missing or unsupported vision model.
5. Reference/current image request ordering.
6. BAD/GOOD/UNKNOWN evaluation.
7. Three-of-four alert persistence.
8. Alert cooldown and recovery.
9. Slow server response and request skipping.
10. Disconnected camera/server.
11. Notifications with mocked delivery.
12. Safe shutdown and camera release.

Add optional manual integration tests using:

- `normal.jpg` vs `forward.jpg`
- `normal.jpg` vs `lean-back.jpg`
- `normal.jpg` vs `normal.jpg`

Expected observations:

- Forward comparison should detect visible forward movement.
- Lean-back comparison should recognize reclining and avoid treating it as a forward lean.
- Identical-image comparison should report no meaningful change.
- Head-forward versus whole-torso-forward classification may remain UNKNOWN where visual evidence is insufficient.

Do not assert that the model correctly diagnoses posture solely from these test images.

The application must remain responsive during inference, and no alert should be generated by a timeout, invalid response or uncertain posture evaluation.

## 14. Deliverables

Produce:

- Complete runnable source code
- PySide6 Windows desktop interface
- First-launch configuration wizard
- Remote llama.cpp integration
- Calibration workflow
- Continuous monitoring engine
- Windows and Telegram notifications
- Unit tests
- Windows packaging/build script
- README with installation, usage and troubleshooting

Do not stop after implementing skeletons, pseudocode or mock screens.

Implement incrementally, run available tests after each milestone and report what has been verified.

Where Windows hardware or the remote AI server is unavailable during development, use mock interfaces for tests and clearly identify the remaining manual validation steps.

**Priority: Deliver a stable, working Windows application over adding unnecessary features.**

No MediaPipe integration is required for V1.