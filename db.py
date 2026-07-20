import time

def init_db():
    open("db.txt", "w").close()

def log_action(username: str, pin: str, action: str):
    with open("db.txt", "a") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S") + "|" + username + "|" + pin + "|" + action + "\n")

def create_user(username: str, pin: str):
    log_action(username, pin, "create")

def login_user(username: str, pin: str):
    log_action(username, pin, "login")

def logout_user(username: str, pin: str):
    log_action(username, pin, "logout")

def deactivate_user(username: str, pin: str):
    log_action(username, pin, "deactivate")

def activate_user(username: str, pin: str):
    log_action(username, pin, "activate")