from flask import Flask, request, render_template, redirect, url_for
import db
from flask_apscheduler import APScheduler
import time
    
app = Flask(__name__)
scheduler = APScheduler()



gerstner_hours = 0
def scheduled_task():
    ret = db.get_state()
    global gerstner_hours
    gerstner_hours = ret.get('gerstner_sec', 0)/60


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

    
@app.route('/logging', methods=['GET', 'POST'])
def logging():
    if request.method == 'POST':
        pin = request.form['pin']
        state = db.get_state()
        if pin in state and not state[pin]['logged_in']:
            db.login_user(state[pin]['username'], pin)
        elif pin in state and state[pin]['logged_in']:
            db.logout_user(state[pin]['username'], pin)
    return render_template('logging.html')

@app.route("/logging.html")
def logging_redirect():
    return redirect(url_for('logging'))

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        username = request.form['username']
        pin = request.form['pin'] # Make sure this is a 4 digit or longer positive pin
        state = db.get_state()
        if pin not in state:
            db.create_user(username, pin)
    return render_template('registration.html')

@app.route("/registration.html")
def registration_redirect():
    return redirect(url_for('registration'))

@app.route("/")
def root_redirect():
    return redirect(url_for('logging'))


if __name__ == "__main__":
    scheduler.add_job(id='my_background_task', func=scheduled_task, trigger='interval', seconds=60)
    scheduler.start()
    app.run(debug=True,use_reloader=False)
