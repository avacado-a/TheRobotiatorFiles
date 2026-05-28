import streamlit as st
from pages.utils.helpers import get_leaderboard
from streamlit_autorefresh import st_autorefresh

# update every 5 mins
st_autorefresh(interval=5 * 60 * 1000, key="dataframerefresh")

st.title("Shop Time Leaderboard")
leaderboard, time = get_leaderboard()

element_list = []

if leaderboard is None:
    st.error("Not enough people have registered!")
else:
    for i in range(len(leaderboard)):
        message = f"### `#{i+1}` {leaderboard[i]} with {time[i]} hours"

        if i == 0:
            element_list.append(st.success(message))
        elif i == 1:
            element_list.append(st.warning(message))
        elif i == 2:
            element_list.append(st.error(message))
        else:
            element_list.append(st.info(message))
