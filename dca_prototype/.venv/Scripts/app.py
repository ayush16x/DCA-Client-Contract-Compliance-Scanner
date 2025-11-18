import streamlit as st
from pypdf import PdfReader
import requests # Used for API communication
import json
from dotenv import load_dotenv

# Base URL for the FastAPI server (assuming default port 8000)
API_URL = "http://127.0.0.1:8000/analyze"

# Load environment variables (only needed for Streamlit if using it for config later)
load_dotenv()

# --- Mock Data (for testing when using the sample text) ---
SAMPLE_CONTRACT_TEXT = """
ARTICLE 5: TERM AND TERMINATION. The term begins on signing. The Customer may terminate this Agreement for convenience at any time with 60 days written notice.
ARTICLE 6: LIABILITY LIMIT. Notwithstanding anything to the contrary, neither party's total liability shall exceed the total amount paid by Customer in the preceding six months ($50,000 max).
ARTICLE 7: DATA. The parties shall comply with all data laws. No explicit mention of the company's DPA is required.
"""

# --- Utility Functions ---

def extract_text_from_pdf(pdf_file):
    """Extracts text from a PDF file."""
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"Error processing PDF: {e}")
        return None

def main():
    st.set_page_config(page_title="Dynamic Clause Analyzer (DCA) Client", layout="wide")
    st.title("⚖️ DCA Client: Contract Compliance Scanner")
    st.markdown("**(FastAPI Backend, Streamlit Frontend)**")
    st.markdown("---")

    uploaded_file = st.file_uploader(
        "Upload a Contract (PDF)",
        type="pdf",
        help="The file will be processed and sent to the FastAPI analysis server."
    )

    contract_text = None

    if uploaded_file:
        with st.spinner("Processing file..."):
            contract_text = extract_text_from_pdf(uploaded_file)

        if contract_text:
            st.success("Text extraction complete!")
            with st.expander("Review Extracted Text Snippet"):
                st.text_area("Contract Text (First 500 chars)", contract_text[:500], height=150)
    
    st.subheader("Action: Analyze Contract Clauses")

    text_to_analyze = contract_text if contract_text else SAMPLE_CONTRACT_TEXT
    
    if st.button("Start Compliance Scan (Call API)", use_container_width=True, type="primary"):
        
        if not text_to_analyze:
            st.warning("Please upload a file or use the sample text.")
            return

        with st.spinner("Sending request to FastAPI server for analysis..."):
            
            try:
                # 1. Prepare payload
                payload = {"contract_text": text_to_analyze}
                headers = {"Content-Type": "application/json"}
                
                # 2. Call the API using the requests library
                response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
                
                # 3. Check response status
                if response.status_code == 200:
                    analysis_result = response.json()
                else:
                    st.error(f"API Error: Received status code {response.status_code}.")
                    st.error(f"Response Detail: {response.text}")
                    return

            except requests.exceptions.ConnectionError:
                st.error(f"Connection Error: Could not connect to the API server at {API_URL}.")
                st.info("Please ensure your FastAPI server is running in a separate terminal: `uvicorn api_server:app --reload`")
                return
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                return

        # --- Display Results ---
        flagged_clauses = analysis_result.get("flagged_clauses", [])

        if flagged_clauses:
            st.success("Analysis Complete! 🚨 Critical Red Flags Found.")

            data_to_display = flagged_clauses
            
            column_order = (
                "risk_level",
                "clause_title",
                "discrepancy_summary",
                "suggested_redline",
                "internal_standard",
                "contract_snippet"
            )
            
            cols_present = [c for c in column_order if data_to_display and c in data_to_display[0].keys()]

            st.dataframe(
                data_to_display,
                use_container_width=True,
                column_order=tuple(cols_present)
            )
        else:
            st.success("Analysis Complete! 🎉 No high-risk deviations found based on the playbook.")


if __name__ == "__main__":
    main()