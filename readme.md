# PS4 — Local AI Meeting Companion

A privacy-focused, offline-first AI meeting companion designed to capture conversations, transcribe them locally, and later generate useful meeting conclusions using a local LLM.

The project is currently being developed and tested on a **Linux/WSL laptop environment** and is planned to move to a **Raspberry Pi 5** after the software pipeline is stable.

---

## 1. Project Goal

The goal of PS4 is to build a small local AI assistant that can:

1. Capture audio from a microphone.
2. Detect when people are speaking.
3. Record conversation segments.
4. Transcribe speech locally using Whisper.
5. Store the complete meeting transcription.
6. Send the accumulated transcription to a local LLM.
7. Generate:

   * Meeting summary
   * Key points
   * Decisions
   * Action items
   * Conclusions
8. Eventually operate on Raspberry Pi 5.
9. Provide physical status indicators using LEDs.
10. Provide a physical switch for controlling internet connectivity.

The system is intended to work locally as much as possible, minimizing dependence on cloud APIs.

---

# 2. Current Architecture

Current planned pipeline:

```text
                ┌──────────────────┐
                │   Laptop Mic     │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Audio Capture     │
                │ sounddevice       │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Voice Activity   │
                │ Detection (VAD)  │
                │ webrtcvad        │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ WAV Audio File   │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ whisper.cpp      │
                │ small.en         │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Transcription    │
                │ meeting.json     │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Local LLM        │
                │ Ollama + Llama   │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Meeting          │
                │ Conclusion       │
                └──────────────────┘
```

---

# 3. Technology Stack

| Component         | Current Technology              |
| ----------------- | ------------------------------- |
| Development OS    | Linux / WSL                     |
| Language          | Python                          |
| Audio capture     | `sounddevice`                   |
| Voice detection   | `webrtcvad`                     |
| Speech-to-text    | `whisper.cpp`                   |
| Whisper model     | `small.en`                      |
| LLM runtime       | Ollama                          |
| LLM               | Llama                           |
| Meeting storage   | JSON                            |
| Current hardware  | Laptop                          |
| Future hardware   | Raspberry Pi 5                  |
| Future indicators | 3 physical LEDs                 |
| Future control    | Physical internet toggle switch |

---

# 4. Project Directory

The project is currently being moved away from the Windows filesystem and developed directly inside Linux.

Recommended project location:

```text
/home/ashish/ps4
```

Example structure:

```text
ps4/
│
├── whisper.cpp/
│
├── models/
│   └── llama/
│
├── audio/
│
├── transcripts/
│
├── meeting.json
│
├── scripts/
│
├── .venv/
│
└── README.md
```

The exact structure may change as development continues.

---

# 5. Linux / WSL Setup

The project is being developed inside Linux/WSL instead of:

```text
/mnt/d/ps4
```

The preferred location is:

```text
/home/ashish/ps4
```

This avoids unnecessary interaction with the Windows filesystem and makes the environment closer to the eventual Raspberry Pi Linux environment.

Check the current directory:

```bash
pwd
```

Example:

```text
/home/ashish/ps4
```

List files:

```bash
ls -lah
```

---

# 6. Python Virtual Environment

Create the virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

After activation, the terminal should show something similar to:

```text
(.venv) ashish@Ashish-Laptop:~/ps4$
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

---

# 7. Python Dependencies

The current audio-processing pipeline uses:

```bash
pip install sounddevice
pip install webrtcvad
```

Other packages can be installed as required.

Check installed packages:

```bash
pip list
```

---

# 8. Microphone Testing

The project uses the laptop microphone through Python's `sounddevice`.

Check audio devices:

```bash
python -c "import sounddevice as sd; print(sd.query_devices())"
```

To check the default input device:

```bash
python -c "import sounddevice as sd; print(sd.default.device)"
```

A basic audio test can be performed using `sounddevice`.

---

# 9. Audio Configuration

The current audio configuration is designed around speech recognition:

```python
SAMPLE_RATE = 16000
CHANNELS = 1
FRAME_MS = 30
FRAME_SAMPLES = SAMPLE_RATE * FRAME_MS // 1000
VAD_MODE = 2
```

### Explanation

### Sample rate

```text
16000 Hz
```

This is suitable for speech recognition.

### Channels

```text
1
```

Mono audio is sufficient for speech transcription and reduces processing requirements.

### Frame duration

```text
30 ms
```

The audio stream is processed in small frames for voice activity detection.

### VAD mode

```text
2
```

`webrtcvad` provides different aggressiveness levels.

The current project uses:

```python
VAD_MODE = 2
```

This can be adjusted later depending on real-world meeting conditions.

---

# 10. Voice Activity Detection

The project uses:

```text
webrtcvad
```

to determine whether speech is currently present.

Conceptually:

```text
Microphone
    │
    ▼
Audio frame
    │
    ▼
VAD
 ┌──┴───┐
 │      │
Speech  Silence
 │      │
 ▼      ▼
Record  Continue waiting
```

The purpose is to avoid continuously saving large amounts of silence.

---

# 11. Recording Logic

The current Python recording system:

1. Opens the microphone.
2. Reads small audio frames.
3. Runs VAD.
4. Detects speech.
5. Starts/continues recording.
6. Detects silence.
7. Stops after the configured amount of silence.
8. Saves the resulting audio as a WAV file.

This provides a more efficient workflow than continuously recording an entire meeting into one large stream.

---

# 12. Whisper.cpp

The project uses `whisper.cpp` for local speech-to-text.

Repository:

[whisper.cpp GitHub repository](https://github.com/ggml-org/whisper.cpp?utm_source=chatgpt.com)

Clone it:

```bash
cd ~/ps4

git clone https://github.com/ggml-org/whisper.cpp.git
```

Enter the directory:

```bash
cd whisper.cpp
```

---

# 13. Building whisper.cpp

Install the basic build tools if necessary:

```bash
sudo apt update
sudo apt install build-essential cmake git
```

Create/build using CMake:

```bash
cmake -B build
cmake --build build -j
```

Check the generated binaries:

```bash
find build -type f -iname "whisper-cli"
```

Depending on the build configuration, the executable should be inside the build directory.

Example:

```text
build/bin/whisper-cli
```

---

# 14. Whisper Models

The project initially considered different Whisper models, including:

```text
base.en
small.en
```

The current plan is to use:

```text
small.en
```

The reason is to obtain better transcription quality while still keeping the model practical for local processing.

Model selection can be revisited later when testing on Raspberry Pi 5.

---

# 15. Downloading Whisper Models

From the `whisper.cpp` directory:

```bash
cd ~/ps4/whisper.cpp
```

Check the available model download scripts:

```bash
ls models
```

For the English small model, use the model download mechanism provided by the current `whisper.cpp` version.

After downloading, verify:

```bash
ls -lh models/
```

The model file should be present before attempting transcription.

---

# 16. Running Whisper Manually

A typical workflow is:

```bash
./build/bin/whisper-cli \
    -m models/ggml-small.en.bin \
    -f audio.wav
```

The exact model filename/path may differ depending on the `whisper.cpp` version and download method.

Check available options:

```bash
./build/bin/whisper-cli --help
```

This command is useful whenever command-line options change between versions.

---

# 17. Current Transcription Pipeline

The current system is moving toward:

```text
Microphone
     ↓
Python recorder
     ↓
VAD
     ↓
WAV file
     ↓
whisper.cpp
     ↓
Text
     ↓
meeting.json
```

Each speech segment can be transcribed individually.

The important design decision is that the individual transcriptions should not remain isolated forever.

They should be accumulated into one meeting-level data structure.

---

# 18. meeting.json

The project will use:

```text
meeting.json
```

as the central storage file for one meeting.

The idea is:

```text
Meeting starts
      │
      ▼
Speech segment 1
      │
      ▼
Transcribe
      │
      ▼
Add to meeting.json
      │
      ▼
Speech segment 2
      │
      ▼
Transcribe
      │
      ▼
Add to meeting.json
      │
      ▼
...
      │
      ▼
Meeting ends
      │
      ▼
Send complete meeting data to Llama
```

This means the LLM does not need to process every sentence independently.

Instead, it receives the accumulated meeting context.

---

# 19. Example meeting.json

A possible structure:

```json
{
    "meeting_id": "2026-09-25-001",
    "started_at": "2026-09-25T20:00:00",
    "ended_at": null,
    "segments": [
        {
            "timestamp": "2026-09-25T20:01:12",
            "text": "We need to finish the hardware prototype."
        },
        {
            "timestamp": "2026-09-25T20:02:30",
            "text": "The Raspberry Pi integration can be done next."
        }
    ]
}
```

At the end of the meeting:

```text
meeting.json
      │
      ▼
Complete transcript
      │
      ▼
Llama
      │
      ▼
Meeting summary
```

The exact JSON schema can be improved as development continues.

---

# 20. Ollama

The project uses Ollama to run a local LLM.

Ollama:

[Ollama official website](https://ollama.com/?utm_source=chatgpt.com)

The important advantage for this project is that the LLM can run locally instead of sending meeting conversations to a cloud API.

---

# 21. Ollama Model Storage

On the current Linux setup, Ollama's model directory was not found at:

```bash
~/.ollama/models
```

because the Ollama installation is using a system-level location.

The model directory was found at:

```bash
/usr/share/ollama/.ollama/models
```

To inspect it:

```bash
sudo ls -lah /usr/share/ollama/.ollama/models
```

Example:

```text
drwxr-xr-x 5 ollama ollama ...
```

This indicates that the Ollama service is using the `ollama` system user.

---

# 22. Check Ollama

Check whether Ollama is installed:

```bash
ollama --version
```

Check available models:

```bash
ollama list
```

Run a model:

```bash
ollama run <model-name>
```

For example, if the selected model is a Llama model:

```bash
ollama run <llama-model>
```

The exact model should be selected based on available RAM/GPU resources and later Raspberry Pi 5 requirements.

---

# 23. Planned LLM Pipeline

The eventual workflow is:

```text
meeting.json
     │
     ▼
Python
     │
     ▼
Create prompt
     │
     ▼
Ollama
     │
     ▼
Llama
     │
     ▼
Structured meeting result
```

The LLM should eventually produce something similar to:

```json
{
    "summary": "...",
    "key_points": [],
    "decisions": [],
    "action_items": [],
    "conclusion": "..."
}
```

This will make the output easier for the rest of the application to consume.

---

# 24. Important Design Decision

The project should **not** send every small transcription directly to the LLM.

Instead:

```text
Audio
 ↓
Transcription
 ↓
meeting.json
 ↓
Complete meeting context
 ↓
Llama
```

This provides the LLM with the complete conversation context when generating the final conclusion.

Later, if meetings become very long, the system can introduce:

```text
Chunking
+
Intermediate summaries
+
Final summary
```

to prevent the prompt from becoming too large.

---

# 25. Current Development Environment

The project is currently being developed on:

```text
Laptop
   │
   └── Linux / WSL
          │
          ├── Python
          ├── whisper.cpp
          └── Ollama
```

The laptop is being used as the initial development platform because it is easier to debug and provides more computational resources.

---

# 26. Why Laptop First?

The planned final hardware is:

```text
Raspberry Pi 5
```

However, development is currently being done on a laptop.

This is intentional.

The software can first be developed and tested on a more powerful machine:

```text
Laptop
   ↓
Stable software pipeline
   ↓
Optimize
   ↓
Raspberry Pi 5
```

This avoids simultaneously debugging:

* Audio hardware
* Raspberry Pi configuration
* Whisper performance
* LLM performance
* Python code
* GPIO
* Power issues

---

# 27. Raspberry Pi 5 Migration

The planned final architecture is:

```text
                 Raspberry Pi 5
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   Microphone       LEDs        Physical Switch
        │
        ▼
      VAD
        │
        ▼
    whisper.cpp
        │
        ▼
   meeting.json
        │
        ▼
      Llama
        │
        ▼
    Conclusion
```

The software stack should remain mostly Linux/Python based, making the migration easier.

---

# 28. Planned Physical LEDs

The project will eventually have **3 physical LEDs**.

Possible states:

```text
LED 1 → Recording
LED 2 → Processing / Transcribing
LED 3 → LLM / Meeting result
```

The exact meaning can be finalized later.

Example:

```text
Recording:
LED 1 = ON

Transcribing:
LED 2 = ON

Generating summary:
LED 3 = ON
```

The Raspberry Pi GPIO pins will control these LEDs.

---

# 29. Planned Physical Internet Switch

The project will also include a physical switch for controlling internet connectivity.

Conceptually:

```text
             Physical Switch
                    │
                    ▼
              Raspberry Pi
                    │
             ┌──────┴──────┐
             │             │
         Internet ON   Internet OFF
```

This is especially useful for a privacy-focused offline AI device.

The software should detect the switch state and enable/disable the appropriate network interface or networking behavior.

The exact implementation will be decided during the Raspberry Pi hardware stage.

---

# 30. Current Progress

## Completed / Working

### Development environment

* Linux/WSL environment established.
* Project being moved to Linux filesystem.
* Python virtual environment created.
* Microphone access tested.

### Audio

* `sounddevice` integrated.
* 16 kHz mono audio configured.
* Frame-based processing implemented.

### Voice detection

* `webrtcvad` integrated.
* Speech/silence detection working.
* Silence-based recording termination implemented.

### Speech-to-text

* `whisper.cpp` cloned and built.
* Whisper CLI available.
* `base.en` and `small.en` considered.
* Current target model: `small.en`.

### LLM

* Ollama installed/configured.
* Ollama model storage identified.
* Local Llama-based processing planned.

### Meeting data

* Decision made to maintain a single:

```text
meeting.json
```

for each meeting.

---

# 31. Current Development Priority

The next major software task is to connect everything together:

```text
Microphone
    ↓
VAD
    ↓
Audio segment
    ↓
whisper.cpp
    ↓
Transcription
    ↓
meeting.json
    ↓
Meeting ends
    ↓
Ollama
    ↓
Llama
    ↓
Summary / Conclusion
```

The immediate focus should therefore be the Python integration between:

```text
Audio recorder
        +
whisper.cpp
        +
meeting.json
```

After this is stable, integrate:

```text
meeting.json
        ↓
Ollama
        ↓
Llama
```

---

# 32. Useful Commands

## Linux

```bash
pwd
ls -lah
cd ~/ps4
```

Check OS:

```bash
uname -a
```

Check Python:

```bash
python3 --version
```

Check Git:

```bash
git --version
```

---

## Python environment

Activate:

```bash
source ~/ps4/.venv/bin/activate
```

Deactivate:

```bash
deactivate
```

Install packages:

```bash
pip install <package>
```

List packages:

```bash
pip list
```

---

## Audio

List audio devices:

```bash
python -c "import sounddevice as sd; print(sd.query_devices())"
```

Check default device:

```bash
python -c "import sounddevice as sd; print(sd.default.device)"
```

---

## whisper.cpp

```bash
cd ~/ps4/whisper.cpp
```

Build:

```bash
cmake -B build
cmake --build build -j
```

Find binaries:

```bash
find build -type f -iname "whisper-cli"
```

Help:

```bash
./build/bin/whisper-cli --help
```

---

## Ollama

Check installation:

```bash
ollama --version
```

List models:

```bash
ollama list
```

Run model:

```bash
ollama run <model-name>
```

Check Ollama model storage:

```bash
sudo ls -lah /usr/share/ollama/.ollama/models
```

---

# 33. Troubleshooting

## Python environment not activated

If the terminal does not show:

```text
(.venv)
```

run:

```bash
source ~/ps4/.venv/bin/activate
```

---

## Microphone not detected

Run:

```bash
python -c "import sounddevice as sd; print(sd.query_devices())"
```

If no input device appears, check the WSL/Linux audio configuration.

---

## whisper-cli not found

Run:

```bash
cd ~/ps4/whisper.cpp
find build -type f -iname "whisper-cli"
```

Then use the actual path returned.

---

## Ollama model directory missing

Do not assume the model directory is:

```bash
~/.ollama/models
```

On this development environment, inspect:

```bash
sudo ls -lah /usr/share/ollama/.ollama/models
```

---

# 34. Git Workflow

Check repository status:

```bash
git status
```

Add changes:

```bash
git add .
```

Commit:

```bash
git commit -m "describe changes"
```

View history:

```bash
git log --oneline
```

---

# 35. Future Architecture

The final system is expected to evolve toward:

```text
                    ┌───────────────────┐
                    │   Physical Mic    │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Audio Capture     │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │       VAD         │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   whisper.cpp     │
                    │     small.en      │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   meeting.json    │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │      Ollama       │
                    │       Llama       │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Meeting Summary   │
                    │ Decisions         │
                    │ Action Items      │
                    │ Conclusion        │
                    └───────────────────┘

       Raspberry Pi GPIO
       ├── LED 1
       ├── LED 2
       ├── LED 3
       └── Internet Switch
```

---

# 36. Development Philosophy

The project should be developed incrementally.

### Stage 1 — Audio

```text
Microphone → WAV
```

### Stage 2 — VAD

```text
Microphone → VAD → Speech segments
```

### Stage 3 — Whisper

```text
Speech → whisper.cpp → Text
```

### Stage 4 — Meeting storage

```text
Text → meeting.json
```

### Stage 5 — Local LLM

```text
meeting.json → Ollama → Llama
```

### Stage 6 — Complete software pipeline

```text
Microphone
→ VAD
→ Whisper
→ meeting.json
→ Llama
→ Conclusion
```

### Stage 7 — Raspberry Pi

Move the stable software pipeline to:

```text
Raspberry Pi 5
```

### Stage 8 — Hardware controls

Add:

```text
3 LEDs
+
Internet switch
```

---

# 37. Important Principle

The project should remain **local-first**.

The preferred data flow is:

```text
Microphone
    ↓
Local processing
    ↓
Local transcription
    ↓
Local storage
    ↓
Local LLM
```

Internet access should not be required for the core meeting transcription and summarization workflow once all required models and software are installed.

---

# 38. Current Status

```text
[████████████████░░░░] Development

✓ Linux/WSL environment
✓ Python environment
✓ Microphone
✓ Audio capture
✓ VAD
✓ whisper.cpp
✓ Whisper model selection
✓ Ollama
✓ Llama integration planning
✓ meeting.json design

→ Integrate transcription into meeting.json
→ Integrate meeting.json with Ollama/Llama
→ Generate structured meeting conclusion
→ Optimize
→ Raspberry Pi 5 migration
→ GPIO LEDs
→ Physical internet switch
```

---

# 39. Next Immediate Task

The next implementation step is to modify the current Python recording/transcription script so that every successfully transcribed audio segment is appended to:

```text
meeting.json
```

Once the meeting is finished, the complete `meeting.json` can be passed to the local Llama model through Ollama.

That will establish the first complete end-to-end software pipeline:

```text
MIC
 ↓
VAD
 ↓
WAV
 ↓
Whisper
 ↓
meeting.json
 ↓
Llama
 ↓
Meeting Conclusion
```

---

## Project Status

**Current phase:** Local laptop/WSL prototype

**Speech recognition:** `whisper.cpp + small.en`

**LLM:** `Ollama + Llama`

**Meeting storage:** `meeting.json`

**Target hardware:** Raspberry Pi 5

**Future hardware:** 3 LEDs + physical internet switch
