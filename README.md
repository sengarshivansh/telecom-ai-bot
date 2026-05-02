<<<<<<< HEAD
# telecom-ai-bot
Multilingual Conversational AI for Indian Telecom Ecosystems
=======
# Multilingual Conversational AI for Indian Telecom Ecosystems

An AI-powered voice and chat assistant that understands and responds 
in multiple Indian languages (English, Hindi, Kannada, Tamil, Telugu).

## Features
- Speech to text using Whisper
- Multilingual intent detection using mBERT
- Supports 5 Indian languages
- Telecom-specific: recharge, balance, complaints, plans
- FastAPI backend + React frontend

## Tech Stack
- Python, FastAPI, HuggingFace Transformers
- Whisper (STT), gTTS (TTS)
- React (Frontend)
- bert-base-multilingual-cased

## Setup
```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

## Dataset
- 330 samples across 8 intents and 5 languages
- Intents: recharge, balance, network_issue, plan_info, 
  data_usage, complaint, port_number, unknown
>>>>>>> d3f5cc6 (Initial commit - dataset and project structure added)
