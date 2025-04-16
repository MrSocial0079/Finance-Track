import streamlit as st
from components.spin_wheel import show as show_spin_wheel

def show():
    st.title("🎮 Rewards")
    st.markdown("""
    <style>
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Description of the weekly reward system
    st.markdown("""
    ### 🎡 Weekly Reward System
    
    Log in to FinTrack every day of the week to earn a free spin on our reward wheel!
    You can win points, gift cards, and exclusive features to enhance your financial journey.
    
    **How it works:**
    1. Log in to FinTrack every day for 7 consecutive days
    2. Unlock a free spin on the reward wheel
    3. Win amazing prizes and points
    4. Use your points to unlock premium features
    """)
    
    # Spin & Win section
    st.markdown("### 🎡 Spin & Win")
    st.markdown("""
    Complete challenges and earn points to spin the wheel for amazing rewards!
    Spin once every 24 hours for a chance to win points, gift cards, and more.
    """)
    
    show_spin_wheel()
