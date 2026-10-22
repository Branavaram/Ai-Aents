# 🤖 AI Dev Office — Cyberpunk Edition

A multi-agent AI code review system with a **cyberpunk-themed React UI** and **FastAPI backend**. Watch 5 AI teammates (each with their own personality + domain knowledge) collaborate on your code in real-time.

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Backend](https://img.shields.io/badge/backend-FastAPI-009688)
![Frontend](https://img.shields.io/badge/frontend-Next.js%2015-black)
![Animation](https://img.shields.io/badge/motion-Framer-ff0080)

---

## 🏗️ Architecture

```
┌─────────────────────────────┐           ┌──────────────────────┐
│   FRONTEND (Next.js 15)     │ ◄──WS────►│   BACKEND (FastAPI)  │
│   TailwindCSS + Framer      │           │   CrewAI agents      │
│   TypeScript                │           │   Groq LLM           │
└─────────────────────────────┘           └──────────────────────┘
   Cyberpunk neon office                      Live agent streaming
```

---

## 🚀 Quick Start

### 1. Backend (Python)
```bash
cd backend
pip install -r ../requirements.txt
pip install fastapi "uvicorn[standard]"
# Make sure .env has GROQ_API_KEY=...
uvicorn api:app --reload --port 8000
```

### 2. Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000** 🎉

---

## 👥 Meet The Team

| Avatar | Agent | Role | Reads |
|---|---|---|---|
| 🧑‍💼 | Alex | Engineering Lead | All domains |
| 👩‍💻 | Priya | Senior Developer | PEP 8, Clean Code, Anti-patterns |
| 👨‍💻 | Jake | Junior Developer | Fresh-eyes + common confusions |
| 🛡️ | Sam | Security Engineer | OWASP Top 10, Bandit rules |
| 📚 | Luna | Technical Writer | PEP 257, Google style |

Each agent **cites real industry standards** (OWASP A03, Bandit B608, PEP 8) when flagging issues.

---

## 🎯 Review Modes

- 🔍 **Full Review** — all 5 agents
- 🐛 **Bugs Only** — Priya + Jake fast scan
- 🔒 **Security Only** — Sam goes deep
- 💡 **Explain Code** — Luna walks you through it

---

## 📁 Project Structure

```
Code crew Agent/
├── backend/              ← Python FastAPI + CrewAI
│   ├── api.py            ← Main API server
│   ├── app.py            ← (Legacy Streamlit UI)
│   ├── team.py           ← Agent personalities
│   ├── knowledge_loader.py
│   └── vault/            ← Knowledge base + past reviews
│       ├── knowledge/
│       │   ├── dev/
│       │   ├── security/
│       │   └── writing/
│       └── reviews/
├── frontend/             ← Next.js React app
│   ├── app/
│   │   ├── page.tsx
│   │   ├── layout.tsx
│   │   ├── globals.css
│   │   ├── components/
│   │   │   ├── OfficeFloor.tsx
│   │   │   ├── AgentCard.tsx
│   │   │   └── ChatPanel.tsx
│   │   └── lib/
│   │       └── api.ts
│   └── package.json
└── README.md
```

---

## 🛠️ Tech Stack

**Backend**
- FastAPI (REST + WebSockets)
- CrewAI (multi-agent orchestration)
- Groq (free fast LLM hosting)
- LiteLLM (unified LLM interface)

**Frontend**
- Next.js 15 (App Router)
- TypeScript
- TailwindCSS v4
- Framer Motion (animations)
- Lucide (icons)
- react-markdown

---

## 🎨 Theme: Cyberpunk Neon

- 🌃 Dark `#050510` base
- 💠 Neon cyan `#00f0ff` accents
- 💗 Pink `#ff00e0` highlights
- 💜 Purple `#a855f7` for the shared brain
- 💚 Green `#00ff9f` for success
- Scanlines overlay + glowing text

---

## 📜 License

MIT

---

Built with ❤️ while learning AI engineering.
