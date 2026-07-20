from flask import Flask, request, render_template
import db
from flask_apscheduler import APScheduler
import time


    
app = Flask(__name__)
scheduler = APScheduler()




def scheduled_task():
    ret = db.get_state()
    gerstner_hours = ret.get('gerstner_sec', 0)/60
    total_people_in_shop = ret.get('total_logged_in', 0)
    total_hours = ret.get(ret['current_season'], {}).get('total_hours', 0)/60
    current_season = ret.get('current_season', '')

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

    leaderboard = []
    for user in ret['users']:

        leaderboard.append({
            "username": ret[user]['username'],
            "total_hours": ret[user][current_season]['total_hours'],
            "logged_in": ret[user]['logged_in'],
            "activated": ret[user]['activated']
        })

    leaderboard.sort(key=lambda x: x['total_hours'], reverse=True)
    

    
@app.route('/logging', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        pin = request.form['pin']
        state = db.get_state()
        if '1234' not in state:
            db.create_user("Aikam", 1234)
        state = db.get_state()
        if pin in state and not state[pin]['logged_in']:
            db.login_user(state[pin]['username'], pin)
        elif pin in state and state[pin]['logged_in']:
            db.logout_user(state[pin]['username'], pin)
        return render_template('logging.html')
    return render_template('logging.html')


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


if __name__ == "__main__":
    scheduler.add_job(id='my_background_task', func=scheduled_task, trigger='interval', seconds=5)
    scheduler.start()
    app.run(debug=True,use_reloader=False)
