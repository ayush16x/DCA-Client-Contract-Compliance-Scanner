# ⚖️ Dynamic Clause Analyzer (DCA)

## ✨ About This Project

The **Dynamic Clause Analyzer (DCA)** is an advanced compliance tool designed to rapidly scan legal contracts (uploaded as PDFs) and flag deviations from internal company policies (the **Playbook**).

The system uses a modern **Client–Server Architecture** to separate the interface from the analysis engine:

- **Backend (FastAPI):** Hosts the core analysis logic, RAG pipeline, vector retrieval, and LLM calls.  
- **Frontend (Streamlit):** A simple, interactive UI for file upload and reading results.

Using **Retrieval-Augmented Generation (RAG)**, the model only analyzes each clause against the *single most relevant* policy from the Playbook, ensuring precise and reliable outputs.

---

## 🚀 Key Benefits

| Benefit | Description |
|--------|-------------|
| 🔍 **Automated Compliance** | Instantly identifies risky or non-compliant contract language. |
| 💡 **Actionable Redlines** | Provides exact replacement text suggestions for compliance. |
| 🛡️ **Architectural Scalability** | Backend and frontend scale independently. |
| 🎯 **Focused Analysis (RAG)** | Minimizes hallucinations by comparing clauses only to the most relevant policy. |

---

## 💻 Tech Stack

This project is built using a modern Python-based stack optimized for LLM applications.

| Category | Technology | Purpose in Project |
|---------|------------|--------------------|
| **Backend API** | FastAPI | High-performance async API serving the RAG pipeline. |
| **Frontend / Client** | Streamlit | Web-based interface for uploading files and displaying results. |
| **LLM & Embeddings** | OpenAI (gpt-4o-mini) | Intelligence for clause scoring, risk detection, and redline generation. |
| **RAG Framework** | LangChain | Manages retrieval, prompt templates, and structured output parsing. |
| **Vector Store** | ChromaDB | In-memory vector database storing the company's internal Playbook. |
| **Data Validation** | Pydantic | Ensures consistent JSON-structured output from LLM responses. |

---

## ⚙️ How to Run the Project (Local Setup)

### 1. Prerequisites

- Python **3.10+**
- An **OpenAI API Key** with active billing  
  (uses `gpt-4o-mini` for analysis and embeddings)

---

### 2. Clone the Repository

```bash
git clone https://github.com/ayush16x/DCA-Client-Contract-Compliance-Scanner.git
cd dca_prototype

# Create environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate
B. Install Dependencies
pip install -r requirements.txt

C. Configure API Key (.env file)

Create a .env file:

# .env
OPENAI_API_KEY="sk-YOUR_SECRET_API_KEY_HERE"


.env is git-ignored to protect your API key.

3. Run Both Servers (Backend + Frontend)

Because this is a client–server system, start both components in separate terminals.

🖥️ Terminal 1 — Start Backend (FastAPI)
uvicorn api_server:app --reload


Backend will start at:
http://127.0.0.1:8000

🌐 Terminal 2 — Start Frontend (Streamlit)
streamlit run app.py


Streamlit will open at:
http://localhost:8501

#4. Usage

Open the Streamlit web interface.

Upload a PDF contract or use the sample text.

Click “Start Compliance Scan (Call API)”.

Streamlit sends your data to the FastAPI backend.

Backend performs:

Vector retrieval from Chroma

Clause-to-policy matching

LLM compliance analysis

Risk classification

Suggested redline generation

Results appear in a clean, structured table.
