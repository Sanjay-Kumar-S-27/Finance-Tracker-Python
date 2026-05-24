import streamlit as st
import requests
import pandas as pd
from datetime import date
from cred import *
import plotly.express as px
import datetime

# def reports():
#     st.subheader("Basic Reports")

#     data = requests.get(f"{API_URL}/transactions").json()

#     if data:
#         # df = pd.DataFrame(data, columns=[
#         #     "ID", "Date", "Category", "Type", "Amount", "Note"
#         # ])
#         df = pd.DataFrame(data)

#         pie = px.pie(df, names="name", values="amount", title="Category Distribution")
#         st.plotly_chart(pie, use_container_width=True)

#         bar = px.bar(df, x="name", y="amount", title="Category vs Amount")
#         st.plotly_chart(bar, use_container_width=True)

#         st.dataframe(df)
#     else:
#         st.info("No data available")

def reports():
    st.subheader("Basic Reports")

    # -------------------------------
    # DATE FILTER
    # -------------------------------
    today = datetime.date.today()
    default_start = today - datetime.timedelta(days=30)

    if "report_start_date" not in st.session_state:
        st.session_state.report_start_date = default_start
    if "report_end_date" not in st.session_state:
        st.session_state.report_end_date = today

    def on_report_start_change():
        new_start = st.session_state.report_start_date
        if (st.session_state.report_end_date - new_start).days > 30:
            st.session_state.report_end_date = new_start + datetime.timedelta(days=30)

    def on_report_end_change():
        new_end = st.session_state.report_end_date
        if (new_end - st.session_state.report_start_date).days > 30:
            st.session_state.report_start_date = new_end - datetime.timedelta(days=30)

    col_start, col_end = st.columns(2)

    with col_start:
        st.date_input(
            "Start Date",
            key="report_start_date",
            on_change=on_report_start_change
        )

    with col_end:
        st.date_input(
            "End Date",
            key="report_end_date",
            on_change=on_report_end_change
        )

    start_date = st.session_state.report_start_date
    end_date = st.session_state.report_end_date

    # -------------------------------
    # FETCH & DISPLAY
    # -------------------------------
    data = requests.get(
        f"{API_URL}/transactions",
        params={"start_date": str(start_date), "end_date": str(end_date)}
    ).json()

    if data:
        df = pd.DataFrame(data)

        pie = px.pie(df, names="name", values="amount", title="Category Distribution")
        st.plotly_chart(pie, use_container_width=True)

        bar = px.bar(df, x="name", y="amount", title="Category vs Amount")
        st.plotly_chart(bar, use_container_width=True)

        st.dataframe(df)
    else:
        st.info("No data available")
