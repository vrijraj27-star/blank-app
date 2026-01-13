import requests
import streamlit as st
import os

# -----------------------
# Secrets from Streamlit Cloud
# -----------------------
# Avoid hardcoding secrets in repo; prefer Streamlit secrets or environment variables.
LAMATIC_API_KEY = None
try:
    LAMATIC_API_KEY = st.secrets.get("LAMATIC_API_KEY")
except Exception:
    LAMATIC_API_KEY = os.getenv("LAMATIC_API_KEY")

GRAPHQL_URL = st.secrets.get("GRAPHQL_URL", "https://sandbox566-assistants320.lamatic.dev/graphql")
WORKFLOW_ID = st.secrets.get("WORKFLOW_ID", "daedf48a-5fcc-43c8-8bde-d5a0309638eb")
PROJECT_ID = st.secrets.get("PROJECT_ID", "8f7208ae-9d95-4c9b-b2f6-72d29a538578")

HEADERS = {
    "Authorization": f"Bearer {LAMATIC_API_KEY}" if LAMATIC_API_KEY else "",
    "Content-Type": "application/json",
    "x-project-id": PROJECT_ID
}

GQL_QUERY = """
query ExecuteWorkflow(
  $workflowId: String!
  $symbol: String
) {
  executeWorkflow(
    workflowId: $workflowId
    payload: {
      symbol: $symbol
    }
  ) {
    status
    result
  }
}
"""

# -----------------------
# UI
# -----------------------
st.set_page_config(page_title="Lamatic Flow Demo", layout="centered")

st.title("☁️ Lamatic Flow Cloud Demo")
st.caption("Streamlit Cloud + Lamatic GraphQL")

symbol_input = st.text_input("Enter Symbol", placeholder="AAPL")

if st.button("Run Flow"):
    if not LAMATIC_API_KEY:
        st.error("LAMATIC_API_KEY not configured; add it to Streamlit secrets or set an environment variable")
    elif not symbol_input:
        st.warning("Please enter a symbol")
    else:
        with st.spinner("Executing Lamatic workflow..."):
            payload = {
                "query": GQL_QUERY,
                "variables": {
                    "workflowId": WORKFLOW_ID,
                    "symbol": symbol_input
                }
            }

            response = requests.post(
                GRAPHQL_URL,
                headers=HEADERS,
                json=payload,
                timeout=30
            )

        if response.ok:
            try:
                data = response.json()
            except ValueError:
                st.error("Response is not valid JSON")
                st.text(response.text)
            else:
                result = data.get("data", {}).get("executeWorkflow")
                if result:
                    st.success("Workflow executed successfully 🚀")
                    st.code(result.get("status", ""))
                    st.json(result.get("result", {}))
                else:
                    st.error("Unexpected response structure")
                    st.json(data)
        else:
            st.error(f"Request failed: {response.status_code}")
            st.text(response.text)
