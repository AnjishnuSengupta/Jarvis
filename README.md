<div align="center">

<img src="https://media.giphy.com/media/26tn33aiTi1jIGsD6/giphy.gif" alt="Jarvis Core Engine" width="100%" style="border-radius: 10px; max-width: 800px;" />

# Jarvis NLU

<samp>J.A.R.V.I.S — A From-Scratch Classical Natural Language Understanding Assistant</samp>

<br/>

[![Version](https://img.shields.io/badge/v0.0.2-3b82f6?style=flat-square&label=release)](#)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)](#)
[![NumPy](https://img.shields.io/badge/NumPy-Power-4d77cf?style=flat-square&logo=numpy&logoColor=white)](#)
[![License](https://img.shields.io/badge/MIT-3b82f6?style=flat-square&label=license)](LICENSE)
[![Creator](https://img.shields.io/badge/AnjishnuSengupta-E4405F?style=flat-square&logo=github&logoColor=white)](https://github.com/AnjishnuSengupta)

<br/>

<kbd>[**Get Started**](#setup)</kbd>&nbsp;&nbsp;
<kbd>[**How it Works**](#architecture-highlights)</kbd>&nbsp;&nbsp;
<kbd>[**Implemented Features**](#implemented-features)</kbd>

<br/>

</div>

---

<br/>

Jarvis is a from-scratch classical Natural Language Understanding (NLU) assistant. **It uses NO pre-trained LLM models.** Everything is built from the ground up using NumPy.

This project focuses on bounding the assistant to task-oriented commands rather than general open-ended conversations. By building the Tokenizer, TF-IDF Vectorizer, and Neural Network manually, we achieve rock-solid reliability on defined tasks like scheduling, code generation, and system control.

## Design Philosophy

- **Zero Pretrained Weights (NLU):** Every part of the NLU intent pipeline is initialized randomly and trained on synthetic and user-provided data. (The offline Vosk STT engine uses a small acoustic model, which is the only exception).
- **Lightweight & Fast:** Runs purely on the CPU via NumPy matrix operations. No GPU required.
- **Task-Oriented Reliability:** Highly reliable for specific intents compared to prompt-drifting LLMs.
- **Continuous Learning Loop:** Jarvis learns from user corrections and actively updates its own neural network.

---

## Architecture Highlights

### 1. Custom Tokenizer
A highly optimized tokenizer that lowercases text, strips punctuation, and builds a vocabulary dynamically. Handles out-of-vocabulary words flawlessly via an `<UNK>` fallback mechanism.

### 2. Hand-rolled TF-IDF Vectorizer
Vectorization implemented via core mathematical principles:
- `tf(t, d) = count(t in d) / len(d)`
- `idf(t) = log(N / (1 + df(t)))`

### 3. Neural Network Intent Classifier
A custom 2-layer Neural Network (`input -> hidden (128, ReLU) -> output (num_intents, softmax)`) built with standard NumPy arrays.
- **Forward Pass:** Explicit matrix multiplications.
- **Loss Calculation:** Categorical Cross-Entropy.
- **Backward Pass:** Manually derived gradients (no autograd dependencies).
- **Optimizer:** Mini-batch SGD with momentum.

### 4. Synthetic Data Bootstrapping
Bypasses manual labeling by utilizing procedural template generation to bootstrap thousands of initial training samples. The dataset is injected with real-world noise (typos, dropped punctuation) and complex compound sentence structures.

---

## Implemented Features

This project was built iteratively across 17 distinct phases. All core features are now fully functional:

- **Desktop GUI (Tauri):** A beautifully crafted Tauri (React) desktop app that communicates with a local Flask backend. Features real-time typing indicators and sliding toast notifications.
- **Automated Codegen & Background Servers:** Deterministically scaffolds full projects (such as Vite React Landing Pages, Todo Apps, Express APIs, and Python Scripts). It automatically stitches React components together based on keyword matching and seamlessly spins up background `npm run dev` servers to provide a clickable `localhost` URL instantly.
- **Proactive Scheduling:** Runs a daemon background thread that actively queries Google Calendar and the internal SQLite logs. The UI actively polls this backend to slide in real-time alert toasts for upcoming meetings and training requests.
- **Active Learning Pipeline:** A dedicated `review.py` CLI module that allows developers to review low-confidence interactions, manually assign labels, and continuously retrain the network across all trained intents dynamically.
- **Entity Extraction:** A deterministic Sequence/Rule-based system for extracting temporal data, names, and parameters directly from text, now with local timezone awareness and fallback parsing for edge cases.
- **Dialogue Manager:** Frame-based slot filling and state tracking to handle multi-turn conversations seamlessly, including multi-turn confirmations for destructive actions and cancellation states.
- **Google Calendar Integration:** Schedules meetings via the Google Workspace API using OAuth2 authentication and accurate ISO-8601 parsing.
- **System Control & Automation:** True cross-platform (Windows & Linux) system control for volume, screen locking, sleep, and brightness via native OS APIs (pycaw, loginctl, etc.).
- **Sandboxed File Operations:** Real filesystem operations (create, delete, move, read, find) safely bounded to a secure `~/jarvis-sandbox` root directory.
- **Bluetooth Discovery:** Discovers and pairs to actual Bluetooth devices dynamically using `bluetoothctl` on Linux.
- **Vector Memory Core:** An SQLite-backed facts store that leverages TF-IDF Cosine Similarity for robust memory retrieval over historical conversations.
- **Voice I/O Engine:** Fully integrated offline Speech-to-Text (STT) via Vosk and Text-to-Speech (TTS) capabilities for a secure, hands-free interaction model without relying on external cloud APIs.

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

### Option A: Desktop Application (Recommended)
Start the background API server, and launch the Tauri React application.
```bash
# Terminal 1: Start Backend
python server.py

# Terminal 2: Start Desktop App
cd ui
npm run tauri dev
```

### Option B: Standard CLI Mode
Run Jarvis interactively in your terminal.
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

1. **Wait for a Notification:** If you are using the desktop app, the proactive scheduler will eventually slide a toast notification onto your screen saying "Alert: X interactions need your review!".
2. **Run the Review Tool:** In your terminal, run `python review.py`.
3. **Correct the Assistant:** The tool will present the failed interaction and ask you to type the correct intent name.
4. **Retrain:** Once you've reviewed the backlog, the tool will automatically kick off `src/nlu/train.py` to bake your new corrections into the neural network weights!

By repeatedly interacting with Jarvis and correcting its mistakes, it will naturally align itself perfectly to your unique conversational cadence.

---

<div align="center">
  <i>Developed and engineered by Anjishnu Sengupta</i>
</div>
