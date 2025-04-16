import streamlit as st

def show():
    with st.sidebar:
        st.title("💰 Fintrack")
        st.markdown("---")
        
        # Navigation
        pages = {
            "📊 Dashboard": "dashboard",
            "💳 Transactions": "transactions",
            "🎮 Rewards": "gamification",
            "🤖 AI Tips": "ai_tips",
        }
        
        selected = st.radio("Navigation", list(pages.keys()))
        st.session_state.current_page = pages[selected]
        
        st.markdown("---")
        
        # User info, verification status, and logout
        if st.session_state.user:
            st.write(f"👤 {st.session_state.user['email']}")
            

            
            # Logout button
            if st.button("🚪 Logout"):
                st.session_state.user = None
                st.rerun()
