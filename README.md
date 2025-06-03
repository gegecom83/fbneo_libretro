# fbneo_libretro.py

A cross-platform graphical ROM manager and launcher for FinalBurn Neo (Libretro)  
by [gegecom83](https://github.com/gegecom83)

---

## Overview

**fbneo_libretro.py** is a powerful and user-friendly ROM browser, manager, and launcher for the [FinalBurn Neo](https://github.com/finalburnneo/FBNeo) emulator core (Libretro).  
It supports a broad range of classic systems and is designed for smooth navigation using both keyboard/mouse and game controllers.

Key features:

- **Multi-system support:** Manage and launch ROMs for Arcade, NES, SNES, Sega, Neo-Geo, MSX, ZX Spectrum, and many more.
- **Automatic ROM metadata:** Auto-generate ROM title lists with year and manufacturer info via XML/DAT files.
- **Joystick navigation:** Full joystick/gamepad navigation and controls, including rapid scrolling and system switching.
- **Configurable:** All settings (paths, controls, XML files) are easily editable in the GUI.
- **Fast search & filtering:** Find ROMs quickly by title, year, or manufacturer.
- **Cross-platform:** Works on Windows, Linux, and macOS (requires Python 3, PyQt5, and pygame).

---

## Installation

1. **Clone/download** this repository.
2. Install dependencies:
   ```bash
   pip install PyQt5 pygame
   ```
3. Make sure you have [RetroArch](https://www.retroarch.com/) and the FinalBurn Neo core (`fbneo_libretro`).
4. Place your ROMs in the appropriate folders for each system.

---

## Usage

Run the script:
```bash
python fbneo_libretro.py
```

- Set up paths to RetroArch, the FBNeo core, and your ROM folders via the **Settings** dialog.
- Optionally, add XML/DAT files for richer ROM metadata.
- Browse, search, and filter your ROMs by system, title, year, or manufacturer.
- Double-click or press your joystick "select" button to launch a game instantly.

---

## Supported Systems

- Arcade (MAME/FBNeo)
- CBS ColecoVision
- Fairchild ChannelF
- MSX 1
- Nec PC-Engine / SuperGrafX / TurboGrafx-16
- Nintendo Entertainment System (NES) / Famicom Disk System
- Super Nintendo
- Sega GameGear / Master System / Megadrive / SG-1000
- SNK Neo-Geo Pocket / Neo-Geo CD
- ZX Spectrum

---

## Configuration

All settings are stored in `config.json` (auto-generated).  
You can configure:

- Paths to RetroArch and FBNeo core (.dll/.so/.dylib)
- ROM folders per system
- XML/DAT metadata files per system (optional)
- Joystick button mappings and scrolling behavior

---

## Dependencies

- Python 3.6+
- [PyQt5](https://pypi.org/project/PyQt5/)
- [pygame](https://pypi.org/project/pygame/)

---

## Screenshots

*Want to add screenshots? Paste them here!*

---

## Credits

- Built and maintained by [gegecom83](https://github.com/gegecom83)
- Powered by [FinalBurn Neo](https://github.com/finalburnneo/FBNeo) and [RetroArch](https://www.retroarch.com/)

---

## License

This project is distributed under the MIT License.

---

**Enjoy your retro gaming!**