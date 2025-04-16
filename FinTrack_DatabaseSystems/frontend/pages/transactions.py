import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta
from pytz import timezone
from components.transaction_list import show as show_transactions

# Backend URL
BACKEND_URL = 'http://localhost:8000'

def fetch_transactions():
    """Fetch transactions from the backend API"""
    if 'user' not in st.session_state or 'auth_token' not in st.session_state:
        st.warning("You must be logged in to view transactions")
        return []
        
    try:
        # Show a loading message while fetching
        with st.spinner("Fetching your transactions..."):
            response = requests.get(
                f"{BACKEND_URL}/transactions",
                headers={"Authorization": f"Bearer {st.session_state.auth_token}"}
            )
        
        if response.status_code == 200:
            data = response.json()
            transactions = data.get('data', [])
            if not transactions:
                st.info("No transactions found. Add your first transaction using the form above.")
            return transactions
        else:
            st.error(f"Error fetching transactions: {response.text}")
            return []
    except Exception as e:
        st.error(f"Error connecting to backend: {str(e)}")
        return []

def add_transaction(transaction_data):
    """Add a new transaction via the backend API"""
    if 'user' not in st.session_state or 'auth_token' not in st.session_state:
        st.error("You must be logged in to add transactions")
        return False
        
    try:
        response = requests.post(
            f"{BACKEND_URL}/transactions",
            headers={"Authorization": f"Bearer {st.session_state.auth_token}"},
            json=transaction_data
        )
        
        if response.status_code == 200:
            return True
        else:
            st.error(f"Error adding transaction: {response.text}")
            return False
    except Exception as e:
        st.error(f"Error connecting to backend: {str(e)}")
        return False

def show():
    st.title("💳 Transactions")
    
    # Check if user is logged in
    if 'user' not in st.session_state:
        st.warning("Please log in to manage your transactions")
        return
    
    # Tabs for Add Transaction and View Transactions
    tab1, tab2 = st.tabs(["Add Transaction", "View & Analyze"])
    
    with tab1:
        st.subheader("Add New Transaction")
        
        # Transaction type selection outside the form
        if 'transaction_type' not in st.session_state:
            st.session_state.transaction_type = 'expense'
        
        st.session_state.transaction_type = st.selectbox(
            "Transaction Type", 
            ["expense", "income", "transfer"],
            index=["expense", "income", "transfer"].index(st.session_state.transaction_type)
        )
        
        # Transaction form
        with st.form("transaction_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                amount = st.number_input("Amount ($)", min_value=0.01, step=0.01)
                
                # Dynamic categories based on transaction type in session state
                if st.session_state.transaction_type == "income":
                    category = st.selectbox(
                        "Category",
                        ["💸 Salary", "💰 Freelance", "💳 Investment", "🎁 Gift", 
                         "💸 Refund", "🏢 Business"]
                    )
                else:  # expense or transfer
                    category = st.selectbox(
                        "Category",
                        ["🛒 Groceries", "🎬 Entertainment", "⛽ Transportation", 
                         "🍽️ Dining", "🛍️ Shopping", "🏠 Rent", "💡 Utilities", 
                         "📱 Phone", "💊 Healthcare", "📚 Education"]
                    )
            
            with col2:
                description = st.text_input("Description")
                notes = st.text_area("Notes (Optional)", "")
                tags = st.text_input("Tags (comma separated, optional)", "")
            
            if st.form_submit_button("Add Transaction", use_container_width=True):
                # Validate required fields
                if not description.strip():
                    st.error("❌ Description is required")
                elif amount <= 0:
                    st.error("❌ Amount must be greater than zero")
                else:
                    # Prepare transaction data
                    transaction_data = {
                        "amount": float(amount),
                        "description": description,
                        "category": category,
                        "date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),  # Current time in ISO format
                        "type": st.session_state.transaction_type,
                        "notes": notes if notes else None
                    }
                    
                    # Add tags if provided
                    if tags:
                        transaction_data["tags"] = [tag.strip() for tag in tags.split(',')]
                    
                    # Send to backend
                    if add_transaction(transaction_data):
                        # Update global session state so AI Insights and other pages see the latest transactions
                        st.session_state['transactions'] = fetch_transactions()
                        st.success("✅ Transaction added successfully!")
                        st.rerun()
    
    with tab2:
        # Fetch real transactions from backend
        transactions = fetch_transactions()
        st.session_state['transactions'] = transactions
        
        # Analytics Section
        if transactions:
            st.subheader("📊 Transaction Analytics")
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(transactions)
            if not df.empty and 'date' in df.columns:
                # Print dtype before conversion
                print('Before conversion:', df['date'].dtype)
                # Use a more flexible parsing approach with format='ISO8601'
                df['date'] = pd.to_datetime(df['date'], format='ISO8601', errors='coerce')
                # Print dtype after conversion
                print('After conversion:', df['date'].dtype)
                
                tab1, tab2, tab3 = st.tabs(["Category Breakdown", "Time Trends", "Statistics"])
                
                with tab1:
                    # Category breakdown
                    if 'category' in df.columns and 'type' in df.columns and 'amount' in df.columns:
                        category_data = df[df['type'] == 'expense'].groupby('category')['amount'].sum().reset_index()
                        if not category_data.empty:
                            fig = px.pie(
                                category_data,
                                values='amount',
                                names='category',
                                title='Spending by Category',
                                hole=0.4,
                                color_discrete_sequence=px.colors.qualitative.Bold
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No category data available yet")
                
                with tab2:
                    # Time trends
                    if 'date' in df.columns and 'amount' in df.columns and 'type' in df.columns:
                        # Group by date and calculate daily totals
                        df['date_only'] = df['date'].dt.date
                        daily_totals = df.groupby(['date_only', 'type'])['amount'].sum().unstack().fillna(0)
                        
                        if not daily_totals.empty:
                            # Create time series chart
                            fig = px.line(
                                daily_totals.reset_index(),
                                x='date_only',
                                y=['expense', 'income'] if 'income' in daily_totals.columns and 'expense' in daily_totals.columns else ['expense'],
                                title='Spending Over Time',
                                labels={'date': 'Date', 'amount': 'Amount ($)', 'type': 'Type'},
                                color_discrete_sequence=['#ff4b4b', '#00cc66']
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No time-series data available yet")
                
                with tab3:
                    # Statistics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if 'type' in df.columns and 'amount' in df.columns:
                            expense_data = df[df['type'] == 'expense']['amount']
                            if not expense_data.empty:
                                avg_expense = expense_data.mean()
                                st.metric("Average Expense", f"${avg_expense:.2f}")
                            else:
                                st.metric("Average Expense", "$0.00")
                    
                    with col2:
                        if 'category' in df.columns and not df['category'].empty:
                            most_common_category = df['category'].mode().iloc[0]
                            st.metric("Most Used Category", most_common_category)
                        else:
                            st.metric("Most Used Category", "N/A")
                    
                    with col3:
                        transaction_count = len(df)
                        st.metric("Total Transactions", transaction_count)
        
        # Transactions List with Filters
        st.subheader("📝 Transaction List")
        show_transactions(transactions=transactions)
