import dlib
import sys
import streamlit as st

if not hasattr(st, "rerun"):
    st.rerun = st.experimental_rerun

# Import streamlit CLI
try:
    from streamlit.web import cli as stcli
except ImportError:
    from streamlit import cli as stcli

if __name__ == "__main__":
    sys.argv = ["streamlit", "run", "Home.py"] + sys.argv[1:]
    sys.exit(stcli.main())
