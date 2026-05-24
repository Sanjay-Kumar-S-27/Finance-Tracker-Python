import streamlit as st
import requests
import pandas as pd
from cred import *
import datetime

# -------------------------------
# EDIT DIALOG
# -------------------------------
@st.dialog("Edit Transaction")
def edit_transaction(row, category_dict):

    new_date = st.date_input(
        "Date",
        value=pd.to_datetime(row["date"])
    )

    category_keys = list(category_dict.keys())
    default_category = f"{row['name']} ({row['type']})"

    new_category = st.selectbox(
        "Category",
        category_keys,
        index=category_keys.index(default_category)
    )

    new_amount = st.number_input(
        "Amount",
        value=float(row["amount"])
    )

    new_note = st.text_input(
        "Note",
        value=row["note"] or ""
    )

    category_data = category_dict[new_category]
    friend_id = None

    # Handle friend selection
    if category_data.get("has_friend") == 1:
        friends = requests.get(f"{API_URL}/friends").json()
        friend_dict = {f["name"]: f["id"] for f in friends}

        res = requests.get(f"{API_URL}/friends/transactions/{row['id']}")
        friend_name = res.json().get("friend") if res.status_code == 200 else None

        selected_friend = st.selectbox(
            "Select Friend",
            list(friend_dict.keys()),
            index=list(friend_dict.keys()).index(friend_name)
        )
        friend_id = friend_dict[selected_friend]

    col1, col2 = st.columns(2)

    if col1.button("Save"):
        payload = {
            "date": str(new_date),
            "category_id": category_data["id"],
            "amount": new_amount,
            "note": new_note,
            "friend_id": friend_id
        }

        requests.put(
            f"{API_URL}/transactions/{row['id']}",
            json=payload
        )

        st.success("Updated successfully")
        st.session_state.editing_id = None
        st.rerun()

    if col2.button("Cancel"):
        st.session_state.editing_id = None
        st.rerun()


# -------------------------------
# MAIN FUNCTION
# -------------------------------
def modify_transactions():

    st.subheader("Edit / Delete Transactions")

    # Track which row is being edited
    if "editing_id" not in st.session_state:
        st.session_state.editing_id = None

    if "delete_confirm_id" not in st.session_state:
        st.session_state.delete_confirm_id = None

    # -------------------------------
    # DATE FILTER
    # -------------------------------
    today = datetime.date.today()
    default_start = today - datetime.timedelta(days=30)

    # Initialize session state
    if "filter_start_date" not in st.session_state:
        st.session_state.filter_start_date = default_start
    if "filter_end_date" not in st.session_state:
        st.session_state.filter_end_date = today

    def on_start_change():
        new_start = st.session_state.filter_start_date
        if (st.session_state.filter_end_date - new_start).days > 30:
            st.session_state.filter_end_date = new_start + datetime.timedelta(days=30)

    def on_end_change():
        new_end = st.session_state.filter_end_date
        if (new_end - st.session_state.filter_start_date).days > 30:
            st.session_state.filter_start_date = new_end - datetime.timedelta(days=30)

    col_start, col_end = st.columns(2)

    with col_start:
        st.date_input(
            "Start Date",
            key="filter_start_date",
            on_change=on_start_change
        )

    with col_end:
        st.date_input(
            "End Date",
            key="filter_end_date",
            on_change=on_end_change
        )

    start_date = st.session_state.filter_start_date
    end_date = st.session_state.filter_end_date

    # Fetch data
    data = requests.get(
        f"{API_URL}/transactions",
        params={"start_date": str(start_date), "end_date": str(end_date)}
    ).json()

    if not data:
        st.info("No transactions found")
        return

    df = pd.DataFrame(data)

    categories = requests.get(f"{API_URL}/categories").json()
    category_dict = {
        f"{c['name']} ({c['type']})": c for c in categories
    }

    # -------------------------------
    # LOOP THROUGH ROWS
    # -------------------------------
    for _, row in df.iterrows():

        with st.container(border=True):
            col1, col2, col3 = st.columns([5, 2, 2])
            res = requests.get(f"{API_URL}/friends/transactions/{row['id']}")
            friend_name = res.json().get("friend") if res.status_code == 200 else None
            # st.write(friend_name)
            with col1:
                st.write(f"📅 {row['date']}")
                st.write(f"📂 {row['name']} {"- " + friend_name if friend_name else ''}")
                st.write(f"💰 {row['amount']}")

            # -------------------
            # EDIT BUTTON
            # -------------------
            if col2.button("Edit", key=f"edit_{row['id']}"):
                st.session_state.editing_id = row["id"]

            # -------------------
            # DELETE BUTTON
            # -------------------
            if col3.button("Delete", key=f"delete_{row['id']}"):
                st.session_state.delete_confirm_id = row["id"]

        # -------------------------------
        # OPEN EDIT DIALOG (ONLY FOR MATCHING ROW)
        # -------------------------------
        if st.session_state.editing_id == row["id"]:
            edit_transaction(row, category_dict)

        # -------------------------------
        # DELETE CONFIRMATION
        # -------------------------------
        if st.session_state.delete_confirm_id == row["id"]:
            st.error("Are you sure you want to delete?")
            c1, c2 = st.columns(2)

            if c1.button("Yes", key=f"yes_del_{row['id']}"):
                requests.delete(f"{API_URL}/transactions/{row['id']}")
                st.success("Deleted successfully")

                st.session_state.delete_confirm_id = None
                st.rerun()

            if c2.button("Cancel", key=f"cancel_del_{row['id']}"):
                st.session_state.delete_confirm_id = None


            # with st.expander(f"Transaction ID: {row['id']}"):

            #     new_date = st.date_input(
            #         "Date",
            #         value=pd.to_datetime(row["date"]),
            #         key=f"date{row['id']}"
            #     )

            #     new_category = st.selectbox(
            #         "Category",
            #         list(category_dict.keys()),
            #         index=list(category_dict.keys()).index(row["name"]),
            #         key=f"new_cat{row['id']}"
            #     )

            #     new_amount = st.number_input(
            #         "Amount",
            #         value=float(row["amount"]),
            #         key=f"amt{row['id']}"
            #     )

            #     new_note = st.text_input(
            #         "Note",
            #         value=row["note"] if row["note"] else "",
            #         key=f"note{row['id']}"
            #     )

            #     col1, col2 = st.columns(2)

            #     # SAVE BUTTON
            #     if col1.button("Save", key=f"save{row['id']}"):
            #         st.session_state[f"confirm_edit_{row['id']}"] = True

            #     # DELETE BUTTON
            #     if col2.button("Delete", key=f"delete{row['id']}"):
            #         st.session_state[f"confirm_delete_{row['id']}"] = True

            #     # ------------------------
            #     # CONFIRM EDIT
            #     # ------------------------
            #     if st.session_state.get(f"confirm_edit_{row['id']}"):
            #         st.warning("Are you sure you want to save changes?")
            #         c1, c2 = st.columns(2)

            #         if c1.button("Yes", key=f"yes_edit{row['id']}"):

            #             payload = {
            #                 "date": str(new_date),
            #                 "category_id": category_dict[new_category],
            #                 "amount": new_amount,
            #                 "note": new_note,
            #                 "friend_id": None
            #             }

            #             requests.put(
            #                 f"{API_URL}/transactions/{row['id']}",
            #                 json=payload
            #             )

            #             st.success("Updated successfully")
            #             st.session_state[f"confirm_edit_{row['id']}"] = False
            #             st.rerun()

            #         if c2.button("Cancel", key=f"cancel_edit{row['id']}"):
            #             st.session_state[f"confirm_edit_{row['id']}"] = False

            #     # ------------------------
            #     # CONFIRM DELETE
            #     # ------------------------
            #     if st.session_state.get(f"confirm_delete_{row['id']}"):
            #         st.error("Are you sure you want to delete?")
            #         c1, c2 = st.columns(2)

            #         if c1.button("Yes", key=f"yes_del{row['id']}"):

            #             requests.delete(f"{API_URL}/transactions/{row['id']}")
            #             st.success("Deleted successfully")

            #             st.session_state[f"confirm_delete_{row['id']}"] = False
            #             st.rerun()

            #         if c2.button("Cancel", key=f"cancel_del{row['id']}"):
            #             st.session_state[f"confirm_delete_{row['id']}"] = False

    # else:
    #     st.info("No transactions found")
