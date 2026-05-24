# import streamlit as st
# import requests
# import pandas as pd
# from datetime import date
# from cred import *
# import plotly.express as px

# # @st.dialog("Confirmation")
# # def confirmation():

# @st.dialog("Edit Friend")
# def edit_friends(f):
#     new_name = st.text_input(
#         "Change Name",
#         value=f.get("name"),
#         key=f"new_name_{f.get("id")}"
#     )
#     col1,col2 = st.columns(2)
#     if col1.button("Save", key=f"save_friend_{f.get("id")}"):
#         # st.session_state[f"confirm_edit_f{f['id']}"] = True
#         # payload = st.session_state.payload
#         requests.put(
#             f"{API_URL}/friends/{f['id']}",
#             json={"name": new_name}
#         )
#         st.session_state.edit_friend = False
#         st.rerun()
#     if col2.button("Cancel", key=f"cancel_friend_{f.get("id")}"):
#         st.session_state.edit_friend = False
#         st.rerun()


# def manage_friends():
#     if "edit_friend" not in st.session_state:
#         st.session_state.edit_friend = False
#     st.subheader("Manage Friends")

#     friend_name = st.text_input("Friend Name", placeholder="Enter Friend Name") 

#     if st.button("Add Friend"):
#         requests.post(f"{API_URL}/friends", json={"name": friend_name})
#         st.success("Friend Added")

#     friends = requests.get(f"{API_URL}/friends").json()
#     for f in friends:
#         col1, col2, col3 = st.columns([3,1,1])
#         col1.write(f.get("name"))
#         if col2.button("Edit", key=f"edit_friend_{f.get("id")}"):
#             st.session_state.edit_friend = True
#         if col3.button("Delete", key=f"friend{f.get("id")}"):
#             requests.delete(f"{API_URL}/friends/{f.get("id")}")
#             st.rerun()

#         if st.session_state.edit_friend:
#             edit_friends(f)

import streamlit as st
import requests
from cred import *

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

# -------------------------------
# EDIT FRIEND DIALOG
# -------------------------------
@st.dialog("Edit Friend")
def edit_friend_dialog(friend):

    new_name = st.text_input(
        "Change Name",
        value=friend["name"]
    )

    col1, col2 = st.columns(2)

    if col1.button("Save"):
        requests.put(
            f"{API_URL}/friends/{friend['id']}",
            json={"name": new_name}
        )

        st.success("Friend updated")
        st.session_state.edit_friend_id = None
        st.rerun()

    if col2.button("Cancel"):
        st.session_state.edit_friend_id = None
        st.rerun()


# -------------------------------
# MAIN FUNCTION
# -------------------------------
def manage_friends():

    st.subheader("Manage Friends")

    # -------------------------------
    # STATE
    # -------------------------------
    if "edit_friend_id" not in st.session_state:
        st.session_state.edit_friend_id = None

    if "delete_friend_id" not in st.session_state:
        st.session_state.delete_friend_id = None

    # -------------------------------
    # ADD FRIEND
    # -------------------------------
    friend_name = st.text_input(
        "Friend Name",
        placeholder="Enter Friend Name"
    )

    if st.button("Add Friend"):
        requests.post(
            f"{API_URL}/friends",
            json={"name": friend_name}
        )
        st.success("Friend Added")
        st.rerun()

    with st.expander("Edit/Delete Friends"):

        # -------------------------------
        # FETCH DATA
        # -------------------------------
        friends = requests.get(f"{API_URL}/friends").json()

        if not friends:
            st.info("No friends found")
            return

        # -------------------------------
        # LIST FRIENDS
        # -------------------------------
        for f in friends:

            col1, col2, col3 = st.columns([3, 1, 1])

            col1.write(f["name"])

            # EDIT
            if col2.button("Edit", key=f"edit_friend_{f['id']}"):
                st.session_state.edit_friend_id = f["id"]

            # DELETE
            if col3.button("Delete", key=f"delete_friend_{f['id']}"):
                st.session_state.delete_friend_id = f["id"]

            # -------------------------------
            # OPEN EDIT DIALOG
            # -------------------------------
            if st.session_state.edit_friend_id == f["id"]:
                edit_friend_dialog(f)

            # -------------------------------
            # DELETE CONFIRMATION
            # -------------------------------
            if st.session_state.delete_friend_id == f["id"]:
                st.warning("Delete this friend?")
                c1, c2 = st.columns(2)

                if c1.button("Yes", key=f"yes_del_friend_{f['id']}"):
                    requests.delete(f"{API_URL}/friends/{f['id']}")
                    st.success("Deleted successfully")

                    st.session_state.delete_friend_id = None
                    st.rerun()

                if c2.button("Cancel", key=f"cancel_del_friend_{f['id']}"):
                    st.session_state.delete_friend_id = None
    
    with st.expander("Friends Summary"):
        show_friends_summary()