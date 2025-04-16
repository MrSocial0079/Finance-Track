import streamlit as st
import requests
import json
from datetime import datetime

BACKEND_URL = 'http://localhost:8000'

def ask_gemini(prompt):
    response = requests.post(
        f"{BACKEND_URL}/ai/ask_gemini",
        json={"prompt": prompt},
        headers={"Authorization": f"Bearer {st.session_state.auth_token}"}
    )
    if response.status_code == 200:
        data = response.json()
        # Show the real error if present
        if "error" in data:
            return f"Gemini error: {data['error']}"
        return data.get("answer")
    else:
        return f"Error: {response.text}"

def show():
    st.title("AI Financial Literacy Assistant")
    user_prompt = st.text_input("Ask Gemini anything about financial literacy:")

    if st.button("Get AI Answer") and user_prompt.strip():
        try:
            with st.spinner("Gemini is thinking..."):
                answer = ask_gemini(user_prompt)
                st.write("**Gemini says:**")
                st.write(answer)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print("Gemini error:", str(e))