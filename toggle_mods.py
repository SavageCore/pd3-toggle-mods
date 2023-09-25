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

    # Open steamapps/appmanifest_1272080.acf
    acf_path = os.path.join(steam_path, "steamapps", "appmanifest_" + app_id + ".acf")
    acf_file = vdf.parse(open(acf_path))

    game_name = acf_file["AppState"]["installdir"]

    library_folders_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
    library_folders_file = vdf.parse(open(library_folders_path))

    # For each library folder search for app_id, if found construct the path
    # and return it
    lf_count = library_folders_file["libraryfolders"].__len__()

    for i in range(0, lf_count):
        if library_folders_file["libraryfolders"][str(i)]["apps"].get(app_id):
            path = library_folders_file["libraryfolders"][str(i)]["path"]

            game_path = os.path.join(path, "steamapps", "common", game_name)
            return game_path


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

        xinput_path_base = os.path.join(game_path, "PAYDAY3", "Binaries", "Win64")

        xinput_path = os.path.join(xinput_path_base, "xinput1_3.dll")
        xinput_disabled_path = os.path.join(xinput_path_base, "xinput1_3.dll.disabled")

    # If no mods, also disable UE4SS
    if loaded_mods == 0:
        if os.path.isfile(xinput_path):
            os.rename(xinput_path, xinput_disabled_path)
    else:
        if os.path.isfile(xinput_disabled_path):
            os.rename(xinput_disabled_path, xinput_path)

    print("")
    print("Mods toggled")


main()
