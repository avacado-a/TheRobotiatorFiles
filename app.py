from flask import Flask
import db
from flask_apscheduler import APScheduler
import time
    
app = Flask(__name__)
scheduler = APScheduler()

def scheduled_task():
    ret = db.get_state()
    gerstner_hours_today = 0


    earliest_login_today = None
    anyone_logged_in = False
    for user in ret['users']:
        if user['logged_in']:
            anyone_logged_in = True
            if earliest_login_today is None or time.mktime(time.strptime(user["last_log"], "%Y-%m-%d %H:%M:%S")) < earliest_login_today:
                earliest_login_today = time.mktime(time.strptime(user["last_log"], "%Y-%m-%d %H:%M:%S"))


    if not anyone_logged_in:
        latest_logout_time = None
        for user in ret['users']:
            if user["last_log"] is not None:
                logout_time = time.mktime(time.strptime(user["last_log"], "%Y-%m-%d %H:%M:%S"))
                if latest_logout_time is None or logout_time > latest_logout_time:
                    latest_logout_time = logout_time
        gerstner_hours_today = latest_logout_time - earliest_login_today if latest_logout_time and earliest_login_today else 0
    else:
        current_time = time.time()
        gerstner_hours_today = current_time - earliest_login_today if earliest_login_today else 0


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


if __name__ == "__main__":
    scheduler.add_job(id='my_background_task', func=scheduled_task, trigger='interval', seconds=5)
    scheduler.start()
    app.run(debug=True,use_reloader=False)
