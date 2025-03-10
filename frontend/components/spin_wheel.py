import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import random

# Reward options
rewards = ["$5 Cashback", "10% Discount", "Bonus Points", "Try Again", "Free Coffee"]

# Colors for pie chart
colors = ["#FF5733", "#33FF57", "#3357FF", "#F4FF33", "#FF33F6"]

def show(api_url):
    st.subheader("🎰 Spin the Wheel")

    fig, ax = plt.subplots(figsize=(4, 4))
    
    # Wheel slices
    wedges, texts = ax.pie([1] * len(rewards), labels=rewards, colors=colors, startangle=0)

    if st.button("Spin"):
        # Simulate wheel spinning
        spin_time = random.uniform(2, 4)  # Random spin duration
        rotations = int(spin_time * 10)  # Number of frames

        for i in range(rotations):
            angle = (i * 10) % 360  # Rotate in steps
            ax.clear()
            ax.pie([1] * len(rewards), labels=rewards, colors=colors, startangle=angle)
            st.pyplot(fig)
            time.sleep(0.05)  # Smooth animation

        # Pick a random reward
        chosen_reward = random.choice(rewards)
        st.success(f"🎉 You won: {chosen_reward} 🎉")