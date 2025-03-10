import streamlit as st
import requests
import pandas as pd

def show(api_url):
    st.subheader("📊 Transactions")

    # Fetch Transactions
    response = requests.get(f"{api_url}/transactions/")
    if response.status_code == 200:
        transactions = response.json()
        
        # Convert to DataFrame for better display
        df = pd.DataFrame(transactions)
        
        # Ensure correct column order
        if not df.empty:
            df = df[["id", "amount", "category", "type", "date"]]
            st.dataframe(df)

            # Transaction Update
            st.subheader("✏️ Update Transaction")
            transaction_id = st.selectbox("Select Transaction to Update", df["id"].tolist())
            new_amount = st.number_input("New Amount", min_value=0.01)
            new_category = st.text_input("New Category")
            new_type = st.selectbox("New Type", ["income", "expense"])

            if st.button("Update"):
                update_response = requests.put(f"{api_url}/transactions/{transaction_id}", json={
                    "amount": new_amount,
                    "category": new_category,
                    "type": new_type
                })
                if update_response.status_code == 200:
                    st.success("Transaction updated successfully!")
                else:
                    st.error("Failed to update transaction.")

            # Transaction Deletion
            st.subheader("🗑 Delete Transaction")
            delete_id = st.selectbox("Select Transaction to Delete", df["id"].tolist())

            if st.button("Delete"):
                delete_response = requests.delete(f"{api_url}/transactions/{delete_id}")
                if delete_response.status_code == 200:
                    st.success("Transaction deleted successfully!")
                else:
                    st.error("Failed to delete transaction.")

        else:
            st.info("No transactions found.")