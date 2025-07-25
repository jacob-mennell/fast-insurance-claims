import streamlit as st
import requests
import pandas as pd

# Load secrets from .streamlit/secrets.toml or secrets.toml
API_URL = st.secrets["api"]["API_URL"]
API_KEY = st.secrets["api"]["API_KEY"]
HEADERS = {"X-API-Key": API_KEY}

st.title("Insurance Claims Reporter")


# Sidebar navigation
page = st.sidebar.radio(
    "Navigation",
    ("Submit Claim", "View All Claims", "View Logs", "Fraud Checker"),
    index=0,
)

if page == "Submit Claim":
    st.header("Create a Claim")
    with st.form("create_claim"):
        claim_number = st.text_input("Claim Number")
        claimant_name = st.text_input("Claimant Name")
        amount = st.number_input("Amount", min_value=0.0)
        description = st.text_area("Description")
        status = st.selectbox("Status", ["pending", "approved", "rejected"])
        is_approved = st.checkbox("Is Approved?", value=False)
        date_filed = st.date_input("Date Filed")
        submitted = st.form_submit_button("Submit")
        if submitted:
            resp = requests.post(
                f"{API_URL}/claims",
                json={
                    "claim_number": claim_number,
                    "claimant_name": claimant_name,
                    "amount": amount,
                    "description": description,
                    "status": status,
                    "is_approved": is_approved,
                    "date_filed": str(date_filed),
                },
                headers=HEADERS,
            )
            try:
                st.write(resp.json())
            except Exception:
                st.error(f"Error: {resp.status_code} - {resp.text}")

elif page == "View All Claims":
    st.header("All Claims")
    if st.button("Refresh Claims"):
        claims = requests.get(f"{API_URL}/claims", headers=HEADERS).json()
        if isinstance(claims, list) and claims:
            df = pd.DataFrame(claims)
            st.dataframe(df)
        else:
            st.write(claims)


elif page == "View Logs":
    st.header("Claim Logs")
    if st.button("Refresh Logs"):
        logs = requests.get(f"{API_URL}/logs", headers=HEADERS).json()
        if isinstance(logs, list) and logs:
            df = pd.DataFrame(logs)
            st.dataframe(df)
        else:
            st.write(logs)

elif page == "Fraud Checker":
    st.header("Fraudulent Claim Checker")
    claim_id = st.number_input("Enter Claim ID to Check", min_value=1, step=1)
    if st.button("Check for Fraud"):
        try:
            resp = requests.get(
                f"{API_URL}/agent/check_fraud/{int(claim_id)}", headers=HEADERS
            )
            if resp.status_code == 200:
                result = resp.json()
                st.write(f"**Claim ID:** {result['claim_id']}")
                st.write(f"**Claim Text:** {result['claim_text']}")
                st.write(
                    f"**Prediction:** {result['predicted_label']} (probability: {result['fraud_probability']:.2f})"
                )
                st.write("**All Scores:**")
                st.json(
                    {
                        label: score
                        for label, score in zip(result["labels"], result["scores"])
                    }
                )
            else:
                st.error(f"Error: {resp.status_code} - {resp.text}")
        except Exception as e:
            st.error(f"Exception: {e}")
