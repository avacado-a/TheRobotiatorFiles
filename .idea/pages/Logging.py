import streamlit as st
from pages.utils.helpers import get_name, avoid_block_write, insert_to_csv, avoid_block_read
from pages.utils.CONFIG import LOGGED_IN_PATH, LOG_PATH
from datetime import datetime as dt

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = avoid_block_read(LOGGED_IN_PATH)
if "refresh" not in st.session_state:
    st.session_state["refresh"] = True

st.title("Punch In and Punch Out")
with st.form("log_form", clear_on_submit=True):
    pin_inp = st.text_input("Enter your PIN:", type="password")
    submitted = st.form_submit_button("Submit")

    if submitted:

        if not get_name(pin_inp)[0]:
            st.write("Invalid PIN.")
        else:
            pin_log = pin_inp

            # Raw log used for debug data
            with open(LOG_PATH, "a") as f:
                f.write(f"\nLogged {get_name(pin_log)} at {dt.utcnow()}")

            if pin_log in st.session_state["logged_in"]:
                if dt.utcnow().day != st.session_state["logged_in"][pin_log].day:
                    message = "Forgot to logout, defaulting to 30 minutes"
                    total_hours = 0.5
                else:
                    total_hours = (dt.utcnow() - st.session_state["logged_in"][pin_log]).seconds / 3600
                    message = f"Logged out {get_name(pin_log)} at {dt.now()}"
                    st.write(message)
                del st.session_state["logged_in"][pin_log]
                insert_to_csv(get_name(pin_log), total_hours)
            else:
                st.session_state["logged_in"][pin_log] = dt.utcnow()
                message = f"Logged in {get_name(pin_log)} at {dt.now()}"
                st.write(message)

            avoid_block_write(LOGGED_IN_PATH, st.session_state["logged_in"])
            st.session_state["refresh"] = True
