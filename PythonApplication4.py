import streamlit as st
import json
import os
from datetime import datetime, timedelta
import PyPDF2

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
            st.session_state["session_start"] = datetime.now()
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
            st.session_state["session_start"] = datetime.now()
            st.success("Account created and logged in!")
        else:
            st.error("Please enter both a username and password")

# ------------------------------
# Extract PDF Text
# ------------------------------
def extract_pdf_text(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text.strip()

# ------------------------------
# Analyze Contract
# ------------------------------
def analyze_contract(text):
    word_count = len(text.split())
    summary = text[:300]
    health = "Healthy" if word_count > 200 else "Unhealthy"
    return {
        "word_count": word_count,
        "summary": summary,
        "contract_health": health
    }

# ------------------------------
# Save Analysis
# ------------------------------
def save_analysis(username, result):
    os.makedirs("saved_contracts", exist_ok=True)
    filename = f"saved_contracts/{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=4)
    return filename

# ------------------------------
# Load Saved Contracts
# ------------------------------
def load_saved_contracts(username):
    os.makedirs("saved_contracts", exist_ok=True)
    files = [f for f in os.listdir("saved_contracts") if f.startswith(username)]
    contracts = []
    for file in sorted(files):
        with open(os.path.join("saved_contracts", file), "r") as f:
            contracts.append(json.load(f))
    return contracts

# ------------------------------
# Admin Panel
# ------------------------------
def admin_panel():
    st.title("Admin Dashboard")
    files = os.listdir("saved_contracts") if os.path.exists("saved_contracts") else []
    users = set(f.split("_")[0] for f in files)
    st.metric("Total Contracts Evaluated", len(files))
    st.metric("Total Users", len(users))

    # Mock session log display
    st.subheader("Session Logs")
    st.write("These are mock logs. Actual logging will be implemented via API.")
    st.json([
        {"username": "user1", "login_time": "2024-07-05 09:00:00", "session_length": "15 min"},
        {"username": "user2", "login_time": "2024-07-05 09:20:00", "session_length": "23 min"},
        {"username": "admin", "login_time": "2024-07-05 10:00:00", "session_length": "35 min"}
    ])

    st.subheader("All Evaluated Contracts")
    for user in users:
        st.markdown(f"#### {user}")
        user_contracts = [f for f in files if f.startswith(user)]
        for idx, filename in enumerate(user_contracts):
            with open(os.path.join("saved_contracts", filename), "r") as f:
                contract = json.load(f)
                with st.expander(f"{user} - Contract {idx+1}"):
                    st.json(contract)

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
                text = extract_pdf_text(uploaded_file)
                st.session_state["analysis_result"] = analyze_contract(text)
                st.success("Analysis complete.")

        if "analysis_result" in st.session_state:
            st.json(st.session_state["analysis_result"])

            if st.button("Evaluate"):
                result = st.session_state["analysis_result"]
                st.markdown(f"### Contract Health: **{result['contract_health']}**")

                if st.button("Save Evaluation"):
                    filename = save_analysis(st.session_state["username"], result)
                    st.success(f"Contract saved as: {filename}")

    elif option == "View Saved Contracts":
        contracts = load_saved_contracts(st.session_state["username"])
        if not contracts:
            st.info("No saved contracts found.")
        for idx, data in enumerate(contracts):
            with st.expander(f"Contract {idx+1}"):
                st.json(data)

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
