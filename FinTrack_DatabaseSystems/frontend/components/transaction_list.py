import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def show(transactions=None, show_filters=True):
    if transactions is None or len(transactions) == 0:
        st.info("No transactions found. Add your first transaction using the form above.")
        return
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(transactions)
    
    # Ensure date column is in datetime format
    if 'date' in df.columns:
        # Use a more flexible parsing approach with format='ISO8601'
        df['date'] = pd.to_datetime(df['date'], format='ISO8601', errors='coerce').dt.tz_localize(None)  # Remove timezone info
    elif 'created_at' in df.columns:
        # Use created_at as fallback if date is not available
        df['date'] = pd.to_datetime(df['created_at'], format='ISO8601', errors='coerce').dt.tz_localize(None)  # Remove timezone info
    
    # Sort by date (newest first) to ensure new transactions appear at the top
    if 'date' in df.columns:
        df = df.sort_values(by='date', ascending=False)
    
    # Create a copy of the original dataframe before filtering
    original_df = df.copy()
        
    if show_filters:
        st.markdown("### 🔍 Filter Transactions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Date range filter
            date_range = st.selectbox(
                "Date Range",
                ["Last 7 days", "Last 30 days", "Last 90 days", "All time"],
                index=1
            )
            
            if date_range != "All time" and 'date' in df.columns:
                days = int(date_range.split()[1])
                cutoff_date = (datetime.now() - timedelta(days=days))
                
                # Make sure both dates are naive (no timezone)
                df = df[df['date'] >= cutoff_date]
        
        with col2:
            # Category filter
            if not df.empty and 'category' in df.columns:
                categories = ["All"] + sorted(df['category'].unique().tolist())
                selected_category = st.selectbox("Category", categories)
                
                if selected_category != "All":
                    df = df[df['category'] == selected_category]
        
        with col3:
            # Transaction type filter
            types = ["All", "Expense", "Income", "Transfer"]
            selected_type = st.selectbox("Type", types)
            
            if selected_type != "All" and 'type' in df.columns:
                df = df[df['type'].str.lower() == selected_type.lower()]
        
        # Search filter
        search = st.text_input("🔍 Search descriptions", "")
        if search and 'description' in df.columns:
            df = df[df['description'].str.contains(search, case=False, na=False)]
    
    # Display summary metrics
    if not df.empty and 'amount' in df.columns and 'type' in df.columns:
        st.markdown("### 📊 Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_expenses = df[df['type'] == 'expense']['amount'].sum()
            st.metric("Total Expenses", f"${total_expenses:,.2f}")
        
        with col2:
            total_income = df[df['type'] == 'income']['amount'].sum()
            st.metric("Total Income", f"${total_income:,.2f}")
        
        with col3:
            net = total_income - total_expenses
            st.metric("Net Amount", f"${net:,.2f}", 
                     delta=f"${abs(net):,.2f}", 
                     delta_color="normal" if net >= 0 else "inverse")
    
    # Custom CSS for transactions
    st.markdown("""
    <style>
    .transaction-card {
        border: 1px solid #dcdcdc;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        background-color: #f0f7ff;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .transaction-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .transaction-expense {
        border-left: 6px solid #ff4b4b;
    }
    .transaction-income {
        border-left: 6px solid #00cc66;
    }
    .transaction-transfer {
        border-left: 6px solid #1c83e1;
    }
    .transaction-amount {
        font-weight: bold;
        font-size: 1.3em;
        color: #333333;
    }
    .transaction-date {
        color: #555555;
        font-size: 0.9em;
        font-weight: 500;
    }
    .transaction-category {
        background-color: #f0f7ff;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 0.9em;
        color: #0066cc;
        font-weight: 500;
        display: inline-block;
    }
    .transaction-description {
        margin-top: 8px;
        font-size: 1.1em;
        color: #333333;
    }
    .transaction-tags {
        margin-top: 8px;
    }
    .transaction-tag {
        background-color: #e6f3ff;
        color: #0066cc;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 0.8em;
        margin-right: 5px;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display transactions
    st.markdown("### Transaction List")
    
    if df.empty:
        st.info("No transactions match your filters.")
        if len(original_df) > 0 and show_filters:
            if st.button("Show All Transactions"):
                df = original_df.copy()
        else:
            return
    
    for _, row in df.iterrows():
        # Determine transaction type for styling
        tx_type = row.get('type', 'expense').lower()
        
        # Format date
        if 'date' in row:
            # Convert to local time for display
            try:
                # If date is a string, parse it first
                if isinstance(row['date'], str):
                    date_obj = datetime.fromisoformat(row['date'].replace('Z', '+00:00'))
                else:
                    date_obj = row['date']
                
                # Convert UTC to Eastern Time (UTC-4)
                eastern_time = date_obj - timedelta(hours=4)
                
                # Format in local time
                date_str = eastern_time.strftime("%b %d, %Y at %I:%M %p")
            except Exception as e:
                # Fallback if date parsing fails
                date_str = str(row['date'])
        else:
            date_str = ""
        
        # Format amount with color based on type
        if tx_type == 'expense':
            amount_html = f'<span style="color: #ff4b4b;">-${row["amount"]:.2f}</span>'
        elif tx_type == 'income':
            amount_html = f'<span style="color: #00cc66;">+${row["amount"]:.2f}</span>'
        else:  # transfer
            amount_html = f'<span style="color: #1c83e1;">${row["amount"]:.2f}</span>'
        
        # Build the transaction card HTML
        html = f"""
        <div class="transaction-card transaction-{tx_type}">
            <div style="display: flex; justify-content: space-between;">
                <div>
                    <div class="transaction-date">{date_str}</div>
                    <div class="transaction-description">{row.get('description', 'No description')}</div>
                </div>
                <div class="transaction-amount">{amount_html}</div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                <span class="transaction-category">{row.get('category', 'Uncategorized')}</span>
        """
        
        # Add tags if available
        if 'tags' in row and row['tags'] and isinstance(row['tags'], (list, tuple)):
            html += '<div class="transaction-tags">'
            for tag in row['tags']:
                html += f'<span class="transaction-tag">{tag}</span>'
            html += '</div>'
        
        html += "</div></div>"
        
        st.markdown(html, unsafe_allow_html=True)
        
        # Add action buttons for each transaction
        col1, col2 = st.columns([9, 1])
        with col2:
            if st.button("🗑️", key=f"delete_{row.get('id', '')}"):
                st.session_state['transaction_to_delete'] = row.get('id', '')
                st.rerun()
