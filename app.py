import streamlit as st
import requests
import pandas as pd
from datetime import date
import plotly.express as px
from create_transaction import *
from manage_categories import manage_categories
from modify_transaction import modify_transactions
from manage_friends import manage_friends
from reports import reports
from db_view import view_tables
from cred import API_URL

API_URL = API_URL
balance_data = requests.get(f"{API_URL}/balance").json()
opening_balance = balance_data.get("Opening_balance")
current_balance = balance_data.get("current_balance")

st.set_page_config(layout="wide")
st.title("💰 Personal Finance Tracker")
st.write(f"Opening Balance : {opening_balance if opening_balance != -1 else 'NOT AVAILABLE'} ")
st.write(f"Current Balance : {current_balance if current_balance != -1 else 'NOT AVAILABLE'} ")


tabs = st.tabs([
    "➕ New Transaction",
    "✏ Edit/Delete Transaction",
    "📂 Manage Categories",
    "👥 Manage Friends",
    "📊 Reports",
    "view tables"
])

# ==============================
# TAB 1 — NEW TRANSACTION
# ==============================
with tabs[0]:
    create_transactions()

# ==============================
# TAB 2 — VIEW TRANSACTIONS
# ==============================
with tabs[1]:
    modify_transactions()

# ==============================
# TAB 3 — MANAGE CATEGORIES
# ==============================
with tabs[2]:
    manage_categories()

# ==============================
# TAB 4 — MANAGE FRIENDS
# ==============================
with tabs[3]:
    manage_friends()

# ==============================
# TAB 5 — REPORTS (BASIC)
# ==============================
with tabs[4]:
    reports()

with tabs[5]:
    view_tables()
