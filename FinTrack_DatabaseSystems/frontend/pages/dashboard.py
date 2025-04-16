import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
from datetime import datetime, timedelta
from components.transaction_list import show as show_transactions

# Backend URL
BACKEND_URL = 'http://localhost:8000'

def fetch_transactions():
    """Fetch transactions from the backend API"""
    if 'user' not in st.session_state or 'auth_token' not in st.session_state:
        return []
        
    try:
        response = requests.get(
            f"{BACKEND_URL}/transactions",
            headers={"Authorization": f"Bearer {st.session_state.auth_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        else:
            st.error(f"Error fetching transactions: {response.text}")
            return []
    except Exception as e:
        st.error(f"Error connecting to backend: {str(e)}")
        return []

def show():
    # Custom CSS
    st.markdown("""
    <style>
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        text-align: center;
        color: #1E88E5;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #1E88E5;
    }
    .metric-label {
        color: #1E88E5;
        font-size: 14px;
        margin-top: 5px;
    }
    .chart-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Check if user is logged in
    if 'user' not in st.session_state:
        st.warning("Please log in to view your dashboard")
        return
    
    # Fetch real transactions
    transactions = fetch_transactions()
    
    # Process transaction data for dashboard
    if transactions:
        df = pd.DataFrame(transactions)
        
        # Ensure date is in datetime format
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], format='ISO8601', errors='coerce').dt.tz_localize(None)
        elif 'created_at' in df.columns:
            df['date'] = pd.to_datetime(df['created_at'], format='ISO8601', errors='coerce').dt.tz_localize(None)
            
        # Calculate spending metrics
        total_spending = df[df['type'] == 'expense']['amount'].sum()
        avg_weekly = total_spending / 4 if total_spending > 0 else 0
        transaction_count = len(df)
        
        # Create category data
        if 'category' in df.columns and 'type' in df.columns and 'amount' in df.columns:
            category_data = df[df['type'] == 'expense'].groupby('category')['amount'].sum().to_dict()
        else:
            # Fallback to sample data if no categories
            category_data = {
                "🛒 Groceries": 0,
                "🏠 Rent": 0,
                "⚡ Utilities": 0,
                "🎬 Entertainment": 0,
                "🍽️ Dining": 0,
                "⛽ Transportation": 0,
                "🛍️ Shopping": 0,
                "📱 Phone": 0
            }
    else:
        # Sample data for demonstration when no transactions exist
        total_spending = 0
        avg_weekly = 0
        transaction_count = 0
        category_data = {
            "🛒 Groceries": 0,
            "🏠 Rent": 0,
            "⚡ Utilities": 0,
            "🎬 Entertainment": 0,
            "🍽️ Dining": 0,
            "⛽ Transportation": 0,
            "🛍️ Shopping": 0,
            "📱 Phone": 0
        }
    
    # Key Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${total_spending:.2f}</div>
            <div class="metric-label">Total Spending</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${avg_weekly:.2f}</div>
            <div class="metric-label">Average per Week</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{transaction_count}</div>
            <div class="metric-label">Transactions</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("💸 Spending Over Time")
        
        if transactions and 'date' in df.columns and 'amount' in df.columns and 'type' in df.columns:
            # Use real transaction data for time chart
            expense_df = df[df['type'] == 'expense']
            if not expense_df.empty:
                time_data = expense_df.groupby(expense_df['date'].dt.date)['amount'].sum().reset_index()
                time_data.columns = ['Date', 'Amount']
                
                fig = px.line(time_data, x='Date', y='Amount',
                             title=None,
                             labels={'Date': '', 'Amount': 'Spending ($)'},
                             line_shape='spline')
                fig.update_traces(line_color='#1E88E5')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No expense data available for time chart")
        else:
            # Generate sample daily spending data if no real data
            dates = [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(30)]
            amounts = [0 for _ in range(30)]
            df_time = pd.DataFrame({'Date': dates, 'Amount': amounts})
            
            fig = px.line(df_time, x='Date', y='Amount',
                         title=None,
                         labels={'Date': '', 'Amount': 'Spending ($)'},
                         line_shape='spline')
            fig.update_traces(line_color='#1E88E5')
            st.plotly_chart(fig, use_container_width=True)
            st.info("Add transactions to see your spending over time")
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📊 Categories")
        
        df_cat = pd.DataFrame(list(category_data.items()), columns=['Category', 'Amount'])
        if df_cat['Amount'].sum() > 0:
            fig = px.pie(df_cat, values='Amount', names='Category',
                        title=None,
                        hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Add expense transactions to see category breakdown")
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Recent Transactions
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("📝 Recent Transactions")
    
    # Pass the real transactions to the transaction list component
    show_transactions(transactions=transactions, show_filters=False)
    
    if not transactions:
        st.info("No transactions found. Add your first transaction in the Transactions tab.")
        
    st.markdown('</div>', unsafe_allow_html=True)
