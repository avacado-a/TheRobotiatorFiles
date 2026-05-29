import os
import shutil
import time
import sys

def scan_and_export():
    # Attempt to find USB
    mount_points = ["/media/jules", "/mnt", "/media"]
    found = False

    for root in mount_points:
        if not os.path.exists(root): continue
        for d in os.listdir(root):
            path = os.path.join(root, d)
            if os.path.ismount(path) or d == "usb":
                print(f"USB Detected: {path}")
                ts = time.strftime("%Y%m%d-%H%M%S")
                target = os.path.join(path, f"robotiator_backup_{ts}")
                os.makedirs(target, exist_ok=True)

                shutil.copy("data/attendance.db", os.path.join(target, "attendance.db"))
                if os.path.exists("data/log.txt"):
                    shutil.copy("data/log.txt", os.path.join(target, "log.txt"))

                print(f"Backup Successful to {target}")
                found = True
                break
        if found: break

    if not found:
        print("No USB drive found.")

if __name__ == "__main__":
    scan_and_export()
