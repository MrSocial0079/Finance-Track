import streamlit as st
import requests

def show(api_url):
    st.subheader("🏆 Challenges")
    response = requests.get(f"{api_url}/gamification/challenges")
    if response.status_code == 200:
        challenges = response.json()
        for challenge in challenges:
            st.write(f"**{challenge['challenge']}** - 🎁 Reward: {challenge['reward']}")