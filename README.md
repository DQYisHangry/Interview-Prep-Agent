# 🎯 Interview Prep Agent

An AI-powered web agent that researches a company's website and generates a personalized interview preparation report — including culture analysis, likely interview questions, STAR story suggestions, and smart questions to ask your interviewer.

Built with **Python + Flask + OpenAI GPT-4o**. The system is only able in Mandarin at this moment.

---

## ✨ Features

-  **Auto-scrapes** the company's website (homepage, About, Culture, Careers, etc.)
-  **Company snapshot** — industry, size, core business, recent highlights
-  **Culture signal analysis** — identifies cultural traits with evidence from the website
-  **Likely interview questions** — tailored to the company, each with a "why they ask this" explanation and answer tips
-  **STAR story themes** — suggests which experiences to prepare based on company culture
-  **Dos & Don'ts** — specific advice for this company's interview style
-  **Questions to ask the interviewer** — shows you've done your research

---

## 🖥️ Demo

<img width="768" height="521" alt="image" src="https://github.com/user-attachments/assets/724d3489-c5d9-4154-8be4-aedafe4dcfe7" />


---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/api-keys)

### Installation

1. **Clone the repo**
   ```bash
   git clone [https://github.com/DQYisHangry/Interview-Prep-Agent.git]
   cd interview-prep-agent
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv

   # macOS / Linux
   source .venv/bin/activate

   # Windows
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API key**

   Copy `.env.example` to `.env` and fill in your key:
   ```bash
   cp .env.example .env
   ```
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

5. **Run the app**
   ```bash
   python app.py
   ```

6. Open your browser and go to `http://localhost:8080`

---

## 📁 Project Structure

```
interview-prep-agent/
├── app.py              # Flask backend + agent logic
├── index.html          # Web UI
├── requirements.txt    # Python dependencies
├── .env.example        # API key template
└── .gitignore          # Keeps secrets out of git
```

---

## Tech Stack

| Layer    | Technology          |
|----------|---------------------|
| Backend  | Python, Flask       |
| AI Model | OpenAI GPT-4o       |
| Scraping | urllib (built-in)   |
| Frontend | HTML, CSS, JS       |

---

## Limitations

- Only scrapes publicly accessible pages (no login-required content)
- Works best with English-language company websites
- Quality of report depends on how much content the company publishes on their website

