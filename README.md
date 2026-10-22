# 🤖 AI Code Review Crew

A multi-agent AI system that reviews your code — bugs, security vulnerabilities, and best practices — using 3 specialist agents that collaborate.

Built with **CrewAI**, **Groq** (free LLM hosting), and **Streamlit** for a slick web UI. Features a persistent **vault** that learns your coding style over time.

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Features

- 🔍 **3 specialist agents** — Reviewer (bugs), Security (OWASP), Summarizer (PR comment)
- 🎯 **4 review modes** — Full / Bugs Only / Security Only / Explain Code
- 🧠 **Shared memory vault** — agents remember your style, past reviews, pet peeves
- 📜 **Review history** — click any past review to re-open
- ⚡ **Live metrics** — tokens, cost, speed per session
- 🆓 **Free to run** — uses Groq's free tier (no OpenAI/Anthropic bill)
- 🎨 **Clean web UI** — built with Streamlit

---

## 🚀 Quick Start

### 1. Clone + install
```bash
git clone https://github.com/YOUR-USERNAME/code-review-crew.git
cd code-review-crew
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

### 2. Get a free Groq API key
Sign up at [console.groq.com](https://console.groq.com) → API Keys → create one.

### 3. Add it to `.env`
Create a `.env` file in the project root:
```
GROQ_API_KEY=gsk_your_key_here
```

### 4. Run the app
```bash
streamlit run app.py
```

Opens in your browser at `http://localhost:8501`.

---

## 🧠 How The Vault Works

The `vault/` folder is your crew's shared brain. Edit these files to teach the agents YOUR preferences:

```
vault/
├── profile/
│   ├── coding_style.md     ← How you write code
│   └── pet_peeves.md       ← What NOT to suggest
├── knowledge/
│   └── security_patterns.md ← OWASP reference
├── projects/               ← Add per-project notes
└── reviews/                ← Auto-saved past reviews
```

Every review the crew does gets saved to `vault/reviews/` so it doesn't repeat itself.

---

## 🛠️ Tech Stack

- **[CrewAI](https://crewai.com)** — Multi-agent orchestration
- **[Groq](https://groq.com)** — Fast, free LLM hosting (GPT-OSS 120B)
- **[Streamlit](https://streamlit.io)** — Web UI
- **[LiteLLM](https://litellm.ai)** — Unified LLM interface

---

## 📸 Screenshots

_Add screenshots after cloning + running._

---

## 🎯 Roadmap

- [x] Core 3-agent crew
- [x] Shared memory vault
- [x] Review history
- [x] Live metrics
- [x] Multiple review modes
- [ ] Agent-to-agent chat panel
- [ ] Learning loop (self-improving prompts)
- [ ] Vector search over vault (RAG)
- [ ] Multiple crews (Code Review, Docs, Tests)
- [ ] Visual "office floor" with moving agents
- [ ] VS Code extension

---

## 📜 License

MIT — do whatever you want with it.

---

Built while learning AI engineering. 🚀
