import os
import shutil
import time

def scan_and_export():
    print("Scanning for USB drives...")
    # Common mount points for Linux
    mount_points = ["/media/", "/mnt/"]

    found = False
    for root_mount in mount_points:
        if not os.path.exists(root_mount):
            continue

        for drive in os.listdir(root_mount):
            drive_path = os.path.join(root_mount, drive)
            if os.path.ismount(drive_path) or drive == "usb": # 'usb' check for specific setups
                print(f"Found drive: {drive_path}")
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                target = os.path.join(drive_path, f"robotiators_backup_{timestamp}")
                os.makedirs(target, exist_ok=True)

                shutil.copy("data/attendance.db", os.path.join(target, "attendance.db"))
                if os.path.exists("data/captures"):
                    # Only copy recent captures to save space/time
                    shutil.copytree("data/captures", os.path.join(target, "captures"), dirs_exist_ok=True)

                print(f"Export successful to {target}")
                found = True
                break
        if found: break

    if not found:
        print("No USB drive detected. Please ensure it is mounted in /media or /mnt.")

if __name__ == "__main__":
    scan_and_export()
