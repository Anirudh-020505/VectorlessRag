# Vectorless RAG | PageIndex

A high-performance, autonomous RAG (Retrieval-Augmented Generation) system that uses hierarchical knowledge trees instead of traditional vector databases.

## 🚀 Features

- **Vectorless Architecture**: Uses LLM-driven hierarchical indexing for precise context retrieval.
- **Autonomous Agent**: Features a ReAct (Reason + Act) loop that browses the knowledge tree to find answers.
- **Visual Reasoning**: See the agent's internal monologue and reasoning path for every answer.
- **Privacy First**: Local file parsing and selective context injection.

## 🛠️ Tech Stack

- **Frontend**: React, Vite, Tailwind CSS, Framer Motion.
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL.
- **LLM**: OpenAI GPT models (custom endpoint support).

## 🚦 Getting Started

### Local Development

1. **Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 📄 License

MIT License
