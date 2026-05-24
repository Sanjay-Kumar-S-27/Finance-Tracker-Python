# import streamlit as st
# import requests
# import pandas as pd
# from datetime import date
# from cred import *
# import plotly.express as px

# def manage_categories():
#     st.subheader("Manage Categories")

#     name = st.text_input("Category Name", placeholder="Enter Category Name")
#     type_option = st.selectbox("Type", ["income", "expense"])
#     has_friend = st.checkbox("Requires Friend?")

#     if st.button("Add Category"):
#         payload = {
#             "name": name,
#             "type": type_option,
#             "has_friend": 1 if has_friend else 0
#         }
#         requests.post(f"{API_URL}/categories", json=payload)
#         st.success("Category Added")

#     categories = requests.get(f"{API_URL}/categories").json()
#     income_col, expense_col = st.columns([1,1])
#     with income_col:
#         with st.expander(f"Edit/Delete Income Categories"):
#             for c in categories:
#                 if c.get("type") == "income":
#                     col1, col2 = st.columns([4,1])
#                     col1.write(f"{c.get("name")}")
#                     if col2.button("Delete", key=f"cat{c.get("id")}"):
#                         requests.delete(f"{API_URL}/categories/{c.get("id")}")
#                         st.rerun()
    
#     with expense_col:
#         with st.expander(f"Edit/Delete Expense Categories"):
#             for c in categories:
#                 if c.get("type") == "expense":
#                     col1, col2 = st.columns([4,1])
#                     col1.write(f"{c.get("name")}")
#                     if col2.button("Delete", key=f"cat{c.get("id")}"):
#                         requests.delete(f"{API_URL}/categories/{c.get("id")}")
#                         st.rerun()

import streamlit as st
import requests
from cred import *

# -------------------------------
# EDIT CATEGORY DIALOG
# -------------------------------
@st.dialog("Edit Category")
def edit_category_dialog(category):

    new_name = st.text_input(
        "Category Name",
        value=category["name"]
    )

    col1, col2 = st.columns(2)

    if col1.button("Save"):
        payload = {
            "name": new_name,
            "type": category["type"],          # unchanged
            "has_friend": category["has_friend"]  # unchanged
        }

        requests.put(
            f"{API_URL}/Categories/{category['id']}",
            json=payload
        )

        st.success("Category updated")
        st.session_state.edit_category_id = None
        st.rerun()

    if col2.button("Cancel"):
        st.session_state.edit_category_id = None
        st.rerun()


# -------------------------------
# MAIN FUNCTION
# -------------------------------
def manage_categories():

    st.subheader("Manage Categories")

    # -------------------------------
    # STATE
    # -------------------------------
    if "edit_category_id" not in st.session_state:
        st.session_state.edit_category_id = None

    if "delete_category_id" not in st.session_state:
        st.session_state.delete_category_id = None

    # -------------------------------
    # ADD CATEGORY
    # -------------------------------
    name = st.text_input("Category Name", placeholder="Enter Category Name")
    type_option = st.selectbox("Type", ["income", "expense"])
    has_friend = st.checkbox("Requires Friend?")

    if st.button("Add Category"):
        payload = {
            "name": name,
            "type": type_option,
            "has_friend": 1 if has_friend else 0
        }

        requests.post(f"{API_URL}/categories", json=payload)
        st.success("Category Added")
        st.rerun()

    # -------------------------------
    # FETCH DATA
    # -------------------------------
    categories = requests.get(f"{API_URL}/categories").json()

    income_col, expense_col = st.columns(2)

    # -------------------------------
    # INCOME
    # -------------------------------
    with income_col:
        with st.expander("Income Categories"):

            for c in categories:
                if c["type"] != "income":
                    continue

                col1, col2, col3 = st.columns([4, 1, 1])

                col1.write(c["name"])

                # EDIT
                if col2.button("Edit", key=f"edit_cat_{c['id']}"):
                    st.session_state.edit_category_id = c["id"]

                # DELETE
                if col3.button("Delete", key=f"delete_cat_{c['id']}"):
                    st.session_state.delete_category_id = c["id"]

                # OPEN EDIT DIALOG
                if st.session_state.edit_category_id == c["id"]:
                    edit_category_dialog(c)

                # DELETE CONFIRM
                if st.session_state.delete_category_id == c["id"]:
                    st.warning("Delete this category?")
                    c1, c2 = st.columns(2)

                    if c1.button("Yes", key=f"yes_del_cat_{c['id']}"):
                        requests.delete(f"{API_URL}/categories/{c['id']}")
                        st.success("Deleted")
                        st.session_state.delete_category_id = None
                        st.rerun()

                    if c2.button("Cancel", key=f"cancel_del_cat_{c['id']}"):
                        st.session_state.delete_category_id = None

    # -------------------------------
    # EXPENSE
    # -------------------------------
    with expense_col:
        with st.expander("Expense Categories"):

            for c in categories:
                if c["type"] != "expense":
                    continue

                col1, col2, col3 = st.columns([4, 1, 1])

                col1.write(c["name"])

                # EDIT
                if col2.button("Edit", key=f"edit_cat_{c['id']}"):
                    st.session_state.edit_category_id = c["id"]

                # DELETE
                if col3.button("Delete", key=f"delete_cat_{c['id']}"):
                    st.session_state.delete_category_id = c["id"]

                # OPEN EDIT DIALOG
                if st.session_state.edit_category_id == c["id"]:
                    edit_category_dialog(c)

                # DELETE CONFIRM
                if st.session_state.delete_category_id == c["id"]:
                    st.warning("Delete this category?")
                    c1, c2 = st.columns(2)

                    if c1.button("Yes", key=f"yes_del_cat_{c['id']}"):
                        requests.delete(f"{API_URL}/categories/{c['id']}")
                        st.success("Deleted")
                        st.session_state.delete_category_id = None
                        st.rerun()

                    if c2.button("Cancel", key=f"cancel_del_cat_{c['id']}"):
                        st.session_state.delete_category_id = None
