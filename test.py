import random
from datetime import datetime, timedelta

def generate_massive_db(filename="db.txt", num_users=1000, total_events=10000000):
    print(f"Generating {total_events} events for {num_users} users...")
    
    base_time = datetime(2026, 1, 1, 8, 0, 0)
    seasons = ["PreSeason2026", "BuildSeason2026", "Competition2026","PreSeason20267", "BuildSeason20267", "Competition20267"]
    current_season_idx = 0
    
    # 1. Pre-populate user credentials pool
    user_pool = []
    for i in range(num_users):
        username = f"Student_{i}"
        pin = 1000 + i  # Unique 4-digit PINs
        user_pool.append({"username": username, "pin": str(pin), "logged_in": False, "active": True})
    
    with open(filename, "w") as f:
        # Start with the first season
        f.write(f"{base_time.strftime('%Y-%m-%d %H:%M:%S')}|system|-1|change_season|{seasons[current_season_idx]}\n")
        
        # Create all users in the file
        for u in user_pool:
            base_time += timedelta(seconds=1)
            f.write(f"{base_time.strftime('%Y-%m-%d %H:%M:%S')}|{u['username']}|{u['pin']}|create\n")
            
        # Define milestones where seasons transition
        season_triggers = [total_events // 3, (2 * total_events) // 3]
        
        # 2. Generate a massive stream of interleaved activity
        for step in range(total_events):
            base_time += timedelta(minutes=random.randint(1, 15))
            
            # Check for seasonal shifts
            if step in season_triggers and current_season_idx < len(seasons) - 1:
                current_season_idx += 1
                f.write(f"{base_time.strftime('%Y-%m-%d %H:%M:%S')}|system|-1|change_season|{seasons[current_season_idx]}\n")
                continue
                
            # Pick a random user to do something
            u = random.choice(user_pool)
            
            # Infrequent administrative actions (Deactivate / Reactivate / PIN changes)
            rand_roll = random.random()
            if rand_roll < 0.001:  # 0.1% chance: toggle activation status
                if u["active"] and not u["logged_in"]:
                    u["active"] = False
                    f.write(f"{base_time.strftime('%Y-%m-%d %H:%M:%S')}|{u['username']}|{u['pin']}|deactivate\n")
                elif not u["active"]:
                    u["active"] = True
                    f.write(f"{base_time.strftime('%Y-%m-%d %H:%M:%S')}|{u['username']}|{u['pin']}|activate\n")
                    
            elif rand_roll < 0.002:  # 0.1% chance: change PIN
                if u["active"] and not u["logged_in"]:
                    old_pin = u["pin"]
                    new_pin = str(int(old_pin) + 5000)  # Move to a completely new range
                    u["pin"] = new_pin
                    f.write(f"{base_time.strftime('%Y-%m-%d %H:%M:%S')}|{u['username']}|{old_pin}|change_pin|{new_pin}\n")
            
            # Standard sign-in / sign-out clock cycles
            else:
                if not u["logged_in"] and u["active"]:
                    u["logged_in"] = True
                    f.write(f"{base_time.strftime('%Y-%m-%d %H:%M:%S')}|{u['username']}|{u['pin']}|login\n")
                elif u["logged_in"]:
                    u["logged_in"] = False
                    f.write(f"{base_time.strftime('%Y-%m-%d %H:%M:%S')}|{u['username']}|{u['pin']}|logout\n")

    print(f"Done! Created '{filename}' successfully.")

if __name__ == "__main__":
    generate_massive_db()