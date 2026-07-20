import os
import random
from datetime import datetime, timedelta
days = 1825
studentsOnTeam = 40
# Set target end time to exactly "today" at 6:17 PM
target_end_time = datetime(2026, 7, 20, 18, 17, 0)
start_date = target_end_time - timedelta(days=days)

# Define our roster of students (names and unique PINs)
students = [
    {"username": "Aikam", "pin": "1234"},
] + [
    {"username": "Student_"+str(i), "pin": str(i+1000)} for i in range(studentsOnTeam)
]

def format_ts(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def generate_logs():
    logs = []
    current_time = start_date
    
    # Track student login states during log generation
    active_logins = {}
    
    # Establish the initial season
    logs.append(f"{format_ts(current_time)}|system|-1|change_season|BuildSeason2026")
    
    # Create all users at the very beginning of the log
    for s in students:
        current_time += timedelta(seconds=1)
        logs.append(f"{format_ts(current_time)}|{s['username']}|{s['pin']}|create")
        active_logins[s['pin']] = False

    # Step day-by-day for 30 days
    for day_offset in range(days):
        meeting_day = start_date + timedelta(days=day_offset)
        
        # Don't simulate today's normal meeting sequence here; we'll write a custom live session for today
        if meeting_day.date() == target_end_time.date():
            continue
            
        # Simulate season change mid-month (July 5th)
        if meeting_day.date() == datetime(2026, 7, 5).date():
            season_change_time = datetime.combine(meeting_day.date(), datetime.min.time()) + timedelta(hours=12)
            logs.append(f"{format_ts(season_change_time)}|system|-1|change_season|Competition2026")

        # FRC Offseason/Summer Schedule: Meetings on Tuesday, Thursday, and Saturday
        is_meeting = meeting_day.weekday() in [1, 3, 5]  # Tuesday = 1, Thursday = 3, Saturday = 5
        
        if is_meeting:
            # Weekday meetings: 4:00 PM - 8:00 PM (16:00 to 20:00)
            # Saturday meetings: 9:00 AM - 3:00 PM (09:00 to 15:00)
            if meeting_day.weekday() in [1, 3]:
                start_hour, end_hour = 16, 20
            else:
                start_hour, end_hour = 9, 15
                
            meeting_start = datetime.combine(meeting_day.date(), datetime.min.time()) + timedelta(hours=start_hour)
            meeting_end = datetime.combine(meeting_day.date(), datetime.min.time()) + timedelta(hours=end_hour)
            
            # Select a random subset of 5 to 9 students attending today's meeting
            attendees = random.sample(students, k=random.randint(5, studentsOnTeam))
            forgotten_logouts = []

            # 1. Simulate check-ins (staggered slightly around meeting start)
            for student in attendees:
                stagger_seconds = random.randint(-900, 900)  # arrive up to 15 mins early or late
                login_time = meeting_start + timedelta(seconds=stagger_seconds)
                logs.append(f"{format_ts(login_time)}|{student['username']}|{student['pin']}|login")
                active_logins[student['pin']] = login_time
                
                # 10% chance a student forgets to log out at the end of the meeting
                if random.random() < 0.10:
                    forgotten_logouts.append(student)

            # 2. Simulate check-outs
            for student in attendees:
                if student in forgotten_logouts:
                    continue  # Skip logout to simulate ghost session
                    
                stagger_seconds = random.randint(-600, 1200)  # leave up to 10 mins early or 20 mins late
                logout_time = meeting_end + timedelta(seconds=stagger_seconds)
                
                # Check to prevent time-travel logs if checkout calculation slips before checkin
                if logout_time > active_logins[student['pin']]:
                    logs.append(f"{format_ts(logout_time)}|{student['username']}|{student['pin']}|logout")
                    active_logins[student['pin']] = False

            # 3. Handle midnight cleanups for forgotten logouts (using delete_time at midnight)
            if forgotten_logouts:
                midnight = datetime.combine(meeting_day.date(), datetime.min.time()) + timedelta(days=1)
                for student in forgotten_logouts:
                    logs.append(f"{format_ts(midnight)}|{student['username']}|{student['pin']}|delete_time")
                    active_logins[student['pin']] = False

    # # Final Day Simulation: Today (July 20, 2026)
    # # A meeting started today at 3:00 PM (15:00:00) and is still active "right now" at 6:17 PM (18:17:00)
    # today = target_end_time.date()
    # today_meeting_start = datetime.combine(today, datetime.min.time()) + timedelta(hours=15) # 3:00 PM
    
    # # Active today: Aikam, Student_1, Student_2, Student_5
    # today_attendees = [
    #     {"username": "Student_1", "pin": "1001", "login": today_meeting_start + timedelta(minutes=5), "logout": today_meeting_start + timedelta(hours=2)}, # Logged out already
    #     {"username": "Student_2", "pin": "1002", "login": today_meeting_start + timedelta(minutes=10), "logout": None}, # Still here!
    #     {"username": "Aikam", "pin": "1234", "login": today_meeting_start + timedelta(minutes=12), "logout": None}, # Still here!
    #     {"username": "Student_5", "pin": "1005", "login": today_meeting_start + timedelta(minutes=15), "logout": None}, # Still here!
    # ]
    
    # for s in today_attendees:
    #     logs.append(f"{format_ts(s['login'])}|{s['username']}|{s['pin']}|login")
    #     if s['logout'] is not None:
    #         logs.append(f"{format_ts(s['logout'])}|{s['username']}|{s['pin']}|logout")

    # # Sort historical events by timestamp to guarantee absolute chronological order
    # logs.sort(key=lambda x: datetime.strptime(x.split("|")[0], "%Y-%m-%d %H:%M:%S"))

    # # Save output directly to db.txt
    # with open("db.txt", "w", encoding="utf-8") as f:
    #     for log in logs:
    #         f.write(log + "\n")
            
    print(f"Successfully generated a 30-day realistic log file 'db.txt'!")
    print(f"File contains {len(logs)} log entries ending exactly on {format_ts(target_end_time)}")
    # print("Active users still checked in: Aikam (1234), Student_2 (1002), Student_5 (1005)")

if __name__ == "__main__":
    generate_logs()