# PS4 --- Nova Local AI Assistant

> **PS4** is a privacy-first, local AI assistant designed to run
> primarily on Linux.\
> The current implementation combines **voice input, local
> speech-to-text, a local LLM, tool-based actions, meeting-transcript
> intelligence, document summarization, web access, date/time tools,
> logging, and voice output**.
>
> The project is currently operated mainly through the **terminal +
> voice interface**. Hardware/LED integration and a graphical frontend
> are planned extensions rather than requirements for the current
> software demonstration.

------------------------------------------------------------------------

## Table of Contents

-   [1. Project Overview](#1-project-overview)
-   [2. Current Status](#2-current-status)
-   [3. Core Capabilities](#3-core-capabilities)
-   [4. System Architecture](#4-system-architecture)
-   [5. Voice Pipeline](#5-voice-pipeline)
-   [6. AI and Model Layer](#6-ai-and-model-layer)
-   [7. Tool Architecture](#7-tool-architecture)
-   [8. Meeting Assistant](#8-meeting-assistant)
-   [9. Document Summarization](#9-document-summarization)
-   [10. Web / Internet Agent](#10-web--internet-agent)
-   [11. Date and Time Retrieval](#11-date-and-time-retrieval)
-   [12. Logging](#12-logging)
-   [13. Linux Environment](#13-linux-environment)
-   [14. Project Setup](#14-project-setup)
-   [15. Whisper.cpp Setup](#15-whispercpp-setup)
-   [16. Ollama / Llama Setup](#16-ollama--llama-setup)
-   [17. Audio Setup and Diagnostics](#17-audio-setup-and-diagnostics)
-   [18. Running Nova](#18-running-nova)
-   [19. Useful Commands](#19-useful-commands)
-   [20. Suggested Project Structure](#20-suggested-project-structure)
-   [21. Request Lifecycle](#21-request-lifecycle)
-   [22. Configuration](#22-configuration)
-   [23. Troubleshooting](#23-troubleshooting)
-   [24. Demonstration Guide](#24-demonstration-guide)
-   [25. Hardware / LED Extension](#25-hardware--led-extension)
-   [26. Performance Notes](#26-performance-notes)
-   [27. Development Practices](#27-development-practices)
-   [28. Future Roadmap](#28-future-roadmap)
-   [29. Quick Start](#29-quick-start)

------------------------------------------------------------------------

# 1. Project Overview

Nova is a local AI assistant intended to provide an assistant-like
experience without requiring the complete AI pipeline to run in the
cloud.

The main idea is:

``` text
             USER
               │
               │ Voice
               ▼
        ┌───────────────┐
        │ Microphone    │
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │ Audio Capture │
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │ Whisper.cpp    │
        │ Speech → Text │
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │ Nova Agent    │
        │ Orchestrator  │
        └───────┬───────┘
                │
       ┌────────┼─────────────┐
       │        │             │
       ▼        ▼             ▼
    Tools     LLM          Web Agent
       │        │             │
       │        ▼             │
       │     Ollama           │
       │     + Llama          │
       │                      │
       └────────┬─────────────┘
                │
                ▼
        ┌───────────────┐
        │ Final Answer  │
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │ Voice Output  │
        └───────┬───────┘
                │
                ▼
              USER
```

The important design principle is that **the LLM is not expected to do
everything itself**. Nova can select or call deterministic tools when a
task requires reliable information or an operation.

------------------------------------------------------------------------

# 2. Current Status

## Implemented / Working

-   Linux-native project environment.
-   Python virtual environment.
-   `whisper.cpp` for local speech-to-text.
-   Local LLM execution through **Ollama**.
-   Llama-family local model support.
-   Voice command → transcription → agent → response flow.
-   Wake phrase detection.
-   Terminal-based interaction.
-   Voice response/output.
-   Central tool list architecture.
-   Date/time tool (`time_tools.py` / `get_current_datetime()`).
-   Meeting transcript retrieval/search concepts.
-   Meeting-aware assistant prompt.
-   Web-agent functionality.
-   Document summarization capability.
-   Logging of assistant activity.
-   Audio-device diagnostics through PulseAudio/PipeWire tools.
-   Project moved toward a Linux-only workflow rather than developing
    from `/mnt/...` Windows-mounted paths.
-   Current demonstration can be performed without physical hardware.

## Not Required for the Current Software Demo

-   Physical LED hardware.
-   Custom PCB.
-   Embedded controller.
-   Final graphical frontend.
-   Dedicated enclosure.
-   Production deployment.

The current system can be demonstrated using:

``` text
Laptop
  │
  ├── Microphone
  ├── Speaker / Headphones
  ├── Terminal
  ├── Whisper.cpp
  ├── Ollama
  └── Nova
```

------------------------------------------------------------------------

# 3. Core Capabilities

  -----------------------------------------------------------------------
  Capability              Purpose                 Main component
  ----------------------- ----------------------- -----------------------
  Wake phrase             Activates Nova          Voice/input layer

  Speech recognition      Converts speech to text Whisper.cpp

  Local reasoning         Generates responses /   Ollama + Llama
                          decides actions         

  Tools                   Performs deterministic  Python tools
                          operations              

  Date/time               Reliable current        `time_tools.py`
                          date/time               

  Meeting assistant       Understands/searches    Transcript tools + LLM
                          transcript              

  Web agent               Retrieves current       Web/browser layer
                          online information      

  Document summarization  Summarizes user         Document pipeline + LLM
                          documents               

  Logging                 Records system activity Python logging

  Voice response          Speaks result back      TTS/output layer

  Terminal UI             Displays live execution CLI
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 4. System Architecture

## High-level architecture

``` mermaid
flowchart TD
    U[User]
    MIC[Microphone]
    STT[Whisper.cpp]
    WAKE[Wake Phrase Detection]
    AGENT[Nova Agent]
    TOOLS[Tool Registry]
    LLM[Ollama + Llama]
    WEB[Web Agent]
    TIME[Time Tool]
    MEET[Meeting Transcript Tools]
    DOC[Document Summarization]
    LOG[Logging]
    TTS[Voice Output]
    TERM[Terminal]

    U --> MIC
    MIC --> STT
    STT --> WAKE
    WAKE --> AGENT

    AGENT --> LLM
    AGENT --> TOOLS

    TOOLS --> TIME
    TOOLS --> MEET
    TOOLS --> DOC
    TOOLS --> WEB

    AGENT --> LOG
    LLM --> AGENT

    AGENT --> TTS
    AGENT --> TERM
    TTS --> U
    TERM --> U
```

## Layered design

### Layer 1 --- Input

Responsible for:

-   Microphone capture.
-   Audio files / streams.
-   Wake phrase detection.
-   Speech recognition.

### Layer 2 --- Agent

Responsible for:

-   Receiving the user's command.
-   Maintaining the system prompt.
-   Selecting tools.
-   Calling the LLM.
-   Combining tool results with model reasoning.
-   Producing the final response.

### Layer 3 --- Tools

Responsible for deterministic functionality such as:

-   Date/time.
-   Transcript retrieval.
-   Transcript search.
-   Document operations.
-   Web operations.
-   Other future integrations.

### Layer 4 --- Model

Ollama provides the local model runtime.

The model is used for:

-   Understanding natural language.
-   Reasoning.
-   Tool selection / orchestration.
-   Summarization.
-   Generating final responses.

### Layer 5 --- Output

The result can be:

-   Printed in the terminal.
-   Spoken through the audio output.
-   Eventually reflected through LEDs or a GUI.

------------------------------------------------------------------------

# 5. Voice Pipeline

The current voice flow is:

``` text
Microphone
    │
    ▼
Audio Capture
    │
    ▼
Whisper.cpp
    │
    ▼
Transcribed Text
    │
    ▼
Wake Phrase / Command Detection
    │
    ▼
Nova Agent
    │
    ├── Local LLM
    ├── Tools
    └── Web / Documents / Transcript
    │
    ▼
Final Response
    │
    ├── Terminal
    └── TTS
```

A typical execution looks like:

``` text
[Nova] Wake phrase detected.
[Nova] Command: fetch the latest date of India from the browser.
[START SPEECH RECOGNITION]
...
[USER TEXT] ...
[TOOL] ...
[LLM] ...
[Nova] ...
```

The exact log text can change as the implementation evolves.

------------------------------------------------------------------------

# 6. AI and Model Layer

## 6.1 Whisper.cpp

`whisper.cpp` is used for local speech recognition.

Its role is:

``` text
Audio → Speech-to-Text
```

This keeps the transcription stage local.

Typical repository location:

``` text
whisper.cpp/
```

Typical model location:

``` text
models/
```

or another configured model directory.

### Important performance consideration

Whisper model size affects:

-   Startup time.
-   RAM usage.
-   CPU/GPU usage.
-   Transcription latency.

For a demonstration, choose a model that provides an acceptable balance
between accuracy and response time.

------------------------------------------------------------------------

## 6.2 Ollama

Ollama is used as the local LLM runtime.

Architecture:

``` text
Nova Python Code
       │
       ▼
    Ollama
       │
       ▼
 Local Llama Model
       │
       ▼
   Response
```

The model files can be large. A model that is no longer required can be
removed from Ollama's model store after confirming that no part of the
project depends on it.

List installed models:

``` bash
ollama list
```

Show running models:

``` bash
ollama ps
```

Run a model manually:

``` bash
ollama run <model-name>
```

Remove an unused model:

``` bash
ollama rm <model-name>
```

> Replace `<model-name>` with the exact name shown by `ollama list`.

------------------------------------------------------------------------

# 7. Tool Architecture

Nova uses a tool-oriented design instead of putting every operation
directly inside the main agent file.

Conceptually:

``` text
                 Nova Agent
                     │
                     ▼
               Tool Registry
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
  Time Tools    Meeting Tools   Web Tools
       │             │             │
       ▼             ▼             ▼
 Current Time    Transcript      Internet
```

A central tool list can be maintained in a dedicated module such as:

``` python
from tools import Tools
```

The exact import should match the current project structure.

## Why this architecture?

Without tools:

``` text
User → LLM → Answer
```

With tools:

``` text
User
  │
  ▼
LLM / Agent
  │
  ├── Can answer directly
  │
  ├── Can call time tool
  │
  ├── Can search transcript
  │
  ├── Can summarize document
  │
  └── Can use web agent
```

This makes the system easier to extend and gives deterministic
operations a dedicated implementation.

------------------------------------------------------------------------

# 8. Meeting Assistant

Nova also contains a meeting-assistant design.

The meeting assistant is instructed to treat the **meeting transcript as
the primary source of truth**.

## Supported transcript operations

1.  Retrieve transcript between timestamps.
2.  Retrieve the most recent transcript portion.
3.  Search the transcript for a keyword or phrase.

Architecture:

``` text
Meeting Audio / Transcript
          │
          ▼
   Transcript Storage
          │
          ▼
    Transcript Tools
          │
     ┌────┼────┐
     ▼    ▼    ▼
   Range Recent Search
     │    │    │
     └────┼────┘
          ▼
       Nova LLM
          │
          ▼
   Meeting Answer
```

## Meeting assistant rules

The assistant should:

-   Use the transcript as the source of truth.
-   Avoid inventing meeting facts.
-   Retrieve relevant transcript sections when necessary.
-   Answer questions using evidence from the transcript.
-   Clearly distinguish transcript facts from general reasoning.

Example:

``` text
User:
"What did we decide about the database?"

Nova:
1. Searches the transcript.
2. Retrieves relevant section.
3. Sends the evidence to the model.
4. Produces a concise answer.
```

------------------------------------------------------------------------

# 9. Document Summarization

The project includes document summarization as an additional assistant
capability.

General flow:

``` text
Document
   │
   ▼
Text Extraction
   │
   ▼
Relevant Content
   │
   ▼
Nova / Local LLM
   │
   ▼
Summary
```

The feature can be extended to support:

-   PDF.
-   Text files.
-   Markdown.
-   Office documents.
-   Other formats supported by the project's extraction layer.

For large documents, avoid sending the complete document to the model in
one request if the model/context window becomes a bottleneck. A chunk →
summarize → combine strategy can be used.

------------------------------------------------------------------------

# 10. Web / Internet Agent

Nova can use a web-agent path when the user asks for information that
should come from the internet.

This is different from a normal local-model question.

## Local question

``` text
User → Nova → Local LLM → Answer
```

## Current-information question

``` text
User
  │
  ▼
Nova Agent
  │
  ▼
Web Agent
  │
  ▼
Internet
  │
  ▼
Retrieved Information
  │
  ▼
Nova / LLM
  │
  ▼
Answer
```

Use the web path when the request depends on information such as:

-   Latest information.
-   Current dates from online sources.
-   Current websites.
-   Current online documents.
-   Information unavailable in the local model.

The agent should not pretend that a local model's static knowledge is
live internet data.

------------------------------------------------------------------------

# 11. Date and Time Retrieval

A dedicated time tool was added to avoid relying on the LLM for the
current date/time.

Example concept:

``` python
get_current_datetime()
```

Architecture:

``` text
User: "What is today's date?"
             │
             ▼
        Nova Agent
             │
             ▼
         Time Tool
             │
             ▼
      System Date/Time
             │
             ▼
          Response
```

This is more reliable than asking the language model to guess the
current date.

A tool-based design also makes the capability reusable by other agent
operations.

------------------------------------------------------------------------

# 12. Logging

The project maintains logs so that important events can be inspected
later.

Examples of events worth logging:

-   Wake phrase detected.
-   User command.
-   Selected model.
-   Tool calls.
-   Tool results/errors.
-   Speech recognition start/end.
-   LLM start/end.
-   Exceptions.
-   Final response.
-   Web-agent activity.

Typical Python logging setup:

``` python
import logging

logger = logging.getLogger(__name__)
```

A module can then use:

``` python
logger.info("User command: %s", user_command)
logger.info("Using model: %s", model_name)
logger.error("Operation failed: %s", error)
```

## Why logging matters

During a live demonstration, logs make the internal pipeline visible:

``` text
Wake detected
     ↓
Speech recognized
     ↓
Command received
     ↓
Tool selected
     ↓
Tool completed
     ↓
LLM generated response
     ↓
Voice response
```

For a distributed project, logging should be configured centrally where
practical instead of manually reinventing handlers in every file.

------------------------------------------------------------------------

# 13. Linux Environment

The project has been moved toward a native Linux environment.

Recommended location:

``` text
/home/<user>/Projects/ps4
```

or:

``` text
/home/<user>/ps4
```

Avoid using a Windows-mounted path such as:

``` text
/mnt/d/ps4
```

for the main Linux development environment when possible.

## Why native Linux?

Benefits include:

-   Better Linux audio integration.
-   Simpler permissions.
-   Better native tool behavior.
-   No WSL filesystem boundary for the main project.
-   Easier access to Linux processes and services.
-   Cleaner Python/compiled-binary paths.

Check the current directory:

``` bash
pwd
```

Example:

``` text
/home/ashish/Projects/ps4
```

------------------------------------------------------------------------

# 14. Project Setup

## 14.1 Install system dependencies

Update package metadata:

``` bash
sudo apt update
```

Install common build and Python dependencies:

``` bash
sudo apt install -y \
    git \
    build-essential \
    cmake \
    python3 \
    python3-venv \
    python3-pip \
    pkg-config \
    ffmpeg \
    portaudio19-dev
```

Depending on the exact audio stack, additional PulseAudio/PipeWire
utilities may be useful:

``` bash
sudo apt install -y pulseaudio-utils
```

On systems using PipeWire, also inspect:

``` bash
wpctl status
```

------------------------------------------------------------------------

## 14.2 Clone the project

Example:

``` bash
cd ~/Projects
git clone <repository-url> ps4
cd ps4
```

If the repository is already available:

``` bash
cd ~/Projects/ps4
```

------------------------------------------------------------------------

## 14.3 Create the Python virtual environment

``` bash
python3 -m venv .venv
```

Activate:

``` bash
source .venv/bin/activate
```

Verify:

``` bash
which python
python --version
pip --version
```

The shell should show the virtual environment:

``` text
(.venv)
```

Deactivate when finished:

``` bash
deactivate
```

------------------------------------------------------------------------

## 14.4 Install Python packages

If the project contains a requirements file:

``` bash
pip install -r requirements.txt
```

If one does not exist yet, install dependencies according to the imports
used by the project and then generate one:

``` bash
pip freeze > requirements.txt
```

Do not blindly install every package from another machine; keep the
requirements file aligned with the actual project.

------------------------------------------------------------------------

# 15. Whisper.cpp Setup

## 15.1 Clone Whisper.cpp

From the project root:

``` bash
git clone https://github.com/ggerganov/whisper.cpp.git
```

Enter the directory:

``` bash
cd whisper.cpp
```

Build it using the current upstream build instructions.

A common CMake workflow is:

``` bash
cmake -B build
cmake --build build -j$(nproc)
```

Return to the project:

``` bash
cd ..
```

------------------------------------------------------------------------

## 15.2 Verify the build

Inspect the generated binaries:

``` bash
find whisper.cpp/build -maxdepth 3 -type f -executable | head -50
```

If the project uses a configured binary path, keep that path in the
project configuration instead of hard-coding it in multiple Python
files.

------------------------------------------------------------------------

## 15.3 Whisper model

Store the selected Whisper model in the project's model directory or
another configured location.

Example:

``` text
ps4/
├── models/
│   └── whisper/
└── whisper.cpp/
```

The exact model filename depends on the Whisper model selected.

Check the configured model path before running:

``` bash
grep -R "MODEL" -n config.py *.py 2>/dev/null
```

------------------------------------------------------------------------

## 15.4 Manual transcription test

Before debugging Nova, verify Whisper independently.

Use the Whisper.cpp executable and model configured by the project.

The exact command depends on the version of Whisper.cpp currently
installed, so first inspect:

``` bash
./whisper.cpp/build/bin/whisper-cli --help
```

Then run a transcription using the project's model and audio file.

This isolates:

``` text
Audio problem
```

from:

``` text
Nova problem
```

------------------------------------------------------------------------

# 16. Ollama / Llama Setup

## 16.1 Verify Ollama

``` bash
ollama --version
```

Check the service:

``` bash
systemctl status ollama
```

If required:

``` bash
sudo systemctl start ollama
```

Enable it at boot:

``` bash
sudo systemctl enable ollama
```

------------------------------------------------------------------------

## 16.2 List models

``` bash
ollama list
```

Check currently loaded/running models:

``` bash
ollama ps
```

------------------------------------------------------------------------

## 16.3 Download a model

Use the model selected for the project:

``` bash
ollama pull <model-name>
```

Then test it:

``` bash
ollama run <model-name>
```

Exit the interactive model session with:

``` text
/bye
```

or the appropriate command supported by the installed Ollama version.

------------------------------------------------------------------------

## 16.4 Remove large unused models

List them first:

``` bash
ollama list
```

Then remove an unnecessary model:

``` bash
ollama rm <model-name>
```

This is useful when several large models are consuming disk space.

------------------------------------------------------------------------

## 16.5 Find Ollama model storage

Ollama manages its own model storage. Do not manually delete individual
model blobs unless you fully understand the storage layout.

Inspect disk usage:

``` bash
du -sh ~/.ollama 2>/dev/null
```

If the installation uses another service user/location, inspect the
service configuration:

``` bash
systemctl cat ollama
```

The safest normal operation is:

``` bash
ollama list
ollama rm <model-name>
```

------------------------------------------------------------------------

# 17. Audio Setup and Diagnostics

Linux audio problems should be diagnosed independently before changing
Nova code.

## 17.1 List recording devices

``` bash
pactl list sources short
```

or:

``` bash
pactl list sources
```

Useful filtered output:

``` bash
pactl list sources | grep -E "Name:|State:|Description:"
```

------------------------------------------------------------------------

## 17.2 Inspect a specific microphone

Example:

``` bash
pactl list sources | grep -A 70 "Name: <source-name>"
```

To inspect active port information:

``` bash
pactl list sources | grep -A 70 "<source-name>" | grep -E "Active Port|analog-input"
```

------------------------------------------------------------------------

## 17.3 Set the default microphone

List sources:

``` bash
pactl list short sources
```

Then:

``` bash
pactl set-default-source <source-name>
```

------------------------------------------------------------------------

## 17.4 Set the default speaker

List sinks:

``` bash
pactl list short sinks
```

Then:

``` bash
pactl set-default-sink <sink-name>
```

------------------------------------------------------------------------

## 17.5 PipeWire systems

Check:

``` bash
wpctl status
```

The output can help identify:

-   Sources.
-   Sinks.
-   Default devices.
-   Audio nodes.

------------------------------------------------------------------------

## 17.6 Test recording

If `arecord` is available:

``` bash
arecord -l
```

A simple recording test:

``` bash
arecord -d 5 test.wav
```

Then inspect/play the file using an available audio player.

If recording works but Whisper fails, the issue is probably in:

``` text
audio format
    or
Whisper configuration
```

rather than the physical microphone.

------------------------------------------------------------------------

# 18. Running Nova

Activate the virtual environment:

``` bash
cd ~/Projects/ps4
source .venv/bin/activate
```

Verify dependencies:

``` bash
python --version
```

Run the project's main entry point.

For example, if the entry point is `nova_agent.py`:

``` bash
python nova_agent.py
```

If the project has another launcher, use that launcher instead.

## Recommended pre-demo startup

Terminal 1:

``` bash
ollama ps
```

Terminal 2:

``` bash
cd ~/Projects/ps4
source .venv/bin/activate
python nova_agent.py
```

Keep the Nova terminal visible during the demonstration so the audience
can see the pipeline.

------------------------------------------------------------------------

# 19. Useful Commands

## Project

``` bash
pwd
ls
ls -lah
find . -maxdepth 2 -type f
```

Search source code:

``` bash
grep -R "MODEL_NAME" -n . --exclude-dir=.git --exclude-dir=.venv
```

Search tool references:

``` bash
grep -R "Tools" -n . --exclude-dir=.git --exclude-dir=.venv
```

------------------------------------------------------------------------

## Python

``` bash
python --version
which python
pip --version
pip list
pip freeze
```

Activate:

``` bash
source .venv/bin/activate
```

Deactivate:

``` bash
deactivate
```

------------------------------------------------------------------------

## Git

``` bash
git status
git add .
git commit -m "Update Nova"
git log --oneline -10
git pull
```

------------------------------------------------------------------------

## Ollama

``` bash
ollama --version
ollama list
ollama ps
ollama run <model-name>
ollama pull <model-name>
ollama rm <model-name>
```

------------------------------------------------------------------------

## Whisper.cpp

``` bash
cd whisper.cpp
cmake -B build
cmake --build build -j$(nproc)
```

Inspect executable help:

``` bash
./build/bin/whisper-cli --help
```

Return:

``` bash
cd ..
```

------------------------------------------------------------------------

## Audio

``` bash
pactl list short sources
pactl list short sinks
pactl get-default-source
pactl get-default-sink
wpctl status
```

Set defaults:

``` bash
pactl set-default-source <source-name>
pactl set-default-sink <sink-name>
```

------------------------------------------------------------------------

## Processes

Find Nova:

``` bash
ps aux | grep -i nova
```

Find Ollama:

``` bash
ps aux | grep -i ollama
```

------------------------------------------------------------------------

## Disk usage

``` bash
df -h
du -sh .
du -sh ~/.ollama 2>/dev/null
```

------------------------------------------------------------------------

# 20. Suggested Project Structure

The exact filenames may evolve, but the architecture should remain close
to:

``` text
ps4/
│
├── .venv/
│
├── models/
│   ├── whisper/
│   └── llama/
│
├── whisper.cpp/
│
├── tools/
│   ├── __init__.py
│   ├── time_tools.py
│   ├── meeting_tools.py
│   ├── document_tools.py
│   └── web_tools.py
│
├── logs/
│
├── data/
│   ├── meetings/
│   └── documents/
│
├── config.py
├── tools.py
├── nova_agent.py
├── requirements.txt
└── README.md
```

The actual project can use a different layout; the important separation
is:

``` text
Configuration
     │
     ├── Input / Audio
     ├── Agent
     ├── Tools
     ├── Models
     ├── Data
     └── Logging
```

------------------------------------------------------------------------

# 21. Request Lifecycle

A normal voice request follows this sequence:

``` mermaid
sequenceDiagram
    participant User
    participant Mic as Microphone
    participant Whisper as Whisper.cpp
    participant Nova as Nova Agent
    participant Tool as Tool Layer
    participant LLM as Ollama/Llama
    participant TTS as Voice Output

    User->>Mic: Speak command
    Mic->>Whisper: Audio
    Whisper->>Nova: Transcribed text
    Nova->>LLM: Interpret request

    alt Tool required
        LLM->>Nova: Select tool
        Nova->>Tool: Execute operation
        Tool-->>Nova: Tool result
        Nova->>LLM: Provide tool result
        LLM-->>Nova: Final response
    else No tool required
        LLM-->>Nova: Final response
    end

    Nova->>TTS: Response text
    TTS-->>User: Spoken response
```

This is the central execution model of the system.

------------------------------------------------------------------------

# 22. Configuration

Configuration should be centralized.

Typical configuration values include:

``` python
WHISPER = "path/to/whisper-cli"
MODEL = "path/to/whisper-model"
MODEL_NAME = "<ollama-model>"
```

Keep paths and model names in configuration rather than duplicating them
throughout the codebase.

A useful configuration pattern is:

``` text
config.py
   │
   ├── Whisper executable
   ├── Whisper model
   ├── Ollama model
   ├── audio settings
   ├── data directories
   └── logging configuration
```

This makes moving the project between machines easier.

------------------------------------------------------------------------

# 23. Troubleshooting

## 23.1 Nova starts but microphone input does not work

Check:

``` bash
pactl list short sources
```

Then:

``` bash
pactl get-default-source
```

Verify the selected source:

``` bash
pactl list sources | grep -A 70 "<source-name>"
```

Test recording independently.

------------------------------------------------------------------------

## 23.2 Whisper is too slow

Possible causes:

-   Whisper model is too large.
-   CPU-only inference.
-   Large audio segments.
-   Too much processing per request.
-   Multiple processes competing for CPU/RAM.

Check:

``` bash
top
```

or:

``` bash
htop
```

Consider using a smaller Whisper model for a live demo.

------------------------------------------------------------------------

## 23.3 LLM responses are too slow

Possible causes:

-   LLM is too large.
-   Model is being loaded repeatedly.
-   Insufficient RAM.
-   CPU inference.
-   Long prompts.
-   Large transcript/document context.

Check:

``` bash
ollama ps
```

and:

``` bash
free -h
```

Avoid loading several large models simultaneously if the machine cannot
handle them efficiently.

------------------------------------------------------------------------

## 23.4 Ollama is not responding

Check:

``` bash
systemctl status ollama
```

Start it if needed:

``` bash
sudo systemctl start ollama
```

Then:

``` bash
ollama list
ollama ps
```

------------------------------------------------------------------------

## 23.5 Model takes too long to generate

For a demonstration:

1.  Use a smaller model.
2.  Keep the prompt concise.
3.  Avoid sending unnecessary transcript/document content.
4.  Keep only the required model loaded.
5.  Test the model independently with:

``` bash
ollama run <model-name>
```

------------------------------------------------------------------------

## 23.6 Date/time answer is wrong

Do not make the LLM guess the current date.

Use the deterministic time tool:

``` text
User
 ↓
Nova
 ↓
get_current_datetime()
 ↓
Actual system datetime
```

Also verify Linux time:

``` bash
date
timedatectl
```

------------------------------------------------------------------------

## 23.7 Tool is not being called

Check:

-   Tool is registered.
-   Tool name matches the agent's tool definition.
-   Tool arguments are correctly described.
-   The system prompt tells the model when the tool should be used.
-   Logs show whether the model attempted a tool call.

Search the source:

``` bash
grep -R "Tools" -n . --exclude-dir=.git --exclude-dir=.venv
```

------------------------------------------------------------------------

## 23.8 Logs are missing

Check that logging is configured before the application starts
generating logs.

A basic configuration:

``` python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
```

Use module-level loggers:

``` python
logger = logging.getLogger(__name__)
```

------------------------------------------------------------------------

## 23.9 Project accidentally runs from the wrong environment

Check:

``` bash
pwd
which python
which pip
```

The Python path should point into:

``` text
.../ps4/.venv/bin/python
```

If not:

``` bash
source .venv/bin/activate
```

------------------------------------------------------------------------

# 24. Demonstration Guide

The current project can be demonstrated **without physical hardware**.

## Demo setup

Show:

``` text
┌──────────────────────────────────────────┐
│              Linux Laptop                │
│                                          │
│  Microphone → Whisper.cpp → Nova         │
│                         │                │
│                         ├→ Llama         │
│                         ├→ Tools         │
│                         ├→ Web           │
│                         └→ Documents     │
│                         │                │
│                         ▼                │
│                  Terminal + Voice        │
└──────────────────────────────────────────┘
```

## Recommended demonstration sequence

### Demo 1 --- Basic voice interaction

Say a simple command and show:

``` text
Wake phrase
   ↓
Transcription
   ↓
LLM
   ↓
Response
```

### Demo 2 --- Deterministic date/time tool

Ask:

``` text
"What is the current date and time?"
```

Show that Nova uses the time tool rather than guessing.

### Demo 3 --- Meeting assistant

Use a meeting transcript and ask:

``` text
"What did we discuss about the project?"
```

or:

``` text
"Search the meeting for the database discussion."
```

Show the transcript-driven answer.

### Demo 4 --- Document summarization

Provide a document and ask:

``` text
"Summarize this document."
```

### Demo 5 --- Web agent

Ask for information that requires current internet data.

Show:

``` text
Command
  ↓
Web agent
  ↓
Retrieved information
  ↓
Nova response
```

### Demo 6 --- Logs

Keep the terminal visible and show the execution pipeline.

This is especially useful when there is no physical LED/hardware system
available.

------------------------------------------------------------------------

# 25. Hardware / LED Extension

The software architecture intentionally leaves room for hardware output.

Future architecture:

``` text
                    Nova
                      │
              ┌───────┴───────┐
              ▼               ▼
        Voice Output       Hardware
                              │
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
                   LED      Buzzer    Display
```

Possible LED states:

``` text
OFF
 │
 ├── Listening
 │
 ├── Processing
 │
 ├── Tool execution
 │
 ├── Speaking
 │
 └── Error
```

Example conceptual state machine:

``` text
IDLE
 │
 ▼
LISTENING
 │
 ▼
PROCESSING
 │
 ├──────────────┐
 ▼              ▼
TOOL_CALL     DIRECT_LLM
 │              │
 └──────┬───────┘
        ▼
     SPEAKING
        │
        ▼
       IDLE
```

No hardware is required to demonstrate these states; the terminal can
represent them during software development.

------------------------------------------------------------------------

# 26. Performance Notes

Local AI has a direct relationship between model size and response
latency.

A simplified relationship is:

``` text
Larger Model
    │
    ├── More RAM
    ├── More compute
    ├── More disk
    └── Usually higher latency
```

For a live demonstration, **response speed is often more important than
maximum model size**.

## Practical optimization order

1.  Use an appropriate model size.
2.  Avoid repeatedly loading models.
3.  Keep prompts focused.
4.  Keep transcript/document context relevant.
5.  Use deterministic tools for simple facts.
6.  Use smaller Whisper models if transcription latency is excessive.
7.  Avoid running multiple large models unnecessarily.

------------------------------------------------------------------------

# 27. Development Practices

## Keep responsibilities separate

Avoid putting everything in `nova_agent.py`.

Prefer:

``` text
nova_agent.py
    │
    ├── agent orchestration
    │
    ├── config.py
    │
    ├── tools.py
    │
    ├── time_tools.py
    │
    ├── meeting_tools.py
    │
    ├── document tools
    │
    └── web tools
```

## Add a tool instead of adding another giant conditional

Prefer:

``` text
Tool Registry
     │
     ├── time
     ├── transcript
     ├── document
     └── web
```

over:

``` python
if command_contains_time:
    ...
elif command_contains_meeting:
    ...
elif command_contains_document:
    ...
```

The tool architecture scales better.

------------------------------------------------------------------------

## Log at meaningful boundaries

Useful boundaries:

``` text
INPUT START
TRANSCRIPTION COMPLETE
AGENT START
TOOL START
TOOL COMPLETE
LLM START
LLM COMPLETE
OUTPUT START
OUTPUT COMPLETE
```

Do not log sensitive document contents or credentials unnecessarily.

------------------------------------------------------------------------

## Test components independently

Before testing the complete system:

``` text
1. Test microphone
2. Test audio capture
3. Test Whisper
4. Test Ollama
5. Test tools
6. Test Nova agent
7. Test TTS
8. Test complete pipeline
```

This dramatically reduces debugging time.

------------------------------------------------------------------------

# 28. Future Roadmap

## Short term

-   Improve response latency.
-   Stabilize model selection.
-   Improve terminal visualization.
-   Add stronger tool error handling.
-   Standardize logging.
-   Add more document formats.
-   Improve meeting transcript retrieval.
-   Add automated tests.

## Medium term

-   Graphical frontend.
-   Conversation history UI.
-   Better document ingestion.
-   Better meeting timeline UI.
-   Tool execution visualization.
-   Hardware/LED controller.
-   More robust web-agent workflows.

## Long term

``` text
                 ┌───────────────────┐
                 │       Nova        │
                 └─────────┬─────────┘
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
     Voice                GUI              Hardware
       │                   │                   │
       ▼                   ▼                   ▼
   Whisper.cpp          Dashboard          LEDs/etc.
       │
       ▼
     Agent
       │
 ┌─────┼────────┬──────────┐
 ▼     ▼        ▼          ▼
LLM   Tools   Documents   Web
```

The core agent/tool architecture should remain the foundation as these
interfaces are added.

------------------------------------------------------------------------

# 29. Quick Start

For a machine where the project is already installed:

``` bash
cd ~/Projects/ps4
source .venv/bin/activate
```

Check Python:

``` bash
python --version
```

Check Ollama:

``` bash
ollama list
ollama ps
```

Check microphone:

``` bash
pactl list short sources
```

Check speaker:

``` bash
pactl list short sinks
```

Check PipeWire if applicable:

``` bash
wpctl status
```

Then start Nova:

``` bash
python nova_agent.py
```

If the project uses another entry point, run that file instead.

------------------------------------------------------------------------

# Final Architecture Summary

The complete current concept is:

``` text
                         ┌──────────────────┐
                         │       USER       │
                         └────────┬─────────┘
                                  │
                              Voice/Text
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Audio / Input    │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   Whisper.cpp    │
                         │ Speech → Text    │
                         └────────┬─────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │       NOVA AGENT         │
                    │   Orchestration Layer    │
                    └────────────┬─────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
       ┌────────────┐    ┌──────────────┐    ┌────────────┐
       │   Ollama   │    │    Tools     │    │ Web Agent  │
       │  + Llama   │    │              │    │            │
       └─────┬──────┘    └──────┬───────┘    └─────┬──────┘
             │                  │                  │
             │          ┌───────┼────────┐         │
             │          ▼       ▼        ▼         │
             │        Time   Meeting  Documents    │
             │                  │                  │
             └──────────────────┼──────────────────┘
                                ▼
                         ┌──────────────┐
                         │ Final Answer │
                         └──────┬───────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
              ┌──────────┐            ┌──────────┐
              │ Terminal │            │   TTS    │
              └──────────┘            └────┬─────┘
                                           │
                                           ▼
                                         USER
```

**Design goal:** keep the intelligence local where practical, keep
deterministic operations in tools, keep current-information tasks in the
web layer, keep meeting/document data grounded in their source material,
and keep the architecture modular enough to add a GUI and hardware
later.
