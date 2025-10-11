# FRisk_proyect
Data Engineer to automate with AI agents evalutations of the alerts. This include an AI-powered agent that collects and analyzes global news related to money laundering, terrorist financing, and corruption, and outputs structured JSON data.


# AI News Intelligence Agent

This project is an **AI-powered agent** that automatically collects and analyzes global news related to **money laundering**, **terrorist financing**, and **corruption**.

It extracts key entities (people, countries, crimes, and dates) and stores the information in a structured **JSON** format.

---

## Features
- Collects news from multiple sources using `gnews`
- Uses **spaCy** for entity extraction (names, locations, dates)
- Generates structured JSON datasets
- Simple modular design, ready for automation

---

## Installation

```bash
git clone https://github.com/<your-username>/ai-news-intelligence-agent.git
cd ai-news-intelligence-agent
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
