![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/SavageCore/pd3-toggle-mods/release.yml?style=for-the-badge)

# pd3-toggle-mods

> This script is used to toggle mods on and off for the game [Payday 3](https://store.steampowered.com/app/1194630/PAYDAY_3/).

## Usage

1. Download and extract the latest [release](https://github.com/SavageCore/pd3-toggle-mods/releases/latest)
1. Place any pak mods you want to toggle in the `~mods` folder. You may rename them to ".skip" to not install them.
1. Any additional files that you want to be copied to the game folder should be placed in the `additions` folder. This includes UE4SS.
1. You guessed it! Overrides go in the `overrides` folder. These are files which get backed up and replaced when toggling mods. Such as intro videos.
1. Run the exe as Admin.

### Example Folder Structure

```
ToggleMods.exe
~mods
    mod1.pak
    mod2.pak
    mod3.pak.skip
additions
    PAYDAY3
        Binaries
            Win64
                ue4ss.dll
overrides
    PAYDAY3
        Content
            Movies
                StartUp_DeepSilver.bk2
```

### Debugging

You may run the script with the `--debug` flag to see some extra information.

# Building

1. Install [Python 3](https://www.python.org/downloads/).
1. Run `pip install -r requirements.txt` in the project directory.
1. Run `pyinstaller --noconfirm --onefile --console --uac-admin --name=pd3-toggle-mods main.py` in the project directory.

# Publishing

1. Push a new tag to the repo. This will trigger a GitHub Action which will build the script and upload it as an asset to the release.

## Notes

- The script will automatically detect the game folder.
- You may run with the `--force` flag to force installation rather than toggling.
- If there are more mods in the `~mods` folder than currently installed, the script will also `--force` install.