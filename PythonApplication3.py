import streamlit as st
import PyPDF2
import json
import os
from datetime import datetime

# ------------------------------
# Sign In and Sign Up Pages
# ------------------------------
def login():
    st.subheader("Sign In")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        if username and password:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.success("Logged in successfully!")
        else:
            st.error("Please enter both username and password")

def signup():
    st.subheader("Sign Up")
    new_username = st.text_input("Choose a Username", key="signup_username")
    new_password = st.text_input("Choose a Password", type="password", key="signup_password")
    if st.button("Create Account"):
        if new_username and new_password:
            st.session_state["authenticated"] = True
            st.session_state["username"] = new_username
            st.success("Account created and logged in!")
        else:
            st.error("Please enter both a username and password")

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
    return result

# ------------------------------
# Save Analysis
# ------------------------------
def save_analysis(username, result):
    os.makedirs("saved_contracts", exist_ok=True)
    filename = f"saved_contracts/{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=4)
    st.success(f"Contract saved as: {filename}")

# ------------------------------
# View Saved Contracts
# ------------------------------
def view_saved_contracts(username):
    st.subheader("Saved Evaluated Contracts")
    os.makedirs("saved_contracts", exist_ok=True)
    files = [f for f in os.listdir("saved_contracts") if f.startswith(username)]
    if not files:
        st.info("No saved contracts found.")
    else:
        for file in sorted(files, reverse=True):
            with open(os.path.join("saved_contracts", file), "r") as f:
                data = json.load(f)
                with st.expander(file):
                    st.json(data)

# ------------------------------
# Admin Panel
# ------------------------------
def admin_panel():
    st.title("Admin Dashboard")
    os.makedirs("saved_contracts", exist_ok=True)
    all_files = os.listdir("saved_contracts")
    total_contracts = len(all_files)
    users = set([f.split("_")[0] for f in all_files])
    st.metric("Total Contracts Evaluated", total_contracts)
    st.metric("Total Users", len(users))

    st.subheader("Login Records")
    st.write("Logged in as:", st.session_state.get("username"))
    st.write("Logged in at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    st.subheader("All Evaluated Contracts")
    for file in sorted(all_files, reverse=True):
        with open(os.path.join("saved_contracts", file), "r") as f:
            data = json.load(f)
            with st.expander(file):
                st.json(data)

# ------------------------------
# Main App Flow
# ------------------------------
def main():
    st.title("Contract Evaluation App")

    if st.session_state["username"] == "admin":
        admin_panel()
        return

    option = st.radio("Choose an action", ["Evaluate New Contract", "View Saved Contracts"])

    if option == "Evaluate New Contract":
        uploaded_file = st.file_uploader("Upload your Contract (PDF)", type="pdf")

        if uploaded_file:
            st.success("PDF uploaded successfully.")

            if st.button("Analyze"):
                with st.spinner("Analyzing contract..."):
                    text = extract_pdf_text(uploaded_file)
                    st.session_state["analysis_result"] = analyze_contract(text)
                    st.success("Analysis complete.")

        if "analysis_result" in st.session_state:
            st.json(st.session_state["analysis_result"])

            if st.button("Evaluate"):
                health = st.session_state["analysis_result"].get("contract_health", "Unknown")
                st.markdown(f"### Contract Health: **{health}**")

                if st.button("Save Evaluation"):
                    save_analysis(st.session_state["username"], st.session_state["analysis_result"])

    elif option == "View Saved Contracts":
        view_saved_contracts(st.session_state["username"])

# ------------------------------
# App Entry Point
# ------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "auth_mode" not in st.session_state:
    st.session_state["auth_mode"] = None

if not st.session_state["authenticated"]:
    st.title("Welcome")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sign In"):
            st.session_state["auth_mode"] = "login"
    with col2:
        if st.button("Sign Up"):
            st.session_state["auth_mode"] = "signup"

    if st.session_state["auth_mode"] == "login":
        login()
    elif st.session_state["auth_mode"] == "signup":
        signup()
else:
    main()

