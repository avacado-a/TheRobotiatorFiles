import json
import streamlit as st
from pages.utils.CONFIG import ADMIN_PW, WEEKLY_PATH, DAILY_PATH, LOGGED_IN_PATH, PIN_PATH
from passlib.hash import pbkdf2_sha256
from pages.utils.helpers import avoid_block_pandas_read, avoid_block_read, upload_data
from streamlit_autorefresh import st_autorefresh

# Require admin password every 5 minutes
st_autorefresh(interval=5 * 60 * 1000, key="dataframerefresh")

st.title("Admin Page")

def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if pbkdf2_sha256.verify(st.session_state["password"], ADMIN_PW):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = True

    # Return True if the passward is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Please enter the administrator password to view this page:",
        type="password",
        on_change=password_entered,
        key="password"
    )

    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
        return False


if not check_password():
    st.stop()

with st.form("upload_form"):
    st.subheader("Upload Data to Cloud")



    share_with = st.text_input("Share with Who? Format it in a list form: me@gmail.com,you@yahoo.com,him@gmail.com")
    submit_btn = st.form_submit_button("Upload Data")

    if submit_btn:
        share_with = share_with.split(",")
        try:
            upload_data(share_with)
            st.success("Data sucessfully uploaded!")
        except Exception as e:
            st.error(e)

# TODO Finish PIN reset
# with st.form("pin_reset_form"):
#     st.subheader("Reset a PIN")
#     current = st.text_input("Current PIN")
#     new = st.text_input("New PIN")
#     submit_btn = st.form_submit_button("Reset")
#
#     if submit_btn:
#         pass

with st.expander("Raw CSV data"):
    st.subheader("Weekly Raw Data")
    st.write(avoid_block_pandas_read(WEEKLY_PATH))

    st.subheader("Daily Raw Data")
    st.write(avoid_block_pandas_read(DAILY_PATH))

with st.expander("PIN data"):
    st.subheader("PIN Data")
    with open(PIN_PATH, "r") as f:
        st.write(json.load(f))

with st.expander("Logged in Data"):
    st.subheader("Currently Logged In Data")
    st.write(avoid_block_read(LOGGED_IN_PATH))

