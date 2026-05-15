r"""
Everdell Russian translation installer.

Replaces two files in a local Everdell installation:
  * Everdell_Data\game.cfg
  * Everdell_Data\StreamingAssets\Localization\win\localization

The Russian versions of both files are bundled inside the exe at build time
(see build_exe.bat / PyInstaller --add-data). At runtime they are extracted to
sys._MEIPASS and copied over the game's files. Originals are backed up first.

The exe is built with --uac-admin so Windows elevates it automatically; writing
into "C:\Program Files (x86)" needs administrator rights.
"""

import ctypes
import os
import shutil
import sys
import winreg


# Default install location, overridden by Steam auto-detection when possible.
DEFAULT_EVERDELL = r"C:\Program Files (x86)\Steam\steamapps\common\Everdell"

# Files to replace: (name bundled in the exe, path relative to the Everdell folder)
FILES = [
    ("game.cfg", r"Everdell_Data\game.cfg"),
    ("localization", r"Everdell_Data\StreamingAssets\Localization\win\localization"),
]


def resource_dir():
    """Folder holding the bundled source files (game.cfg, localization)."""
    # PyInstaller --onefile extracts bundled data here; otherwise use script dir.
    return getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def find_everdell():
    """Return the Everdell install folder, auto-detecting Steam libraries."""
    candidates = []

    # Steam base path from the registry.
    steam = None
    for hive, key, name in [
        (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "SteamPath"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam", "InstallPath"),
    ]:
        try:
            with winreg.OpenKey(hive, key) as k:
                steam = winreg.QueryValueEx(k, name)[0]
                break
        except OSError:
            continue

    # Every Steam library folder may hold games; parse libraryfolders.vdf.
    if steam:
        vdf = os.path.join(steam, "steamapps", "libraryfolders.vdf")
        try:
            with open(vdf, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    # Lines look like:  "path"   "D:\\SteamLibrary"
                    if line.startswith('"path"'):
                        parts = line.split('"')
                        if len(parts) >= 4:
                            lib = parts[3].replace("\\\\", "\\")
                            candidates.append(
                                os.path.join(lib, "steamapps", "common", "Everdell")
                            )
        except OSError:
            pass
        candidates.append(
            os.path.join(steam, "steamapps", "common", "Everdell")
        )

    candidates.append(DEFAULT_EVERDELL)

    for path in candidates:
        if os.path.isfile(os.path.join(path, "Everdell_Data", "game.cfg")):
            return path
    return None


def main():
    print("=" * 60)
    print(" Everdell - Russian translation installer")
    print("=" * 60)

    everdell = find_everdell()
    if not everdell:
        print("\nERROR: Could not find an Everdell installation.")
        print("Looked in the default Steam path and all Steam libraries.")
        print(f"  Default checked: {DEFAULT_EVERDELL}")
        return 1

    print(f"\nEverdell found at:\n  {everdell}\n")

    src_dir = resource_dir()

    # Verify bundled source files exist before touching anything.
    for src_name, _ in FILES:
        src = os.path.join(src_dir, src_name)
        if not os.path.isfile(src):
            print(f"ERROR: bundled file missing from the exe: {src_name}")
            return 1

    for src_name, rel_dst in FILES:
        src = os.path.join(src_dir, src_name)
        dst = os.path.join(everdell, rel_dst)
        print(f"Installing {src_name} -> {rel_dst}")

        os.makedirs(os.path.dirname(dst), exist_ok=True)

        # Overwrite in place, no backup copies left behind.
        shutil.copy2(src, dst)
        print("  done.")

    print("\nAll files replaced. Russian translation installed.")
    return 0


if __name__ == "__main__":
    code = 1
    try:
        if not is_admin():
            # Re-launch elevated. The PyInstaller manifest normally handles this,
            # so this branch is just a safety net when run as a loose script.
            print("Requesting administrator rights...")
            rc = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit(0 if rc > 32 else 1)
        code = main()
    except Exception as exc:  # keep the window open on any failure
        print(f"\nERROR: {exc}")
    input("\nPress Enter to close...")
    sys.exit(code)
