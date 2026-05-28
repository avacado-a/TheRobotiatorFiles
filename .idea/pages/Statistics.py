import streamlit as st
from pages.utils.CONFIG import LOGGED_IN_PATH, GOAL
from pages.utils.helpers import calculate_metrics, avoid_block_read
from streamlit_autorefresh import st_autorefresh

# update every 5 mins
st_autorefresh(interval=5 * 60 * 1000, key="dataframerefresh")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = avoid_block_read(LOGGED_IN_PATH)

weekly, daily = calculate_metrics()
total_hours = int(weekly["total"])
total_minutes = int((weekly["total"] - total_hours) * 60)

st.markdown(f"<h1 style='text-align: center; font-size: 1000%;'>{total_hours} hrs</h1>", unsafe_allow_html=True)
st.markdown(f"<h1 style='text-align: center; font-size: 1000%;'>{total_minutes} mins</h1>", unsafe_allow_html=True)

st.write("")
st.write("")
st.write("")

if total_hours == GOAL:
    st.balloons()

placeholder = st.empty()
with placeholder.expander(label="", expanded=True):

    delta_week = int(weekly['current_week']) - int(weekly['last_week'])
    delta_day = int(daily['current_day']) - int(daily["last_day"])
    delta_max = int(weekly['max']) - int(weekly['last_max'])
    delta_average = int(weekly["average"]) - int(weekly["last_average"])
    col1, col2, col3 = st.columns(3)
    col1.metric("This Week's Shop Time", f"{int(weekly['current_week'])} hrs", f"{delta_week} hrs since last week")
    col2.metric("People in Shop", f"{len(st.session_state.logged_in.keys())} people")
    col3.metric("Today's Shop Time", f"{int(daily['current_day'])} hrs", f"{delta_day} hrs since yesterday")

    col4, col5, col6 = st.columns(3)
    col4.metric("Distance to Goal", f"{abs(GOAL - total_hours)} hrs")
    col5.metric("Max Hours this Week", f"{int(weekly['max'])} hrs", f"{delta_max} hrs since last week")
    col6.metric("Average Hours this Week", f"{int(weekly['average'])} hrs", f"{delta_average} hrs since last week")