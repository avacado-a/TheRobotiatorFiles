import streamlit as st
from pages.utils.CONFIG import LOGGED_IN_PATH
from pages.utils.helpers import avoid_block_read
# py -m streamlit run C:/Users/timmy/PycharmProjects/AttendanceVK2/Home.py
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = avoid_block_read(LOGGED_IN_PATH)


st.title("Guide")
st.write("""

`Admin` page is password protected. It contains PIN details, the raw attendance data, and the ability to upload that data to the cloud.

`Leaderboard` page contains the top 5 users with the most amount of hours. 

`Logging` page contains the punch in/punch out system. Put the PIN used to register in order to punch in/out.

`Registering` page allows users to register in the system using a PIN and a name. 

`Statistics` page contains statistics about the attendance in the system. 

""")

st.title("FAQ")
st.write("""

### How do I reset the system?
Run init.py to reset all data in the system. Please only do this if necessary and the data being erased is backed up.

### How do I register in the system?
Go to the Registering page and type in your name and your desired PIN. You should be in the system now!

### How do I upload data to Google drive?
Go to the Admin page and type in the administrator password. Go to the "Upload Data to Cloud" section, and type in your email in the text box. Click Upload Data.

### How do I reset my PIN?
Ask a mentor or a member of the leadership team.


""")
