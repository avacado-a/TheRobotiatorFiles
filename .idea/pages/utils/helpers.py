from pages.utils.CONFIG import WEEKLY_PATH, DAILY_PATH, PIN_PATH, LAST_UPDATE_PATH, LOGGED_IN_PATH, LOG_PATH, TOP_N
import json
import pandas as pd
import os
import pickle
import time
from oauth2client.service_account import ServiceAccountCredentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import pickle
from datetime import datetime as dt
import sys

def avoid_block_read(path):
    """
    Read while avoiding blocks (spams read operation until file not in use)
    :param path: Path of the target file
    :return: The contents of the target file
    """
    data = None
    while True:
        try:
            # if file does not exist create one
            if not os.path.isfile(path):
                with open(path, "wb") as f:
                    pickle.dump({}, f)
            with open(path, "rb") as f:
                data = pickle.load(f)
            break
        except Exception as e:
            pass
        time.sleep(0.1)
    return data


def avoid_block_write(path, data):
    """
    Write while avoiding blocks (spams write operation until file not in use)
    :param path: Path of the target file
    :param data: The data to be wrote into the file
    """
    while True:
        try:
            with open(path, "wb") as f:
                pickle.dump(data, f)
            break
        except Exception as e:
            pass
        time.sleep(0.1)

def avoid_block_pandas_read(path, **kwargs):
    """
    Read while avoiding blocks (spams read operation until file not in use)
    :param path: Path of the target file
    :return: The contents of the target file
    """
    data = None
    while True:
        try:
            # if file does not exist create one
            data = pd.read_csv(path, **kwargs)
            break
        except Exception as e:
            pass
        time.sleep(0.1)
    return data


def avoid_block_pandas_write(path, data, **kwargs):
    """
    Write while avoiding blocks (spams write operation until file not in use)
    :param path: Path of the target file
    :param data: The data to be wrote into the file
    """
    while True:
        try:
            data.to_csv(path, **kwargs)
            break
        except Exception as e:
            pass
        time.sleep(0.1)

def instantiate_data():
    pd.DataFrame([{"name": "filler"}]).to_csv(DAILY_PATH)
    pd.DataFrame([{"name": "filler"}]).to_csv(WEEKLY_PATH)

    with open(PIN_PATH, "w") as f:
        json.dump({"PIN": "TEST"}, f)

    with open(LAST_UPDATE_PATH, "wb") as f:
        pickle.dump(dt.utcnow(), f)

    with open(LOGGED_IN_PATH, "wb") as f:
        pickle.dump({}, f)


def insert_to_csv(name, hours):
    try:
        week = dt.utcnow().isocalendar()[1]  # Named tuples are not in Python 3.9>
        query = "{}-W{}".format(dt.utcnow().year, week)
        week_num = "Wk of " + str(dt.strptime(query + "-1", "%G-W%V-%u"))[:-8]
        day_num = str(dt.today().strftime("%Y-%m-%d"))

        # Write to csv
        daily_csv = avoid_block_pandas_read(DAILY_PATH, index_col=0)
        weekly_csv = avoid_block_pandas_read(WEEKLY_PATH, index_col=0)

        # Daily operations
        if day_num not in daily_csv.columns:
            daily_csv[day_num] = 0.0

        if name not in daily_csv["name"].values:
            new_row_data = {}
            for day in daily_csv.columns:
                new_row_data[day] = 0.0
            new_row_data["name"] = name
            daily_csv = pd.concat(
                [daily_csv, pd.DataFrame([new_row_data])], ignore_index=True
            ).sort_index()

        idx = daily_csv.loc[daily_csv["name"] == name].index[0]
        daily_csv.loc[idx, day_num] += hours

        avoid_block_pandas_write(DAILY_PATH, daily_csv)

        # Weekly operations
        if week_num not in weekly_csv.columns:
            weekly_csv[week_num] = 0.0

        if name not in weekly_csv["name"].values:
            new_row_data = {}
            for week in weekly_csv.columns:
                new_row_data[week] = 0.0
            new_row_data["name"] = name
            weekly_csv = pd.concat(
                [weekly_csv, pd.DataFrame([new_row_data])], ignore_index=True
            ).sort_index()

        idx = weekly_csv.loc[weekly_csv["name"] == name].index[0]
        weekly_csv.loc[idx, week_num] += hours

        avoid_block_pandas_write(WEEKLY_PATH, weekly_csv)
        return True
    except Exception as e:
        print(e)
        return False


def insert_pin(pin, name):
    with open(PIN_PATH, "r") as f:
        json_data = json.load(f)

    if pin in json_data.keys() or name in json_data.values():
        return False, "PIN or NAME already exists."
    json_data[str(pin)] = name

    with open(PIN_PATH, "w") as f:
        json.dump(json_data, f, indent=2)

    return True, "Successfully registered."


def get_name(pin):
    """
    Gets the name associated with a pin
    :param pin: The pin of the user
    :return: The name associated with that pin
    """
    with open(PIN_PATH, "r") as f:
        json_data = json.load(f)

    if pin not in json_data:
        return False, "PIN does not exist"
    return json_data[pin]

def calculate_metrics():
    # Current Week hours
    # Last Week hours
    weekly_metrics = {}
    df = avoid_block_pandas_read(WEEKLY_PATH)

    if len(df.columns) <= 2:
        weekly_metrics["current_week"] = 0
        weekly_metrics["last_week"] = 0
        weekly_metrics["total"] = 0
        weekly_metrics["max"] = 0
        weekly_metrics["last_max"] = 0
        weekly_metrics["average"] = 0
        weekly_metrics["last_average"] = 0
    elif len(df.columns) <= 3:
        weekly_metrics["current_week"] = df[df.columns[-1]].sum()
        weekly_metrics["last_week"] = 0
        weekly_metrics["total"] = df[df.columns[2:]].select_dtypes(include='number').sum().sum()
        weekly_metrics["max"] = max(list(df[df.columns[-1]]))
        weekly_metrics["last_max"] = 0
        weekly_metrics["average"] = weekly_metrics["current_week"]/(len(df)-1) # -1 because of filler
        weekly_metrics["last_average"] = 0
    else:
        weekly_metrics["current_week"] = df[df.columns[-1]].sum()
        weekly_metrics["last_week"] = df[df.columns[-2]].sum()
        weekly_metrics["total"] = df[df.columns[2:]].select_dtypes(include='number').sum().sum()
        weekly_metrics["max"] = max(list(df[df.columns[-1]]))
        weekly_metrics["last_max"] = max(list(df[df.columns[-2]]))
        weekly_metrics["average"] = weekly_metrics["current_week"]/(len(df)-1)  # -1 because of filler
        weekly_metrics["last_average"] = weekly_metrics["last_week"] / (len(df) - 1)  # -1 because of filler

    daily_metrics = {}
    df = avoid_block_pandas_read(DAILY_PATH)
    if len(df.columns) <= 2:
        daily_metrics["current_day"] = 0
        daily_metrics["last_day"] = 0
    elif len(df.columns) <= 3:
        daily_metrics["current_day"] = df[df.columns[-1]].sum()
        daily_metrics["last_day"] = 0
    else:
        daily_metrics["current_day"] = df[df.columns[-1]].sum()
        daily_metrics["last_day"] = df[df.columns[-2]].sum()

    return weekly_metrics, daily_metrics


def get_leaderboard():
    df = avoid_block_pandas_read(WEEKLY_PATH)
    if len(df.columns) <= 2:
        leaderboard = None
        time = None
    else:
        df["total_hours"] = df[df.columns[2:]].sum(axis=1)
        leaderboard = list(df.nlargest(TOP_N, 'total_hours')["name"])
        time = [int(i) for i in list(df.nlargest(TOP_N, 'total_hours')["total_hours"])]
    return leaderboard, time


def upload_data(share):

    with open(LOG_PATH, "a") as f:
        f.write(f"\nAttempting to UPLOAD at {dt.utcnow()}")

    # Access the drive
    gauth = GoogleAuth()

    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
        "home/robotiators/Documents/AttendanceVK2/pages/data/client_secrets.json", ["https://www.googleapis.com/auth/drive"]
    )
    drive = GoogleDrive(gauth)

    d = drive.CreateFile({"title": f"Daily_CSV_Backup_{str(dt.now().date())}.csv"})
    d.SetContentFile(DAILY_PATH)
    d.Upload()

    for email in share:
        d.InsertPermission({"type": "user", "role": "reader", "value": email})

    w = drive.CreateFile({"title": f"Weekly_CSV_Backup_{str(dt.now().date())}.csv"})
    w.SetContentFile(WEEKLY_PATH)
    w.Upload()

    for email in share:
        w.InsertPermission({"type": "user", "role": "reader", "value": email})

    with open(LAST_UPDATE_PATH, "wb") as f:
        pickle.dump(dt.utcnow())

    with open(LOG_PATH, "a") as f:
        f.write(f"\nSuccessful attempt to UPLOAD at {dt.utcnow()}")

