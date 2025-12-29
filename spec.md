# Project Specification: AI Trend & Content Factory Agent (Production Ready)

## 1. Project Overview
A fully automated "Content Strategist" system that runs daily on GitHub Actions.
* **Trigger:** Daily cron job (08:00 UTC).
* **Input:** YouTube Data API v3 (Trends) + YouTube Transcript API (Content).
* **Processing:** OpenAI GPT-4o (Analysis).
* **Output:** A JSON file (`data/daily_brief.json`) committed back to the repo.
* **Display:** A Streamlit public dashboard reading that JSON file.

## 2. Directory Structure (Strict)
The agent must generate this EXACT structure to ensure Streamlit Cloud compatibility:

```text
trend-agent/
│
├── .github/
│   └── workflows/
│       └── daily_run.yml   # The Automation Logic
│
├── src/                    # Source Code Module
│   ├── __init__.py
│   ├── scouts/
│   │   ├── __init__.py
│   │   ├── youtube_scout.py
│   │   └── transcript_scout.py
│   └── brain/
│       ├── __init__.py
│       └── agent.py
│
├── data/
│   └── daily_brief.json    # The "Database" (Auto-generated)
│
├── main.py                 # The Entry Point
├── app.py                  # The Dashboard (Must be at root for Streamlit)
├── requirements.txt
└── spec.md