#!/bin/bash
echo "=== Jarvis Setup ==="
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Downloading offline voice model..."
python3 scripts/download_vosk_model.py

echo "Setup complete! You can now run 'python jarvis.py' (or with --voice)"
