<div align="center">

<img src="https://media.giphy.com/media/26tn33aiTi1jIGsD6/giphy.gif" alt="Jarvis Core Engine" width="100%" style="border-radius: 10px; max-width: 800px;" />

# Jarvis NLU & 3D HUD

<samp>J.A.R.V.I.S — A From-Scratch Classical NLU Assistant with an Electron-powered Holographic HUD</samp>

<br/>

[![Version](https://img.shields.io/badge/v1.0.0-3b82f6?style=flat-square&label=release)](#)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)](#)
[![NumPy](https://img.shields.io/badge/NumPy-Power-4d77cf?style=flat-square&logo=numpy&logoColor=white)](#)
[![Electron](https://img.shields.io/badge/Electron-HUD-47848F?style=flat-square&logo=electron&logoColor=white)](#)
[![License](https://img.shields.io/badge/MIT-3b82f6?style=flat-square&label=license)](LICENSE)
[![Creator](https://img.shields.io/badge/AnjishnuSengupta-E4405F?style=flat-square&logo=github&logoColor=white)](https://github.com/AnjishnuSengupta)

<br/>

<kbd>[**Get Started**](#setup)</kbd>&nbsp;&nbsp;
<kbd>[**How it Works**](#architecture-highlights)</kbd>&nbsp;&nbsp;
<kbd>[**Capabilities**](#capabilities)</kbd>

<br/>

</div>

---

<br/>

Jarvis is a from-scratch classical Natural Language Understanding (NLU) assistant. **It uses NO pre-trained LLM models.** Everything is built from the ground up using NumPy.

This project focuses on bounding the assistant to task-oriented commands rather than general open-ended conversations. By building the Tokenizer, TF-IDF Vectorizer, and Neural Network manually, we achieve rock-solid reliability on defined tasks like scheduling, code generation, system control, and code retrieval.

## Design Philosophy

- **Zero Pretrained Weights (NLU):** Every part of the NLU intent pipeline is initialized randomly and trained on synthetic and user-provided data. (The offline Vosk STT engine uses a small acoustic model, which is the only exception).
- **Lightweight & Fast:** Runs purely on the CPU via NumPy matrix operations. No GPU required.
- **Task-Oriented Reliability:** Highly reliable for specific intents compared to prompt-drifting LLMs.
- **Continuous Learning Loop:** Jarvis learns from user corrections and actively updates its own neural network.

---

## Architecture Highlights

### 1. The Holographic 3D HUD (Electron + React Three Fiber)
Jarvis is hosted inside a transparent, frameless **Electron** window. The user interface uses **React Three Fiber (WebGL)** to render a 3D Arc Reactor core, orbiting rings, and a particle field. The UI connects to the Python backend via **Flask-SocketIO** to receive real-time state events (`idle`, `thinking`, `speaking`), altering the color and animation speeds of the 3D meshes dynamically!

### 2. Autonomous Background Code Indexer
Jarvis runs a `watchdog` daemon thread that silently monitors your `~/Documents` directory. It uses Python's `ast` module and Regex to automatically chunk `.py`, `.js`, and `.ts` files into distinct functions and classes. It even reads your `import` statements and hits the PyPI/NPM JSON APIs to grab package descriptions, enriching the metadata. These snippets are saved into an SQLite database. 

### 3. Hand-rolled TF-IDF Code Retrieval
When you ask Jarvis to "look up how I debounced a function", it uses a custom **TF-IDF Vectorizer** and **Cosine Similarity** to instantly query the SQLite `code_snippets` database, returning the exact function you wrote weeks ago, rendered in the terminal or UI.

### 4. Custom Tokenizer & Neural Network
A highly optimized tokenizer lowercases text, strips punctuation, and builds a dynamic vocabulary. The Neural Network Intent Classifier is a custom 2-layer NN built purely with NumPy arrays (Forward pass, categorical cross-entropy loss, backward pass, and SGD optimizer).

---

## Capabilities

Jarvis has been iteratively built to perform the following out-of-the-box:

- **Holographic UI:** A stunning 3D WebGL UI that visualizes Jarvis's internal state.
- **Autonomous Background Code Indexer:** A fast, recursive directory scanner that dynamically monitors your entire local filesystem, parses AST and Regex block chunks (Python, JS, TS, Dart), and fetches external metadata from PyPI and NPM.
- **Rule-Based Code Suggestions:** A deterministic, classical heuristic engine that can analyze your own codebase and automatically propose clean-code refactoring changes (e.g. typing, error handling, strict equality) WITHOUT relying on any LLMs or internet APIs.
- **Code Retrieval Engine:** Instantly search your local codebase via natural language using TF-IDF cosine similarity.
- **Automated Codegen & Background Servers:** Deterministically scaffolds full projects (such as Vite React Landing Pages, Todo Apps, Express APIs, and Python Scripts). It automatically stitches React components together and seamlessly spins up background `npm run dev` servers to provide a clickable `localhost` URL instantly.
- **Proactive Scheduling:** Runs a daemon background thread that actively queries Google Calendar. The UI actively polls this backend to slide in real-time alert toasts for upcoming meetings.
- **Active Learning Pipeline:** A dedicated `review.py` CLI module that allows developers to review low-confidence interactions, manually assign labels, and continuously retrain the network.
- **Entity Extraction:** A deterministic Sequence/Rule-based system for extracting temporal data, names, and parameters directly from text with local timezone awareness.
- **Dialogue Manager:** Frame-based slot filling and state tracking to handle multi-turn conversations seamlessly, including multi-turn confirmations for destructive file actions.
- **Google Calendar Integration:** Schedules meetings via the Google Workspace API using OAuth2 authentication.
- **System Control & Automation:** True cross-platform system control for volume, screen locking, sleep, and brightness via native OS APIs.
- **Sandboxed File Operations:** Real filesystem operations (create, delete, move, read, find) safely bounded to a secure `~/jarvis-sandbox` root directory.
- **Bluetooth Discovery:** Discovers and pairs to Bluetooth devices dynamically using `bluetoothctl` on Linux.
- **Voice I/O Engine:** Fully integrated offline Speech-to-Text (STT) via Vosk and Text-to-Speech (TTS) capabilities.

---

## Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/AnjishnuSengupta/Jarvis.git
   cd Jarvis
   ```

2. **Initialize Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   bash setup.sh
   ```

3. **Install Frontend Dependencies**

   ```bash
   cd ui
   npm install
   cd ..
   ```

4. **Bootstrap and Train the Model**

   ```bash
   python src/data/synthetic_generator.py
   python src/nlu/train.py
   ```

## Usage

### Option A: Holographic Desktop Application (Recommended)
Start the Electron desktop app. It will automatically spawn the Flask backend for you!
```bash
cd ui
npm run dev
```

### Option B: Rich CLI Mode
Run Jarvis interactively in your terminal with beautiful syntax highlighting and spinners.
```bash
python jarvis.py
```

### Option C: Voice Mode
Run Jarvis with the microphone and speaker enabled for a hands-free experience.
```bash
python jarvis.py --voice
```

---

## Continuous Learning & Training

Jarvis is designed to be trained by the user over time. If Jarvis doesn't understand a request or predicts the wrong intent with low confidence, it logs that interaction into an internal SQLite database (`data/jarvis.db`) and flags it for review.

1. **Wait for a Notification:** The proactive scheduler will eventually slide a toast notification onto your screen saying "Alert: X interactions need your review!".
2. **Run the Review Tool:** In your terminal, run `python review.py`.
3. **Correct the Assistant:** The tool will present the failed interaction and ask you to type the correct intent name.
4. **Retrain:** Once you've reviewed the backlog, the tool will automatically kick off `src/nlu/train.py` to bake your new corrections into the neural network weights!

By repeatedly interacting with Jarvis and correcting its mistakes, it will naturally align itself perfectly to your unique conversational cadence.

---

<div align="center">
  <i>Developed and engineered by Anjishnu Sengupta</i>
</div>
