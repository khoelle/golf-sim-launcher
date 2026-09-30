# Golf Sim Launcher

A full-screen launcher for golf simulator software. One click starts GSPro, Awesome Golf, Square Golf, PurePlay, or any other program you add.

## Features

- Big logo tiles with a status dot (ready / file not found / not set up)
- Add, remove and reorder tiles: drag to sort, right-click for **Move left / Move right / Remove**
- Add your own logo to any tile (PNG, JPG, GIF, BMP, WebP)
- Custom background image with an adjustable darkness slider
- Optional full-screen start and minimize-after-launch
- Single file: the built-in logos are embedded in the script

## Requirements

- Windows (uses `%APPDATA%` for settings and Windows DPI scaling)
- Python 3.9+ with Tkinter (included in the standard Windows installer)
- Pillow

```
pip install -r requirements.txt
```

## Run

```
python GolfSimLauncher.py
```

Click **Settings** to point each tile at its `.exe`, add games, set a logo or change the background.

| Key | Action |
| --- | --- |
| `Esc` | Leave full screen |
| `F11` | Toggle full screen |

## Where settings are saved

`%APPDATA%\GolfSimLauncher\config.json` (plus `logos\` and `backgrounds\` folders for images you add). Delete that folder to reset everything.

## Build an .exe (optional)

Put a `background.png` next to the script, then double-click **`BUILD_LAUNCHER.bat`**. It installs PyInstaller and Pillow and builds a single windowed executable:

```
dist\GolfSimLauncher.exe
```

(The default background is bundled into the .exe. You can still change it later in Settings.)

## Notes

The bundled game logos belong to their respective owners and are included only to identify each program's tile.
