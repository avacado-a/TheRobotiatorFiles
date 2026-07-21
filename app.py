from flask import Flask, request, render_template, redirect, url_for, send_file, jsonify, session
import db
from flask_apscheduler import APScheduler
import time
import csv
import os
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = "robotiators_secret_key_888"
socketio = SocketIO(app, cors_allowed_origins="*")
scheduler = APScheduler()

# Global variables for caching state to be pushed to pages
last_day = time.localtime().tm_mday
leaderboard_data = []
stats_data = {}

def scheduled_task():
    global last_day, leaderboard_data, stats_data
    try:
        ret = db.get_state()
    except Exception as e:
        print(f"Error reading database state: {e}")
        return

    current_season = ret.get('current_season', '')
    total_people_in_shop = ret.get('total_logged_in', 0)
    total_hours = ret.get(current_season, {}).get('total_hours', 0) if current_season else 0
    gerstner_hours = ret.get('gerstner_sec', 0) / 3600

    # Auto logout check at midnight
    current_day = time.localtime().tm_mday
    if current_day != last_day:
        last_day = current_day
        for user in ret.get('users', []):
            if ret.get(user, {}).get('logged_in', False):
                try:
                    db.delete_time(ret[user]['username'], ret[user]['pin'])
                except Exception as e:
                    print(f"Error auto-logging out user {user}: {e}")
        try:
            ret = db.get_state()
            current_season = ret.get('current_season', '')
            total_people_in_shop = ret.get('total_logged_in', 0)
            total_hours = ret.get(current_season, {}).get('total_hours', 0) if current_season else 0
            gerstner_hours = ret.get('gerstner_sec', 0) / 3600
        except Exception as e:
            print(f"Error re-fetching state: {e}")

    earliest_login_today = None
    anyone_logged_in = False
    logged_in_users = []

    for user in ret.get('users', []):
        user_info = ret.get(user, {})
        if user_info.get('logged_in', False):
            anyone_logged_in = True
            last_log_str = user_info.get("last_log")
            if last_log_str:
                try:
                    log_time = time.mktime(time.strptime(last_log_str, "%Y-%m-%d %H:%M:%S"))
                    if earliest_login_today is None or log_time < earliest_login_today:
                        earliest_login_today = log_time
                    logged_in_users.append({
                        "username": user_info['username'],
                        "login_time": last_log_str
                    })
                except Exception as e:
                    print(f"Error parsing log time for user {user}: {e}")

    if anyone_logged_in:
        current_time = time.time()
        gerstner_sec_today = current_time - earliest_login_today if earliest_login_today else 0
        gerstner_hours += gerstner_sec_today / 3600

    new_leaderboard = []
    for user in ret.get('users', []):
        user_info = ret.get(user, {})
        user_season_data = user_info.get(current_season, {})
        new_leaderboard.append({
            "username": user_info.get('username', user),
            "pin": user_info.get('pin', user),
            "total_hours": user_season_data.get('total_hours', 0) if user_season_data else 0,
            "logged_in": user_info.get('logged_in', False),
            "activated": user_info.get('activated', True)
        })

    # Sort descending by hours
    new_leaderboard.sort(key=lambda x: x['total_hours'], reverse=True)
    leaderboard_data = new_leaderboard

    stats_data = {
        "current_season": current_season,
        "total_hours": total_hours,
        "gerstner_hours": gerstner_hours,
        "total_people_in_shop": total_people_in_shop,
        "logged_in_users": logged_in_users,
        "total_users": len(ret.get('users', []))
    }

    # Broadcast updates to active websocket connections
    socketio.emit('state_update', {
        "stats": stats_data,
        "leaderboard": leaderboard_data
    })

def update_and_broadcast():
    """Runs scheduled_task sync to update global state and broadcast via SocketIO immediately."""
    scheduled_task()

@app.route('/')
def home():
    # Make sure we have latest data
    if not stats_data:
        scheduled_task()
    return render_template('home.html', stats=stats_data, leaderboard=leaderboard_data)

@app.route('/kiosk')
def kiosk():
    # Dedicated dashboard page for live shop kiosk/display
    if not stats_data:
        scheduled_task()
    return render_template('kiosk.html', stats=stats_data, leaderboard=leaderboard_data)

@app.route('/logging', methods=['GET', 'POST'])
def logging():
    message = None
    success = False
    if request.method == 'POST':
        pin = request.form.get('pin', '').strip()
        state = db.get_state()
        if pin in state:
            user = state[pin]
            if not user.get('activated', True):
                message = f"❌ Account for {user['username']} is deactivated. Please contact an admin."
            elif not user['logged_in']:
                db.login_user(user['username'], pin)
                message = f"⚡ Welcome back, {user['username']}! Logged in successfully."
                success = True
                update_and_broadcast()
            else:
                db.logout_user(user['username'], pin)
                message = f"👋 See you later, {user['username']}! Logged out successfully."
                success = True
                update_and_broadcast()
        else:
            message = "❌ Invalid PIN. Please try again or register."
    return render_template('logging.html', message=message, success=success)

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    message = None
    success = False
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        pin = request.form.get('pin', '').strip()
        if not username or not pin:
            message = "❌ Both Name and PIN are required."
        elif not pin.isdigit() or len(pin) < 4:
            message = "❌ PIN must be at least 4 digits (numbers only)."
        else:
            state = db.get_state()
            if pin not in state:
                db.create_user(username, pin)
                message = f"🎉 Welcome aboard, {username}! Registered successfully. Go to Logging to check in."
                success = True
                update_and_broadcast()
            else:
                message = "❌ This PIN is already taken. Please choose a different one."
    return render_template('registration.html', message=message, success=success)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        admin_pin = request.form.get('admin_pin', '').strip()
        if admin_pin == "RobotiatorFiles888":
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('admin.html', error="Invalid Admin PIN")

    if not session.get('admin_logged_in', False):
        return render_template('admin.html', needs_login=True)

    # Calculate statistics and fetch user states
    if not stats_data:
        scheduled_task()

    # Load system logs from db.txt
    logs = []
    if os.path.exists("db.txt"):
        with open("db.txt", "r") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) >= 4:
                    logs.append({
                        "timestamp": parts[0],
                        "username": parts[1],
                        "pin": parts[2],
                        "action": parts[3],
                        "extra": parts[4] if len(parts) > 4 else ""
                    })
    logs.reverse() # Newest first

    return render_template(
        'admin.html',
        needs_login=False,
        stats=stats_data,
        leaderboard=leaderboard_data,
        logs=logs[:100] # Limit to latest 100 entries for performance
    )

@app.route('/admin/logout')
def admin_logout():
    session['admin_logged_in'] = False
    return redirect(url_for('admin'))

@app.route('/admin/change_season', methods=['POST'])
def admin_change_season():
    if not session.get('admin_logged_in', False):
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    season_name = request.form.get('season_name', '').strip()
    if season_name:
        db.change_season(season_name)
        update_and_broadcast()
        return redirect(url_for('admin'))
    return "Invalid season name", 400

@app.route('/admin/toggle_user', methods=['POST'])
def admin_toggle_user():
    if not session.get('admin_logged_in', False):
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    username = request.form.get('username')
    pin = request.form.get('pin')
    action = request.form.get('action') # 'activate' or 'deactivate'
    
    if username and pin:
        if action == 'activate':
            db.activate_user(username, pin)
        elif action == 'deactivate':
            db.deactivate_user(username, pin)
        update_and_broadcast()
        return redirect(url_for('admin'))
    return "Missing user info", 400

@app.route('/admin/change_pin', methods=['POST'])
def admin_change_pin():
    if not session.get('admin_logged_in', False):
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    username = request.form.get('username')
    old_pin = request.form.get('old_pin')
    new_pin = request.form.get('new_pin')
    
    if username and old_pin and new_pin:
        # Check if new pin is already taken
        state = db.get_state()
        if new_pin in state:
            return "Error: New PIN is already in use by another user.", 400
        db.change_pin(username, old_pin, new_pin)
        update_and_broadcast()
        return redirect(url_for('admin'))
    return "Missing PIN change arguments", 400

@app.route('/admin/delete_time', methods=['POST'])
def admin_delete_time():
    """Forces logout/delete time for a user (gives 0.5hr login credit and logs out)."""
    if not session.get('admin_logged_in', False):
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    username = request.form.get('username')
    pin = request.form.get('pin')
    if username and pin:
        db.delete_time(username, pin)
        update_and_broadcast()
        return redirect(url_for('admin'))
    return "Missing user arguments", 400

def write_csv(csvpath):
    # Make sure we have latest leaderboard data
    scheduled_task()
    filteredBoard = filter(lambda x: x["activated"], leaderboard_data)
    with open(csvpath, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["Name", "Hours"])
        for user in filteredBoard:
            csvwriter.writerow([user["username"], f"{user['total_hours']:.2f}"])
    print(f"CSV written to {csvpath}")

@app.route('/admin/export_csv')
def export_csv():
    if not session.get('admin_logged_in', False):
        return "Unauthorized", 403
    csvpath = os.path.join(os.getcwd(), 'leaderboard.csv')
    write_csv(csvpath)
    return send_file(csvpath, as_attachment=True)

if __name__ == "__main__":
    scheduled_task()
    scheduler.add_job(id='my_background_task', func=scheduled_task, trigger='interval', seconds=15)
    scheduler.start()
    socketio.run(app, port=8501, host="0.0.0.0", debug=True, use_reloader=False)