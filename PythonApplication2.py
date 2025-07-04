import streamlit as st
import PyPDF2
import json
import os

# ------------------------------
# Simple Login
# ------------------------------
def login():
    st.title("Login / Sign Up")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username and password:
            # Demo: Accept any non-empty input
            st.session_state["authenticated"] = True
            st.success("Logged in successfully!")
        else:
            st.error("Please enter both username and password")

# ------------------------------
# Extract Text from PDF
# ------------------------------
def extract_pdf_text(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text.strip()

# ------------------------------
# Analyze Contract and Generate JSON
# ------------------------------
def analyze_contract(text):
    word_count = len(text.split())
    result = {
        "word_count": word_count,
        "summary": text[:300],  # First 300 characters
        "contract_health": "Healthy" if word_count > 200 else "Unhealthy"
    }
    with open("contract_analysis.json", "w") as f:
        json.dump(result, f, indent=4)
    return result

# ------------------------------
# Main App Flow
# ------------------------------
def main():
    st.title("Contract Evaluation App")

    uploaded_file = st.file_uploader("Upload your Contract (PDF)", type="pdf")

    if uploaded_file:
        st.success("PDF uploaded successfully.")

        if st.button("Analyze"):
            with st.spinner("Analyzing contract..."):
                text = extract_pdf_text(uploaded_file)
                analysis_result = analyze_contract(text)
                st.success("Analysis complete. JSON generated.")

                st.json(analysis_result)

                if st.button("Evaluate"):
                    st.markdown(f"### Contract Health: **{analysis_result['contract_health']}**")

# ------------------------------
# App Entry Point
# ------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login()
else:
    main()

