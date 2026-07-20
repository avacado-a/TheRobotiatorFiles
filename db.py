import time


def log_action(username: str, pin: int, action: str):
    with open("db.txt", "a") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S") + "|" + username + "|" + str(pin) + "|" + action + "\n")

def create_user(username: str, pin: int):
    log_action(username, pin, "create")

def login_user(username: str, pin: int):
    log_action(username, pin, "login")

def logout_user(username: str, pin: int ):
    log_action(username, pin, "logout")

def deactivate_user(username: str, pin: int):
    log_action(username, pin, "deactivate")

def activate_user(username: str, pin: int):
    log_action(username, pin, "activate")

def change_pin(username: str, old_pin: int, new_pin: int):
    with open("db.txt", "a") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S") + "|" + username + "|" + str(old_pin) + "|" + "change_pin" + "|" + str(new_pin) + "\n")

def change_season(season: str):
    with open("db.txt", "a") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S") + "|" + "system" + "|" + "-1" + "|" + "change_season" + "|" + season + "\n")

def get_state():
    current_season = ""
    ret = {}
    users = []
    gerstner_hours = 0
    number_logged_in = 0
    with open("db.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            parsedLine = line.strip().split("|")
            if parsedLine[3] == "change_season":
                current_season = parsedLine[4]
                ret[current_season] = {"total_hours":0}
                for user in users:
                    ret[user][current_season] = {"total_hours":0}
            elif parsedLine[3] == "create":
                if parsedLine[2] not in ret:
                    users.append(parsedLine[2])
                    ret[parsedLine[2]] = {"logged_in": False, "pin": parsedLine[2], "username": parsedLine[1], "last_log": None, "activated": True, current_season: {"total_hours":0}}
            elif parsedLine[3] == "login":
                if parsedLine[2] in ret and ret[parsedLine[2]]["activated"] and not ret[parsedLine[2]]["logged_in"]:
                    ret[parsedLine[2]]["last_log"] = parsedLine[0]
                    ret[parsedLine[2]]["logged_in"] = True
                    number_logged_in += 1
                    if number_logged_in == 1:
                        ret[current_season]["first_login"] = parsedLine[0]
            elif parsedLine[3] == "logout":
                if parsedLine[2] in ret and ret[parsedLine[2]]["logged_in"]:
                    start_time = time.mktime(time.strptime(ret[parsedLine[2]]["last_log"], "%Y-%m-%d %H:%M:%S"))
                    end_time = time.mktime(time.strptime(parsedLine[0], "%Y-%m-%d %H:%M:%S"))
                    addedHours = end_time - start_time
                    ret[parsedLine[2]][current_season]["total_hours"] += addedHours / 3600
                    ret[current_season]["total_hours"] += addedHours / 3600
                    ret[parsedLine[2]]["last_log"] = parsedLine[0]
                    ret[parsedLine[2]]["logged_in"] = False
                    number_logged_in -= 1
                    if number_logged_in == 0:
                        gerstner_hours += end_time - time.mktime(time.strptime(ret[current_season]["first_login"], "%Y-%m-%d %H:%M:%S"))
            elif parsedLine[3] == "deactivate":
                if parsedLine[2] in ret and ret[parsedLine[2]]["activated"] and not ret[parsedLine[2]]["logged_in"]:
                    ret[parsedLine[2]]["activated"] = False
            elif parsedLine[3] == "activate":
                if parsedLine[2] in ret and not ret[parsedLine[2]]["activated"]:
                    ret[parsedLine[2]]["activated"] = True
            elif parsedLine[3] == "change_pin":
                if parsedLine[2] in ret and ret[parsedLine[2]]["activated"] and not ret[parsedLine[2]]["logged_in"]:
                    ret[parsedLine[4]] = ret.pop(parsedLine[2])
                    ret[parsedLine[4]]["pin"] = parsedLine[4]
                    users.remove(parsedLine[2])
                    users.append(parsedLine[4])
    ret['users'] = users
    # breakpoint()
    return ret

# change_season("2026Offseason")

