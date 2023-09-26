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
import glob
import winreg
import shutil
import vdf


def get_steam_install_path():
    # Open the Steam registry key
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Valve\\Steam")

    # Read the Steam installation path value
    install_path, _ = winreg.QueryValueEx(key, "SteamPath")

    # Close the registry key
    winreg.CloseKey(key)

    return install_path


def get_game_install_path(app_id):
    # Get the Steam installation path
    steam_path = get_steam_install_path()

    # Open steamapps/appmanifest_1272080.acf to read the "installdir" value
    acf_path = os.path.join(steam_path, "steamapps", "appmanifest_" + app_id + ".acf")
    acf_file = vdf.parse(open(acf_path))

    game_name = acf_file["AppState"]["installdir"]

    # Open steamapps/libraryfolders.vdf to read the library folders
    library_folders_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
    library_folders_file = vdf.parse(open(library_folders_path))

    # For each library folder search for the app_id, if found construct the path
    # and return it
    lf_count = library_folders_file["libraryfolders"].__len__()

    for i in range(0, lf_count):
        if library_folders_file["libraryfolders"][str(i)]["apps"].get(app_id):
            path = library_folders_file["libraryfolders"][str(i)]["path"]

            game_path = os.path.join(path, "steamapps", "common", game_name)
            return game_path


game_path = get_game_install_path("1272080")
overrides_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "overrides")
additions_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "additions")


def add_overrides():
    for root, dirs, files in os.walk(overrides_path):
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = src_file.replace(overrides_path, game_path)

            if not os.path.exists(os.path.dirname(dst_file)):
                os.makedirs(os.path.dirname(dst_file))

            # Backup the original file
            if os.path.exists(dst_file):
                os.rename(dst_file, dst_file + ".bak")

            shutil.copyfile(src_file, dst_file)


def remove_overrides():
    for root, dirs, files in os.walk(overrides_path):
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = src_file.replace(overrides_path, game_path)

            # Remove the override file
            if os.path.exists(dst_file):
                os.remove(dst_file)

            # Restore the original file
            if os.path.exists(dst_file + ".bak"):
                os.rename(dst_file + ".bak", dst_file)


def add_additions():
    for root, dirs, files in os.walk(additions_path):
        for file in files:
            if file == ".gitkeep":
                continue

            src_file = os.path.join(root, file)
            dst_file = src_file.replace(additions_path, game_path)

            if not os.path.exists(os.path.dirname(dst_file)):
                os.makedirs(os.path.dirname(dst_file))

            shutil.copyfile(src_file, dst_file)


def remove_additions():
    folders_to_remove = []

    for root, dirs, files in os.walk(additions_path):
        for file in files:
            if file == ".gitkeep":
                continue

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


def main():
    print("Finding PAYDAY 3 install path...")

    game_path = get_game_install_path("1272080")
    mod_dir = os.path.join(game_path, "PAYDAY3", "Content", "Paks", "~mods")

    print("Found PAYDAY 3 install path: " + game_path)

    # If the directory doesn't exist, exit
    if not os.path.isdir(mod_dir):
        print("Directory does not exist")
        sys.exit(1)

    loaded_mods = 0

    for mod in glob.glob(os.path.join(mod_dir, "*")):
        mod_name = os.path.basename(mod)

        if mod_name.endswith(".pak"):
            new_name = mod_name.replace(".pak", ".pak.disabled")
        else:
            loaded_mods += 1
            new_name = mod_name.replace(".pak.disabled", ".pak")

        # Rename the mod
        os.rename(mod, os.path.join(mod_dir, new_name))

    # If no mods, also disable UE4SS
    if loaded_mods == 0:
        # remove_overrides()
        remove_additions()
    else:
        # add_overrides()
        add_additions()

    print("")
    print("Mods toggled")


main()
