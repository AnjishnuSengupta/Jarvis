<div align="center">

<img src="https://media.giphy.com/media/26tn33aiTi1jIGsD6/giphy.gif" alt="Jarvis Core Engine" width="100%" style="border-radius: 10px; max-width: 800px;" />

# Jarvis NLU

<samp>J.A.R.V.I.S — A From-Scratch Classical Natural Language Understanding Assistant</samp>

<br/>

[![Version](https://img.shields.io/badge/v0.0.1-3b82f6?style=flat-square&label=release)](#)
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

- **Zero Pretrained Weights:** Every part of the pipeline is initialized randomly and trained on synthetic and user-provided data.
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
Bypasses manual labeling by utilizing procedural template generation to bootstrap thousands of initial training samples.

---

## Implemented Features

This project was built iteratively across 12 distinct phases. All core features are now fully functional:

- **Entity Extraction:** A deterministic Sequence/Rule-based system for extracting temporal data, names, and parameters directly from text.
- **Dialogue Manager:** Frame-based slot filling and state tracking to handle multi-turn conversations seamlessly.
- **Automated Codegen Tool:** Deterministically scaffolds full projects (such as Vite/React applications) directly to the filesystem.
- **Google Calendar Integration:** Schedules meetings via the Google Workspace API using OAuth2 authentication.
- **System Control & Automation:** Interfaces directly with Linux subsystems to manage volume and execute core OS-level tasks.
- **Active Learning Pipeline:** A dedicated `review.py` CLI module that allows developers to review low-confidence interactions, manually assign labels, and continuously retrain the network.
- **Vector Memory Core:** An SQLite-backed facts store that leverages TF-IDF Cosine Similarity for robust memory retrieval over historical conversations.
- **Voice I/O Engine:** Fully integrated offline Speech-to-Text (STT) and Text-to-Speech (TTS) capabilities for a hands-free interaction model.
- **Desktop Shell API:** Exposes the core AI logic via a local Flask API and a beautifully crafted Tauri (React) GUI for desktop interactions.

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
   ```

3. **Bootstrap and Train the Model**

   ```bash
   python src/data/synthetic_generator.py
   python src/nlu/train.py
   ```

## Usage

### Option A: Standard CLI Mode
Run Jarvis interactively in your terminal.
```bash
python jarvis.py
```

### Option B: Voice Mode
Run Jarvis with the microphone and speaker enabled for a hands-free experience.
```bash
python jarvis.py --voice
```

### Option C: Desktop Application
Start the background API server, and launch the Tauri React application.
```bash
# Terminal 1: Start Backend
python server.py

# Terminal 2: Start Desktop App
cd ui
npm run tauri dev
```

---

<div align="center">
  <i>Developed and engineered by Anjishnu Sengupta</i>
</div>
