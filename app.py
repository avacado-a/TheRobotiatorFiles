from flask import Flask
import db
from flask_apscheduler import APScheduler
import time
    
app = Flask(__name__)
scheduler = APScheduler()



gerstner_hours = 0
total_people_in_shop = 0
def scheduled_task():
    ret = db.get_state()
    global gerstner_hours
    global total_people_in_shop
    gerstner_hours = ret.get('gerstner_sec', 0)/60
    total_people_in_shop = ret.get('total_logged_in', 0)


    earliest_login_today = None
    anyone_logged_in = False
    for user in ret['users']:
        if ret[user]['logged_in']:
            anyone_logged_in = True
            if earliest_login_today is None or time.mktime(time.strptime(ret[user]["last_log"], "%Y-%m-%d %H:%M:%S")) < earliest_login_today:
                earliest_login_today = time.mktime(time.strptime(ret[user]["last_log"], "%Y-%m-%d %H:%M:%S"))


    if anyone_logged_in:
        current_time = time.time()
        gerstner_sec_today = current_time - earliest_login_today if earliest_login_today else 0
        gerstner_hours += gerstner_sec_today / 60

    


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


if __name__ == "__main__":
    scheduler.add_job(id='my_background_task', func=scheduled_task, trigger='interval', seconds=60)
    scheduler.start()
    app.run(debug=True,use_reloader=False)
