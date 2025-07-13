import sys, time, os, shutil, subprocess

old_exe = sys.argv[1]
new_exe = sys.argv[2]
backup_exe = old_exe + ".bak"
log_path = os.path.join(os.path.dirname(old_exe), "update_log.txt")

def log(msg):
    with open(log_path, "a") as f:
        f.write(f"{time.ctime()} | {msg}\n")

def safe_remove(file):
    for _ in range(5):
        try:
            if os.path.exists(file):
                os.remove(file)
            return True
        except PermissionError:
            time.sleep(0.5)
    return False

time.sleep(1.5)

try:
    if not os.path.exists(new_exe):
        raise FileNotFoundError(f"New .exe not found: {new_exe}")
    
    log("Backing up current .exe")
    shutil.copy2(old_exe, backup_exe)

    log("Attempting to delete old .exe")
    if not safe_remove(old_exe):
        raise RuntimeError("Failed to remove old executable")

    log("Moving new .exe into place")
    shutil.move(new_exe, old_exe)

    log("Update complete — not launching application")

except Exception as e:
    log(f"Update failed: {e}")
    if os.path.exists(backup_exe):
        log("Restoring from backup")
        shutil.move(backup_exe, old_exe)
        log("Backup restored — not launching application")
    else:
        log("No backup available to restore")
        