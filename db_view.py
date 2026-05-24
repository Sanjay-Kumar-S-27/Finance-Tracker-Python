import streamlit as st
import requests
import pandas as pd
from datetime import date
from cred import *
import plotly.express as px

def show_friends_summary():
    data = requests.get(f"{API_URL}/transactions/friends").json()

    if not data:
        st.info("No friend transactions found.")
        return

    st.markdown("#### 👥 Friends Summary")

    for item in data:
        net = item["Income"] - item["Expense"]

        if net > 0:
            net_color = "#2ecc71"
            net_label = f"You'll receive  ₹{net:,.0f}"
            net_icon = "💚"
        elif net < 0:
            net_color = "#e74c3c"
            net_label = f"You owe  ₹{abs(net):,.0f}"
            net_icon = "🔴"
        else:
            net_color = "#95a5a6"
            net_label = "Settled"
            net_icon = "⚪"

        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #1e1e2e, #2a2a3e);
                border-radius: 12px;
                padding: 14px 18px;
                margin-bottom: 10px;
                border-left: 4px solid {net_color};
            ">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="font-size:16px; font-weight:700; color:#ffffff;">
                        👤 {item['name']}
                    </div>
                    <div style="font-size:13px; font-weight:600; color:{net_color};">
                        {net_icon} {net_label}
                    </div>
                </div>
                <div style="display:flex; gap:24px; margin-top:10px;">
                    <div style="background:#1a3a2a; border-radius:8px; padding:6px 14px; text-align:center;">
                        <div style="font-size:11px; color:#2ecc71; letter-spacing:1px;">INCOME</div>
                        <div style="font-size:15px; font-weight:700; color:#ffffff;">₹{item['Income']:,.0f}</div>
                    </div>
                    <div style="background:#3a1a1a; border-radius:8px; padding:6px 14px; text-align:center;">
                        <div style="font-size:11px; color:#e74c3c; letter-spacing:1px;">EXPENSE</div>
                        <div style="font-size:15px; font-weight:700; color:#ffffff;">₹{item['Expense']:,.0f}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

def view_tables():
    categories = requests.get(f"{API_URL}/categories").json()
    categories_df = pd.DataFrame(categories)
    st.write(categories_df)

    friends = requests.get(f"{API_URL}/friends").json()
    friends_df = pd.DataFrame(friends)
    st.write(friends_df)

    transactions = requests.get(f"{API_URL}/transactions").json()
    transactions_df = pd.DataFrame(transactions)
    st.write(transactions_df)

    friends_transactions = requests.get(f"{API_URL}/transactions/friends").json()
    t_df = pd.DataFrame(friends_transactions)
    st.write(t_df)  

    # show_friends_summary()
