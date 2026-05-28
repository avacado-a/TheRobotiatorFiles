import streamlit as st

from pages.utils.CONFIG import LOGGED_IN_PATH
from pages.utils.helpers import insert_pin, avoid_block_read

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = avoid_block_read(LOGGED_IN_PATH)

st.title("Registration")

with st.form("register_form", clear_on_submit=True):

    name = st.text_input("Your name:")
    pin = st.text_input("Your pin: ")
    submitted = st.form_submit_button("Submit")

    if submitted:
        st.write(insert_pin(pin, name)[1])
