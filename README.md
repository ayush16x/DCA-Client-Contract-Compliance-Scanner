# ⚖️ Dynamic Clause Analyzer (DCA)

## ✨ About This Project

The **Dynamic Clause Analyzer (DCA)** is a cutting-edge compliance tool designed to rapidly scan legal contracts (PDFs) and flag deviations from a pre-defined set of internal company rules (the **Playbook**).

This project uses a robust **Client–Server Architecture** to separate the user interface from the heavy computation:

- **Backend (FastAPI):** Hosts the core analysis logic, including the RAG pipeline and LLM calls.  
- **Frontend (Streamlit):** Provides a simple, interactive UI for uploading files and displaying structured results.

The system uses **Retrieval-Augmented Generation (RAG)** to ensure accuracy: the analyzer retrieves the single most relevant policy from the Vector Store before evaluating a contract clause.

---

## 🚀 Key Benefits

| Benefit | Description |
|--------|-------------|
| 🔍 **Automated Compliance** | Instantly identifies non-compliant contract language, saving countless hours of manual review. |
| 💡 **Actionable Redlines** | Provides a summary of risk *and* suggested replacement text to bring clauses into compliance. |
| 🛡️ **Architectural Scalability** | Streamlit client and FastAPI server can scale, test, and deploy independently. |
| 🎯 **Focused Analysis (RAG)** | Compares each contract clause only to the *most relevant* internal standard to minimize hallucinations. |

---

## ⚙️ How to Run the Project (Local Setup)

### 1. Prerequisites

- Python **3.10+**
- An **OpenAI API Key** with active billing  
  (the project uses `gpt-4o-mini` for analysis and embeddings)

---

### 2. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/dca_prototype.git
cd dca_prototype
