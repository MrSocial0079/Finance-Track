import streamlit as st
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

def create_spin_wheel(rewards):
    # Create data for the wheel
    colors = ['#1E88E5', '#42A5F5', '#64B5F6', '#90CAF9', '#BBDEFB', '#E3F2FD']
    rewards_text = list(rewards.keys())
    
    # Create the wheel figure
    fig = go.Figure(
        data=[go.Pie(
            values=[1] * len(rewards),  # Equal probability for each reward
            labels=rewards_text,
            rotation=90,
            direction="clockwise",
            hole=0.3,
            marker_colors=colors * (len(rewards) // len(colors) + 1),
            textinfo="label",
            hoverinfo="none",
            textfont_size=14
        )]
    )
    
    # Update layout for better appearance
    fig.update_layout(
        showlegend=False,
        width=400,
        height=400,
        margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor="black",
        plot_bgcolor="black"
    )
    
    return fig

def show():
    # Available rewards
    rewards = {
        "🎁 $5 Gift Card": 500,
        "💰 $10 Cashback": 1000,
        "🎯 2x Points": 200,
        "🎨 Custom Theme": 300,
        "🎉 Achievement Badge": 100,
        "⭐ Premium Feature": 400
    }
    
    # Initialize session state variables for login tracking
    if 'points' not in st.session_state:
        st.session_state.points = 1000
    
   
    # Create columns for layout with exact HTML
    st.markdown("""
    <div style="background-color: navy blue; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
        <h3 style="text-align: center; margin-bottom: 20px;">🎡 Weekly Reward Spin</h3>
    """, unsafe_allow_html=True)
    
    # Show message about 7-day login requirement
    st.info("🔒 Note: This feature is designed to reward users who log in for 7 consecutive days.")
    
    # Show the wheel
    fig = create_spin_wheel(rewards)
    st.plotly_chart(fig, use_container_width=True)
    
    # Always allow spinning
    if st.button("🎲 Spin the Wheel!"):
        # Random reward
        reward = np.random.choice(list(rewards.keys()))
        points = rewards[reward]
        st.session_state.points += points
        
        st.success(f"🎉 Congratulations! You won {reward} worth {points} points!")
    
    # Close the div
    st.markdown("</div>", unsafe_allow_html=True)
