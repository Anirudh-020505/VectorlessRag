# Vectorless RAG | PageIndex 🚀

A state-of-the-art, autonomous RAG (Retrieval-Augmented Generation) system that operates **without a vector database**. Instead, it builds hierarchical knowledge trees from your documents and uses an intelligent agent to browse them for answers.

![Vectorless RAG Logo](frontend/public/logo.png)

## 🌟 Key Features

### 1. Vectorless Architecture
Traditional RAG relies on vector similarity which can be fuzzy. **Vectorless RAG** uses the LLM to architect your document into a logical tree. This ensures higher precision and maintains the structural context of the information.

### 2. Autonomous ReAct Agent
Powered by a **Reason + Act (ReAct) loop**, the system doesn't just "fetch" snippets; it **explores**.
- **Thoughts**: The agent explains its reasoning before every step.
- **Actions**: It navigates the tree, listing nodes and reading content as needed.
- **Self-Correction**: If a branch is unhelpful, it automatically backtracks to find the right path.

### 3. Visual Reasoning Path
Every answer comes with a clear audit trail. You can see the "Reasoning Steps" the agent took to reach its conclusion, providing full transparency into the AI's logic.

---

## 📁 Project Structure

```text
.
├── backend/            # FastAPI backend & ReAct Agent logic
├── frontend/           # React/Vite dashboard & Chat UI
├── api/                # Subdirectory for serverless deployments
└── package.json        # Root monorepo configuration
```

---

## 🚦 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (or Supabase)
- OpenAI API Key (Custom endpoints supported)

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```
Create a `.env` file in the `backend` folder:
```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/dbname
OPENAI_API_KEY=your_key
OPENAI_BASE_URL=https://your-custom-endpoint/v1
SECRET_KEY=generate_a_random_string
```
Run the server:
```bash
uvicorn app.main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
```
Create a `.env` file in the `frontend` folder:
```env
VITE_API_BASE_URL=http://localhost:8000
```
Run the development server:
```bash
npm run dev
```

---

## ☁️ Deployment

This project is configured for seamless deployment on **Vercel**.
- **Backend**: Use the `api/index.py` entrypoint. Set `maxDuration` to 60s in `vercel.json` for long-running LLM tasks.
- **Frontend**: Standard Vite deployment. Ensure `VITE_API_BASE_URL` points to your production backend.

---

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
