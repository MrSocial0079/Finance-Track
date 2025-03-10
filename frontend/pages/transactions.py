import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000/transactions"

def fetch_transactions():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    return []

def show():
    st.title("📊 Transactions Page")
    
    # Load Transactions
    transactions = fetch_transactions()

    if transactions:
        df = pd.DataFrame(transactions)
        df = df[["id", "amount", "category", "type", "date"]]  # Keep relevant columns
        st.dataframe(df)

        # Transaction Update Form
        st.subheader("✏️ Update Transaction")
        transaction_id = st.selectbox("Select Transaction", df["id"].tolist())
        new_amount = st.number_input("New Amount", min_value=0.01)
        new_category = st.text_input("New Category")
        new_type = st.selectbox("New Type", ["income", "expense"])

        if st.button("Update Transaction"):
            update_response = requests.put(f"{API_URL}/{transaction_id}", json={
                "amount": new_amount,
                "category": new_category,
                "type": new_type
            })
            if update_response.status_code == 200:
                st.success("Transaction updated successfully!")
                st.experimental_rerun()
            else:
                st.error("Failed to update transaction.")

        # Transaction Deletion
        st.subheader("🗑 Delete Transaction")
        delete_id = st.selectbox("Select Transaction to Delete", df["id"].tolist())

        if st.button("Delete Transaction"):
            delete_response = requests.delete(f"{API_URL}/{delete_id}")
            if delete_response.status_code == 200:
                st.success("Transaction deleted successfully!")
                st.experimental_rerun()
            else:
                st.error("Failed to delete transaction.")

    else:
        st.info("No transactions found.")

    # Add New Transaction
    st.subheader("➕ Add New Transaction")
    amount = st.number_input("Amount", min_value=0.01)
    category = st.text_input("Category")
    transaction_type = st.selectbox("Type", ["income", "expense"])
    
    if st.button("Add Transaction"):
        add_response = requests.post(API_URL, json={
            "amount": amount,
            "category": category,
            "type": transaction_type
        })
        if add_response.status_code == 200:
            st.success("Transaction added successfully!")
            st.experimental_rerun()
        else:
            st.error("Failed to add transaction.")