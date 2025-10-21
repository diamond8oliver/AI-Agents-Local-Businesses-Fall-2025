import streamlit as st
import requests

st.set_page_config(page_title="AI Agent Dashboard", layout="wide")

st.title("Local Business AI Agent Platform")

col1, col2 = st.columns(2)
with col1:
    st.subheader("System Health")
    try:
        resp = requests.get("http://localhost:8000/health", timeout=2)
        st.success(f"API health: {resp.json().get('status')}")
    except Exception as e:
        st.error(f"API not reachable: {e}")

with col2:
    st.subheader("Configuration Snapshot")
    try:
        resp = requests.get("http://localhost:8000/config", timeout=2)
        st.json(resp.json())
    except Exception as e:
        st.error(f"Cannot fetch config: {e}")


