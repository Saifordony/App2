import streamlit as st
import requests
import json
import os
from datetime import datetime

API_BASE = "http://localhost:8000"  # Update this when deploying

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
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            requests.post(f"{API_BASE}/log-session", json={"username": username, "timestamp": timestamp})
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
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            requests.post(f"{API_BASE}/log-session", json={"username": new_username, "timestamp": timestamp})
            st.success("Account created and logged in!")
        else:
            st.error("Please enter both a username and password")

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
                with st.spinner("Analyzing contract via API..."):
                    files = {"file": uploaded_file.getvalue()}
                    response = requests.post(f"{API_BASE}/analyze", files=files)
                    if response.ok:
                        st.session_state["analysis_result"] = response.json()
                        st.success("Analysis complete.")
                    else:
                        st.error("Failed to analyze contract.")

        if "analysis_result" in st.session_state:
            st.json(st.session_state["analysis_result"])

            if st.button("Evaluate"):
                with st.spinner("Evaluating and saving via API..."):
                    files = {"file": uploaded_file.getvalue()}
                    data = {"username": st.session_state["username"]}
                    response = requests.post(f"{API_BASE}/evaluate", files=files, data=data)
                    if response.ok:
                        result = response.json()
                        st.markdown(f"### Contract Health: **{result['result']['contract_health']}**")
                        st.success(f"Contract saved as: {result['filename']}")
                    else:
                        st.error("Failed to evaluate and save.")

    elif option == "View Saved Contracts":
        with st.spinner("Loading saved contracts..."):
            response = requests.get(f"{API_BASE}/saved/{st.session_state['username']}")
            if response.ok:
                results = response.json()
                if not results:
                    st.info("No saved contracts found.")
                for idx, data in enumerate(results):
                    with st.expander(f"Contract {idx+1}"):
                        st.json(data)
            else:
                st.error("Failed to load saved contracts.")

# ------------------------------
# Admin Panel
# ------------------------------
def admin_panel():
    st.title("Admin Dashboard")
    response = requests.get(f"{API_BASE}/admin/metrics")
    if response.ok:
        metrics = response.json()
        st.metric("Total Contracts Evaluated", metrics["total_contracts"])
        st.metric("Total Users", metrics["total_users"])
        st.subheader("All Users")
        st.write(metrics["users"])
    else:
        st.error("Failed to load metrics.")

    st.subheader("User Login Sessions")
    logs_response = requests.get(f"{API_BASE}/admin/sessions")
    if logs_response.ok:
        logs = logs_response.json()
        for log in logs:
            st.write(f"{log['timestamp']} - {log['username']}")
    else:
        st.error("Failed to load session logs.")

    st.subheader("All Evaluated Contracts")
    for user in metrics.get("users", []):
        st.markdown(f"#### {user}")
        response = requests.get(f"{API_BASE}/saved/{user}")
        if response.ok:
            contracts = response.json()
            for idx, contract in enumerate(contracts):
                with st.expander(f"{user} - Contract {idx+1}"):
                    st.json(contract)

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

