<div align="center">

<img src="https://media.giphy.com/media/26tn33aiTi1jIGsD6/giphy.gif" alt="Jarvis Banner" width="100%" style="border-radius: 10px;" />

# Jarvis NLU

<samp>J.A.R.V.I.S — A From-Scratch Classical Natural Language Understanding Assistant</samp>

<br/>

[![Version](https://img.shields.io/badge/v0.0.0-3b82f6?style=flat-square&label=release)](#)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)](#)
[![NumPy](https://img.shields.io/badge/NumPy-Power-4d77cf?style=flat-square&logo=numpy&logoColor=white)](#)
[![License](https://img.shields.io/badge/MIT-3b82f6?style=flat-square&label=license)](LICENSE)
[![Creator](https://img.shields.io/badge/AnjishnuSengupta-E4405F?style=flat-square&logo=github&logoColor=white)](https://github.com/AnjishnuSengupta)

<br/>

<kbd>[**Get Started**](#setup)</kbd>&nbsp;&nbsp;
<kbd>[**How it Works**](#architecture-highlights)</kbd>&nbsp;&nbsp;
<kbd>[**Future Plan**](#future-plan)</kbd>

<br/>

</div>

---

<br/>

Jarvis is a from-scratch classical Natural Language Understanding (NLU) assistant. **It uses NO pre-trained LLM models.** Everything is built from scratch using NumPy.

This project focuses on bounding the assistant to task-oriented commands rather than general open-ended conversations. By building the Tokenizer, TF-IDF Vectorizer, and Neural Network manually, we achieve rock-solid reliability on defined tasks like scheduling, code generation, and system control.

## Features

- **Zero Pretrained Weights:** Every part of the pipeline is initialized randomly and trained on synthetic/custom data.
- **Lightweight & Fast:** Runs purely on CPU via NumPy matrix math. No heavy GPU requirements.
- **Task-Oriented:** Highly reliable for specific intents compared to prompt-drifting LLMs.

---

## Architecture Highlights

### 1. Tokenizer

Custom implementation that lowercases text, strips punctuation using regex, and splits tokens. It builds a vocabulary dynamically and handles out-of-vocabulary words with an `<UNK>` token.

### 2. TF-IDF Vectorizer

Hand-rolled TF-IDF implementation:

- `tf(t, d) = count(t in d) / len(d)`
- `idf(t) = log(N / (1 + df(t)))`

### 3. Intent Classifier (Neural Network)

A fully custom 2-layer Neural Network (`input -> hidden (128, ReLU) -> output (num_intents, softmax)`) built with NumPy.

- **Forward Pass:** Explicit matrix multiplications.
- **Loss:** Categorical Cross-Entropy.
- **Backward Pass:** Manually derived gradients (no autograd used!).
- **Optimizer:** Mini-batch SGD with momentum.

### 4. Synthetic Data Generation

Uses template generators to bootstrap initial synthetic training data, bypassing the need for manual labeling of hundreds of examples.

---

## Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/AnjishnuSengupta/Jarvis.git
   cd Jarvis
   ```

2. **Create a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Generate Data & Train**
   ```bash
   python src/data/synthetic_generator.py
   python src/nlu/train.py
   ```

---

## Future Plan

We have an extensive roadmap to turn this from a classification engine into a full-fledged local assistant:

- **Phase 4: Entity Extraction:** Build a rule-based system (upgrading to a Sequence Tagger/CRF later) for extracting dates, names, and parameters from text.
- **Phase 5: Dialogue Manager:** Implement frame-based slot filling and state tracking to handle multi-turn conversations and clarifying questions.
- **Phase 6: Codegen Tool:** Scaffold full projects (like Vite/React) deterministically.
- **Phase 7: Google Calendar Integration:** Schedule real meetings via the Calendar API.
- **Phase 8: System Control:** Cross-platform (Windows/Linux) Bluetooth and volume controls.
- **Phase 9: Active Learning Loop:** A CLI tool to review low-confidence interactions, correct them, and continually retrain the network.
- **Phase 10: Vector Memory:** SQLite facts store with TF-IDF retrieval over past conversations.
- **Phase 11: Voice I/O Layer:** Offline STT (Speech-to-Text) and TTS (Text-to-Speech) for hands-free interactions.
- **Phase 12: Desktop Shell:** Package into a standalone Tauri desktop app.

---

<div align="center">
  <i>Built with ❤️ by Anjishnu Sengupta</i>
</div>
