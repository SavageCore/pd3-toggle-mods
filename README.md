# Toggle Mods Script

This script is used to toggle mods on and off for the game [Payday 3](https://store.steampowered.com/app/1194630/PAYDAY_3/).

## Usage

1. Download and extract the latest [release]().
1. Place any pak mods you want to toggle in the `~mods` folder. You may rename them to ".skip" to not install them.
1. Any additional files that you want to be copied to the game folder should be placed in the `additions` folder. This includes UE4SS.
1. You guessed it! Overrides go in the `overrides` folder. These are files which get backed up and replaced when toggling mods. Such as intro videos.
1. Run the exe as Admin.

## Notes

- The script will automatically detect the game folder.
- You may run with the `--force` flag to force installation.