# Python 3 script that toggles the enabled/disabled state of all mods in a
# given directory.  This is useful for quickly enabling/disabling all mods
# in a directory, for example when testing a new mod.
#
# Usage: python toggle_mods.py
#
# Author: Oliver Sayers <https://github.com/SavageCore>
# License: MIT
#
# Version: 1.0
#
# Changelog:
#  1.0 - Initial version

import os
import sys
import winreg
import vdf


def get_game_install_path(app_id):
    # Return the install path of the game

    # First check Steam
    steam_key = winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE,
        "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Steam App " + app_id,
    )

    install_location = winreg.QueryValueEx(steam_key, "InstallLocation")[0]

    winreg.CloseKey(steam_key)

    if install_location:
        return install_location

    # If not installed in Steam, check the Epic Games Store
    epic_manifests_path = os.path.join(
        os.getenv("ProgramData"), "Epic", "EpicGamesLauncher", "Data", "Manifests"
    )

    for root, dirs, files in os.walk(epic_manifests_path):
        for file in files:
            with open(os.path.join(root, file), "r") as f:
                manifest = vdf.load(f)

                if manifest["DisplayName"] == "PAYDAY 3":
                    return manifest["InstallLocation"]

    return None


cwd = os.getcwd()

game_path = get_game_install_path("1272080")
overrides_path = os.path.join(cwd, "overrides")
additions_path = os.path.join(cwd, "additions")
mods_path = os.path.join(cwd, "~mods")

if "--debug" in sys.argv:
    print("Game path: " + game_path)
    print("Overrides path: " + overrides_path)
    print("Additions path: " + additions_path)
    print("Mods path: " + mods_path)


def add_overrides():
    for root, dirs, files in os.walk(overrides_path):
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = src_file.replace(overrides_path, game_path)

            if not os.path.exists(os.path.dirname(dst_file)):
                os.makedirs(os.path.dirname(dst_file))

            # Backup the original file
            if os.path.exists(dst_file):
                if not os.path.exists(dst_file + ".bak"):
                    os.rename(dst_file, dst_file + ".bak")

            if not os.path.exists(dst_file):
                os.symlink(src_file, dst_file)


def remove_overrides():
    for root, dirs, files in os.walk(overrides_path):
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = src_file.replace(overrides_path, game_path)

            # If no .bak file exists, then continue
            if not os.path.exists(dst_file + ".bak"):
                print("No backup file found for " + dst_file)
                continue

            # Remove the override file
            if os.path.exists(dst_file):
                os.remove(dst_file)

            ue4ss_log = os.path.join(game_path, "PAYDAY3/Binaries/Win64/UE4SS.log")
            if os.path.exists(ue4ss_log):
                os.remove(ue4ss_log)

            # Restore the original file
            if not os.path.exists(dst_file + ".bak"):
                os.rename(dst_file + ".bak", dst_file)


def add_additions():
    for root, dirs, files in os.walk(additions_path):
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = src_file.replace(additions_path, game_path)

            if not os.path.exists(os.path.dirname(dst_file)):
                os.makedirs(os.path.dirname(dst_file))

            if not os.path.exists(dst_file):
                os.symlink(src_file, dst_file)


def remove_additions():
    folders_to_remove = []

    for root, dirs, files in os.walk(additions_path):
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = src_file.replace(additions_path, game_path)

            # Remove the addition file
            if os.path.exists(dst_file):
                os.remove(dst_file)

            # Store the folder to remove if empty later
            folders_to_remove.append(os.path.dirname(dst_file))

    # Remove duplicates
    folders_to_remove = list(dict.fromkeys(folders_to_remove))
    # Reverse the list so that the deepest folders are removed first
    folders_to_remove.sort(reverse=True)

    for folder in folders_to_remove:
        if os.path.exists(folder) and os.path.isdir(folder):
            if not os.listdir(folder):
                os.rmdir(folder)

                # Remove the parent folder if empty
                parent_folder = os.path.dirname(folder)
                if os.path.exists(parent_folder) and os.path.isdir(parent_folder):
                    if not os.listdir(parent_folder):
                        os.rmdir(parent_folder)


def add_mods():
    for root, dirs, files in os.walk(mods_path):
        for file in files:
            if file.endswith(".skip"):
                continue

            src_file = os.path.join(root, file)
            dst_file = src_file.replace(
                mods_path, game_path + "\\PAYDAY3\\Content\\Paks\\~mods"
            )

            if not os.path.exists(os.path.dirname(dst_file)):
                os.makedirs(os.path.dirname(dst_file))

            if not os.path.exists(dst_file):
                os.symlink(src_file, dst_file)


def remove_mods():
    # Remove the symlink
    for root, dirs, files in os.walk(mods_path):
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = src_file.replace(
                mods_path, game_path + "\\PAYDAY3\\Content\\Paks\\~mods"
            )

            if os.path.exists(dst_file):
                os.remove(dst_file)


# For each file in the game's ~mods folder
# Check if there is a matching file in the script's ~mods folder
# If there is not then delete the file in the game's ~mods folder
def cleanup_mods():
    for root, dirs, files in os.walk(game_path + "\\PAYDAY3\\Content\\Paks\\~mods"):
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = src_file.replace(
                game_path + "\\PAYDAY3\\Content\\Paks\\~mods", mods_path
            )

            if not os.path.exists(dst_file):
                os.remove(src_file)


def print_installed_mods(mod_dir):
    installed_mods = 0
    # Count the number mods installed
    for root, dirs, files in os.walk(mod_dir):
        for file in files:
            installed_mods += 1

    print("")
    print("Installed mods: " + str(installed_mods))

    return installed_mods


def main():
    print("\033[1m===| pd3-toggle-mods |===\033[0m")
    print("")
    # If windows, check if the script is running as admin
    if os.name == "nt":
        import ctypes

        if not ctypes.windll.shell32.IsUserAnAdmin():
            # Print red text to the console
            print("\033[91mThis script must be run as administrator\033[0m")
            print("")
            input("Press enter to continue...")

            sys.exit(1)

    game_path = get_game_install_path("1272080")
    mod_dir = os.path.join(game_path, "PAYDAY3", "Content", "Paks", "~mods")

    mods_available = 0
    force = False

    # If the game's mod directory doesn't exist, create it
    if not os.path.isdir(mod_dir):
        os.makedirs(mod_dir)
        force = True

    print("Checking for installed mods...")

    installed_mods = print_installed_mods(mod_dir)

    # If --force is supplied then force the script to install the mods
    if "--force" in sys.argv:
        force = True

    # Count the number of mods available
    for root, dirs, files in os.walk(mods_path):
        for file in files:
            if file.endswith(".skip"):
                continue

            mods_available += 1

    print("Available mods: " + str(mods_available))
    print("")

    # If mods_available not equal to installed_mods then
    # force the script to install the mods
    # This should catch mods being added or removed
    if mods_available != installed_mods:
        print("\033[93mMods have changed, forcing install...\033[0m")
        force = True

    if installed_mods > 0 and not force:
        print("\033[93mMods are currently installed, removing...\033[0m")
        remove_overrides()
        remove_additions()
        remove_mods()
    else:
        print(
            "\033[92mMods are currently not installed or --force was supplied, installing...\033[0m"
        )
        add_overrides()
        add_additions()
        add_mods()
        print_installed_mods(mod_dir)

    cleanup_mods()

    print("")
    input("Press enter to continue...")
    sys.exit(0)


main()
