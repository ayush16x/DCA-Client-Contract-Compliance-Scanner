import os
from dotenv import load_dotenv
from typing import List, Optional

# FastAPI/Pydantic Imports
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# LangChain/RAG Imports (All the heavy lifting dependencies)
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# --- Initialization and Configuration ---

# Load Environment Variables (API Key)
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    # Raise a runtime error if the API key is missing
    raise ValueError("OPENAI_API_KEY not found. Please set it in your .env file.")

# FastAPI App Instance
app = FastAPI(
    title="DCA Analysis API",
    description="API for contract compliance analysis using LLM and RAG."
)

# --- Pydantic Schema Definitions ---
# These models are used both by the LLM (for structured output) and by FastAPI (for API documentation and validation)
class ClauseAnalysis(BaseModel):
    """A single analysis of a contract clause compared against internal policy."""
    clause_title: str = Field(description="The main title or subject of the clause (e.g., 'Limitation of Liability').")
    contract_snippet: str = Field(description="A concise snippet (max 30 words) of the problematic wording from the contract.")
    internal_standard: str = Field(description="The matching internal standard or rule from the company playbook.")
    risk_level: str = Field(description="The assessed risk level: 'High', 'Medium', or 'Low'.")
    discrepancy_summary: str = Field(description="A brief explanation of how the contract wording deviates from the standard.")
    suggested_redline: str = Field(description="The exact text that should replace the problematic wording to comply with the internal standard.")

class ContractAnalysisResult(BaseModel):
    """The full, structured analysis for the entire contract."""
    flagged_clauses: List[ClauseAnalysis]

# Input schema for the API (what the frontend sends)
class ContractAnalysisRequest(BaseModel):
    contract_text: str = Field(description="The raw text of the contract to be analyzed.")

# --- Mock Internal Playbook Data ---
MOCK_PLAYBOOK_RULES = {
    "Limitation of Liability (LoL)": "Policy: Liability must be capped at 2x the annual fees paid and must exclude gross negligence/willful misconduct.",
    "Data Security & GDPR": "Policy: The contract must explicitly reference the Data Processing Addendum (DPA) and confirm compliance with EU GDPR Article 28.",
    "Termination for Convenience": "Policy: The company retains the right to terminate for convenience with 30 days notice. The counterparty must NOT have this right.",
}

# --- RAG Setup (Cached in memory for the API lifecycle) ---

def setup_playbook_vectorstore():
    """Initializes the vector store with the MOCK_PLAYBOOK_RULES."""
    print("Initializing Playbook Vector Store...")
    playbook_docs = [
        Document(page_content=v, metadata={"clause_title": k})
        for k, v in MOCK_PLAYBOOK_RULES.items()
    ]
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    # Using Chroma, the in-memory vector store, for the prototype
    vectorstore = Chroma.from_documents(playbook_docs, embeddings)
    print("Playbook Vector Store initialized.")
    return vectorstore

# This runs once when the API server starts
VECTORSTORE = setup_playbook_vectorstore()

# --- Utility Functions ---

def split_contract_text(contract_text: str) -> List[Document]:
    """Splits the full contract text into smaller, manageable chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500, 
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " "],
    )
    return text_splitter.create_documents([contract_text])

# --- Core LLM Analysis Logic ---

def analyze_contract_core(contract_text: str) -> ContractAnalysisResult:
    """Core logic to analyze contract text against the mock playbook using RAG."""
    
    vectorstore = VECTORSTORE
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
    contract_chunks = split_contract_text(contract_text)
    
    all_flagged_clauses = []
    
    system_prompt = (
        "You are a meticulous Legal Compliance Auditor. Your task is to analyze the provided contract "
        "section against the single most relevant internal Playbook Rule provided. "
        "You MUST follow the Pydantic schema strictly. ONLY flag the clause if it clearly violates or significantly deviates from the rule. "
        "If it is compliant, you MUST return { \"flagged_clauses\": [] }. "
        "For any flagged clause, you MUST also generate the exact text for the 'suggested_redline' field "
        "that corrects the deviation and makes the clause compliant with the internal standard."
    )
    
    human_prompt = (
        "ANALYZE THIS CONTRACT SECTION:\n---\n{contract_section}\n---\n"
        "AGAINST THIS MOST RELEVANT PLAYBOOK RULE:\n---\n{playbook_rule}\n---\n"
        "Return the analysis as a JSON object that adheres strictly to the defined schema."
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt),
    ])

    chain = prompt | llm.with_structured_output(ContractAnalysisResult)

    for chunk in contract_chunks:
        try:
            # 1. RAG Retrieval: Find the single best matching rule
            relevant_rules = vectorstore.similarity_search(chunk.page_content, k=1)
            retrieved_rule_text = relevant_rules[0].page_content 
            
            # 2. LLM Chain Execution
            analysis_chunk_result = chain.invoke({
                "contract_section": chunk.page_content,
                "playbook_rule": retrieved_rule_text
            })
            
            all_flagged_clauses.extend(analysis_chunk_result.flagged_clauses)

        except Exception as e:
            print(f"Warning: Analysis failed for a chunk. Error: {e}")
            
    return ContractAnalysisResult(flagged_clauses=all_flagged_clauses)


# --- API Endpoints ---

@app.get("/")
async def root():
    return {"message": "DCA Analysis API is running. Check /docs for documentation."}

@app.post("/analyze", response_model=ContractAnalysisResult)
async def analyze_contract_endpoint(request: ContractAnalysisRequest):
    """
    Accepts raw contract text and returns a structured compliance analysis.
    """
    try:
        # Calls the core logic function
        result = analyze_contract_core(request.contract_text)
        return result
    except Exception as e:
        # Handle server-side errors
        print(f"Critical error during analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Analysis Error: {e}")