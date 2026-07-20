from flask import Flask, request, render_template, redirect, url_for, send_file
import db
from flask_apscheduler import APScheduler
import time
import csv
import os
app = Flask(__name__)
scheduler = APScheduler()


last_day = time.localtime().tm_mday

leaderboard = []

def scheduled_task():

    ret = db.get_state()
    gerstner_hours = ret.get('gerstner_sec', 0)/3600
    total_people_in_shop = ret.get('total_logged_in', 0)
    total_hours = ret.get(ret['current_season'], {}).get('total_hours', 0)
    current_season = ret.get('current_season', '')



    global last_day
    current_day = time.localtime().tm_mday
    if current_day != last_day:
        last_day = current_day
        for user in ret['users']:
            if ret[user]['logged_in']:
                # db.logout_user(ret[user]['username'], ret[user]['pin'])
                db.delete_time(ret[user]['username'], ret[user]['pin'])


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
        gerstner_hours += gerstner_sec_today / 3600

    global leaderboard
    for user in ret['users']:

        leaderboard.append({
            "username": ret[user]['username'],
            "total_hours": ret[user][current_season]['total_hours'],
            "logged_in": ret[user]['logged_in'],
            "activated": ret[user]['activated']
        })

    leaderboard.sort(key=lambda x: x['total_hours'], reverse=True)

    print(f"Current Season: {current_season}")
    print(f"Total Hours: {total_hours:.2f}")
    print(f"Gerstner Hours: {gerstner_hours:.2f}")

    print(f"Gerstner Hours from Log: {ret.get('gerstner_sec', 0)/3600:.2f}")
    print(f"Total People in Shop: {total_people_in_shop}")
    print("Leaderboard:")
    for entry in leaderboard:
        print(f"Username: {entry['username']}, Total Hours: {entry['total_hours']:.2f}, Logged In: {entry['logged_in']}, Activated: {entry['activated']}")
    

    
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


@app.route('/admin', methods=['GET'])
def admin():
    return render_template('admin.html')

def write_csv(csvpath):
    global leaderboard
    filteredBoard = filter(lambda x: x["activated"], leaderboard)
    with open(csvpath, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["Name", "Hours"])
        for user in filteredBoard:
            csvwriter.writerow([user["username"], user["total_hours"]])
    print(f"CSV written to {csvpath}")

@app.route('/admin/export_csv')
def export_csv():
    csvpath = os.path.join(os.getcwd(), './leaderboard.csv')
    write_csv(csvpath)
    return send_file(csvpath, as_attachment=True)

if __name__ == "__main__":
    scheduled_task()
    scheduler.add_job(id='my_background_task', func=scheduled_task, trigger='interval', seconds=60)
    scheduler.start()
    app.run(port=8501,host="0.0.0.0",debug=True,use_reloader=False)
