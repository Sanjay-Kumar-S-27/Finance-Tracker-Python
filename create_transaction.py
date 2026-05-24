import streamlit as st
import requests
import pandas as pd
from datetime import date
from cred import *
import plotly.express as px

def create_transactions():
    st.subheader("Create New Transaction")

    today = date.today()
    min_date = date(2026, 2, 1)

    selected_date = st.date_input(
        "Select Date",
        value=today,
        min_value=min_date,
        max_value=today
    )

    opening_balance = requests.get(f"{API_URL}/balance").json().get("Opening_balance")
    # opening_balance = balance_data.get("Opening_balance")

    # transaction_count = requests.get(f"{API_URL}/count").json()["count"]
    # st.write(transaction_count)

    # st.write(len(transactions))
    first_transaction = False if opening_balance != -1 else True
    if first_transaction:
        category_dict = {"Opening Balance": {'id': 1, 'name': 'Opening Balance', 'type': 'income', 'has_friend': 0}}
        type_options = ["Income"]
    else:
        type_options = ["Income", "Expense"]

        categories = requests.get(f"{API_URL}/categories").json()
    # st.write(categories)
    col1, col2, col3 = st.columns([2,2,2])
    with col1:
        selected_type = st.selectbox("Type", type_options)
    
    if not first_transaction:
        category_dict = {f"{c.get("name")}": c for c in categories if selected_type.lower() == c.get("type")}

    # st.write(category_dict)
    with col2:
        selected_category = st.selectbox("Category", list(category_dict.keys()))
    category_data = category_dict[selected_category]
    with col3:
        amount = st.number_input("Amount", min_value=0.0)
    note = st.text_input("Note", placeholder="Enter notes")

    friend_id = None

    if category_data.get("has_friend") == 1:
        friends = requests.get(f"{API_URL}/friends").json()
        friend_dict = {f.get("name"): f.get("id") for f in friends}
        selected_friend = st.selectbox("Select Friend", list(friend_dict.keys()))
        friend_id = friend_dict[selected_friend]


    if st.button("Add Transaction"):
        payload = {
            "date": str(selected_date),
            "category_id": category_data.get("id"),
            "amount": amount,
            "note": note,
            "friend_id": friend_id
        }

        requests.post(f"{API_URL}/transactions", json=payload)
        st.success("Transaction Added Successfully")

    if first_transaction:
        st.info("You can make your first transaction as only opening balance")
