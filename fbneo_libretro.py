import os
import sys
import subprocess
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pygame
import time

# Helper function to get the executable's directory
def get_base_dir():
    """Return the directory containing the executable (or script in dev mode)."""
    if getattr(sys, 'frozen', False):  # Running as a PyInstaller executable
        return Path(sys.executable).parent
    else:  # Running as a Python script
        return Path(os.path.dirname(__file__))

# Helper function to get the path to a resource file (e.g., icon.ico)
def get_resource_path(relative_path: str) -> Path:
    """Return the absolute path to a resource file, handling PyInstaller bundles."""
    if getattr(sys, 'frozen', False):  # Running as a PyInstaller executable
        base_path = Path(sys._MEIPASS)  # Temporary directory where resources are extracted
    else:  # Running as a Python script
        base_path = Path(os.path.dirname(__file__))
    return base_path / relative_path

# Configuration of the 17 tabs
TAB_CONFIGS = [
    {"name": "Arcade", "rom_titles_file": Path("rom_titles_arcade.txt"), "roms_dir": Path("")},
    {"name": "CBS ColecoVision", "rom_titles_file": Path("rom_titles_coleco.txt"), "roms_dir": Path("")},
    {"name": "Fairchild ChannelF", "rom_titles_file": Path("rom_titles_channelf.txt"), "roms_dir": Path("")},
    {"name": "MSX 1", "rom_titles_file": Path("rom_titles_msx.txt"), "roms_dir": Path("")},
    {"name": "Nec PC-Engine", "rom_titles_file": Path("rom_titles_pce.txt"), "roms_dir": Path("")},
    {"name": "Nec SuperGrafX", "rom_titles_file": Path("rom_titles_sgx.txt"), "roms_dir": Path("")},
    {"name": "Nec TurboGrafx-16", "rom_titles_file": Path("rom_titles_tg16.txt"), "roms_dir": Path("")},
    {"name": "Nintendo Entertainment System", "rom_titles_file": Path("rom_titles_nes.txt"), "roms_dir": Path("")},
    {"name": "Nintendo Family Disk System", "rom_titles_file": Path("rom_titles_fds.txt"), "roms_dir": Path("")},
    {"name": "Super Nintendo Entertainment System", "rom_titles_file": Path("rom_titles_snes.txt"), "roms_dir": Path("")},
    {"name": "Sega GameGear", "rom_titles_file": Path("rom_titles_gamegear.txt"), "roms_dir": Path("")},
    {"name": "Sega Master System", "rom_titles_file": Path("rom_titles_sms.txt"), "roms_dir": Path("")},
    {"name": "Sega Megadrive", "rom_titles_file": Path("rom_titles_megadrive.txt"), "roms_dir": Path("")},
    {"name": "Sega SG-1000", "rom_titles_file": Path("rom_titles_sg1000.txt"), "roms_dir": Path("")},
    {"name": "SNK Neo-Geo Pocket", "rom_titles_file": Path("rom_titles_ngp.txt"), "roms_dir": Path("")},
    {"name": "SNK Neo-Geo CD", "rom_titles_file": Path("rom_titles_neocd.txt"), "roms_dir": Path("")},
    {"name": "ZX Spectrum", "rom_titles_file": Path("rom_titles_spectrum.txt"), "roms_dir": Path("")}
]

# Path to configuration file
CONFIG_FILE = get_base_dir() / "config.json"

# Default configuration with Xbox 360 controller support
DEFAULT_CONFIG = {
    "RETROARCH": r"C:\Programs\RetroArch\retroarch.exe",
    "RETROARCH_CORE": r"C:\Programs\RetroArch\cores\fbneo_libretro.dll",
    "input_xml_files": {config["name"]: "" for config in TAB_CONFIGS},
    "roms_dirs": {config["name"]: str(config["roms_dir"]) for config in TAB_CONFIGS},
    "output_dirs": {config["name"]: str(get_base_dir()) for config in TAB_CONFIGS},
    "joystick_config": {
        "axis_y": -1,
        "hat_scroll_cooldown": 0.02,
        "hat_fast_steps": 5,
        "button_up": 2,
        "button_down": 3,
        "button_select": 0,
        "button_settings": 7,
        "button_prev_tab": 4,
        "button_next_tab": 5
    }
}

# Global configuration variables
RETROARCH = Path(DEFAULT_CONFIG["RETROARCH"])
RETROARCH_CORE = Path(DEFAULT_CONFIG["RETROARCH_CORE"])
INPUT_TYPES = {}
ROMS_DIRS = {}
OUTPUT_DIRS = {}
JOYSTICK_CONFIG = {}

def load_config():
    """Load configuration from file or apply defaults."""
    global RETROARCH, RETROARCH_CORE, INPUT_TYPES, ROMS_DIRS, OUTPUT_DIRS, JOYSTICK_CONFIG
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                RETROARCH = Path(config.get("RETROARCH", DEFAULT_CONFIG["RETROARCH"]))
                RETROARCH_CORE = Path(config.get("RETROARCH_CORE", DEFAULT_CONFIG["RETROARCH_CORE"]))
                INPUT_TYPES = config.get("input_xml_files", DEFAULT_CONFIG["input_xml_files"])
                ROMS_DIRS = config.get("roms_dirs", DEFAULT_CONFIG["roms_dirs"])
                OUTPUT_DIRS = config.get("output_dirs", DEFAULT_CONFIG["output_dirs"])
                JOYSTICK_CONFIG = config.get("joystick_config", DEFAULT_CONFIG["joystick_config"])
                # Ensure all tabs have configuration entries
                for tab_name in DEFAULT_CONFIG["input_xml_files"]:
                    INPUT_TYPES.setdefault(tab_name, "")
                    ROMS_DIRS.setdefault(tab_name, DEFAULT_CONFIG["roms_dirs"][tab_name])
                    OUTPUT_DIRS.setdefault(tab_name, DEFAULT_CONFIG["output_dirs"][tab_name])
                # Ensure all joystick config fields are present
                JOYSTICK_CONFIG = {**DEFAULT_CONFIG["joystick_config"], **JOYSTICK_CONFIG}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config: {e}")
            reset_to_defaults()
    else:
        reset_to_defaults()
        save_config()

def reset_to_defaults():
    """Reset configuration to defaults."""
    global RETROARCH, RETROARCH_CORE, INPUT_TYPES, ROMS_DIRS, OUTPUT_DIRS, JOYSTICK_CONFIG
    RETROARCH = Path(DEFAULT_CONFIG["RETROARCH"])
    RETROARCH_CORE = Path(DEFAULT_CONFIG["RETROARCH_CORE"])
    INPUT_TYPES = DEFAULT_CONFIG["input_xml_files"]
    ROMS_DIRS = DEFAULT_CONFIG["roms_dirs"]
    OUTPUT_DIRS = DEFAULT_CONFIG["output_dirs"]
    JOYSTICK_CONFIG = DEFAULT_CONFIG["joystick_config"]

def save_config():
    """Save configuration to file."""
    config = {
        "RETROARCH": str(RETROARCH),
        "RETROARCH_CORE": str(RETROARCH_CORE),
        "input_xml_files": INPUT_TYPES,
        "roms_dirs": ROMS_DIRS,
        "output_dirs": OUTPUT_DIRS,
        "joystick_config": JOYSTICK_CONFIG
    }
    try:
        config_dir = CONFIG_FILE.parent
        if not os.access(config_dir, os.W_OK):
            messagebox.showerror("Error", f"Cannot write to {config_dir}. Try running as administrator.")
            return
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    except PermissionError:
        messagebox.showerror("Error", "Cannot save config: Permission denied. Try running as administrator.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save config: {e}")

# Load configuration at startup
load_config()

def load_rom_titles(filename: Path) -> Dict[str, str]:
    """Load ROM titles from a file, excluding invalid or placeholder titles."""
    rom_titles = {}
    if not filename.exists():
        return rom_titles
    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split(maxsplit=1)
                if len(parts) >= 2:
                    key = parts[0].lower()
                    title = parts[1].strip('"')
                    # Skip empty or placeholder titles
                    if not title or title.lower() in {"untitled", "unknown", "no title"}:
                        continue
                    rom_titles[key] = title
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read ROM titles {filename}: {e}")
    return rom_titles

def get_rom_list(rom_titles_file: Path, roms_dir: Path) -> List[Tuple[str, str]]:
    """Get sorted list of ROMs with valid titles, excluding untitled or invalid entries except for .cue files."""
    rom_titles = load_rom_titles(rom_titles_file)
    if not roms_dir.exists():
        return []
    
    # Supported ROM extensions
    roms = [f for f in roms_dir.rglob('*') if f.is_file() and f.suffix.lower() in {'.zip', '.7z', '.cue'}]
    roms_no_ext = {rom.stem: rom.name for rom in roms}
    
    # Filter ROMs with valid titles, exempting .cue files
    rom_list = []
    for rom, rom_name in roms_no_ext.items():
        title = rom_titles.get(rom.lower(), rom)  # Default to ROM stem if no title
        # Skip non-.cue ROMs with empty, "untitled", or identical-to-filename titles
        if rom_name.lower().endswith('.cue'):
            rom_list.append((rom, title))  # Include .cue files regardless of title
        elif not title or title.strip().lower() in {"", "untitled", rom.lower()}:
            continue
        else:
            rom_list.append((rom, title))
    
    return sorted(rom_list, key=lambda x: x[1].lower())

def run_rom(rom: str, roms_dir: Path) -> None:
    """Launch a ROM using RetroArch."""
    try:
        if not RETROARCH.exists() or not RETROARCH.name.lower().endswith(".exe") or "retroarch" not in RETROARCH.name.lower():
            messagebox.showerror("Error", f"Invalid RetroArch executable: {RETROARCH}")
            return
        if not RETROARCH_CORE.exists() or not RETROARCH_CORE.name.lower().endswith(".dll"):
            messagebox.showerror("Error", f"Invalid RetroArch core: {RETROARCH_CORE}")
            return
        
        possible_extensions = ['.zip', '.7z', '.cue']
        rom_path = None
        for ext in possible_extensions:
            for candidate in roms_dir.rglob(f"{rom}{ext}"):
                if candidate.is_file():
                    rom_path = candidate
                    break
            if rom_path:
                break
        
        if not rom_path:
            messagebox.showerror("Error", f"ROM file not found for {rom} in {roms_dir}\nTried extensions: {', '.join(possible_extensions)}")
            return

        cmd = [str(RETROARCH), "-L", str(RETROARCH_CORE)]
        if rom_path.suffix.lower() == '.cue':
            cmd.extend(["--subsystem", "neocd"])
        cmd.append(str(rom_path))
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            messagebox.showerror("Error", f"Failed to launch RetroArch:\n{result.stderr}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch ROM: {e}")

class JoystickSettingsWindow:
    """Window for configuring joystick settings."""
    def __init__(self, root, parent_gui):
        self.root = tk.Toplevel(root)
        self.root.title("Joystick Settings")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        self.parent_gui = parent_gui

        try:
            icon_path = get_resource_path("icon.ico")
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception:
            pass

        self.axis_y_var = tk.StringVar(value=str(JOYSTICK_CONFIG.get("axis_y", -1)))
        self.hat_scroll_cooldown_var = tk.StringVar(value=str(JOYSTICK_CONFIG.get("hat_scroll_cooldown", 0.02)))
        self.hat_fast_steps_var = tk.StringVar(value=str(JOYSTICK_CONFIG.get("hat_fast_steps", 5)))
        self.button_up_var = tk.StringVar(value=str(JOYSTICK_CONFIG.get("button_up", 2)))
        self.button_down_var = tk.StringVar(value=str(JOYSTICK_CONFIG.get("button_down", 3)))
        self.button_select_var = tk.StringVar(value=str(JOYSTICK_CONFIG.get("button_select", 0)))
        self.button_settings_var = tk.StringVar(value=str(JOYSTICK_CONFIG.get("button_settings", 7)))
        self.button_prev_tab_var = tk.StringVar(value=str(JOYSTICK_CONFIG.get("button_prev_tab", 4)))
        self.button_next_tab_var = tk.StringVar(value=str(JOYSTICK_CONFIG.get("button_next_tab", 5)))

        self.create_widgets()
        self.root.lift()  # Ensure Joystick Settings window is in foreground when opened

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=7)
        main_frame.pack(fill=tk.BOTH, expand=True)

        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(fill=tk.BOTH, expand=True, anchor="w")

        for label_text, var in [
            ("Joystick Y-Axis Index (-1 to disable):", self.axis_y_var),
            ("Fast Scroll Cooldown (seconds, 0.02-0.2):", self.hat_scroll_cooldown_var),
            ("Fast Scroll Initial Steps (1-15):", self.hat_fast_steps_var),
            ("Joystick Up Button Index:", self.button_up_var),
            ("Joystick Down Button Index:", self.button_down_var),
            ("Joystick Select Button Index:", self.button_select_var),
            ("Joystick Settings Button Index:", self.button_settings_var),
            ("Joystick Previous Tab Button Index:", self.button_prev_tab_var),
            ("Joystick Next Tab Button Index:", self.button_next_tab_var)
        ]:
            row_frame = ttk.Frame(fields_frame)
            row_frame.pack(fill=tk.X, pady=7, anchor="w")
            ttk.Label(row_frame, text=label_text, width=40).pack(side="left")
            ttk.Entry(row_frame, textvariable=var, width=40).pack(side="left", padx=5)

        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(anchor="se", pady=7)
        ttk.Button(buttons_frame, text="Save", command=self.save_settings, padding=5).pack(side="right", padx=7)
        ttk.Button(buttons_frame, text="Reset Defaults", command=self.restore_defaults, padding=5).pack(side="right", padx=7)
        ttk.Button(buttons_frame, text="Cancel", command=self.root.destroy, padding=5).pack(side="right", padx=7)
        ttk.Button(buttons_frame, text="Test Joystick", command=self.test_joystick, padding=5).pack(side="right", padx=7)

    def test_joystick(self):
        if not pygame.joystick.get_count():
            messagebox.showwarning("Warning", "No joystick detected.")
            return

        test_window = tk.Toplevel(self.root)
        test_window.title("Joystick Test")
        test_window.geometry("600x400")
        test_window.resizable(False, False)

        text_area = tk.Text(test_window, height=15, width=60)
        text_area.pack(padx=7, pady=7, fill=tk.BOTH, expand=True)

        try:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            text_area.insert(tk.END, f"Joystick: {joystick.get_name()}\n")
            text_area.insert(tk.END, f"Number of axes: {joystick.get_numaxes()}\n")
            text_area.insert(tk.END, f"Number of buttons: {joystick.get_numbuttons()}\n")
            text_area.insert(tk.END, f"Number of hats: {joystick.get_numhats()}\n\n")

            def update_joystick():
                try:
                    pygame.event.pump()
                    for i in range(joystick.get_numaxes()):
                        if abs(joystick.get_axis(i)) > 0.1:
                            text_area.delete("5.0", tk.END)
                            text_area.insert(tk.END, f"Axis {i}: {joystick.get_axis(i):.3f}\n")
                    for i in range(joystick.get_numbuttons()):
                        if joystick.get_button(i):
                            text_area.delete("5.0", tk.END)
                            text_area.insert(tk.END, f"Button {i} pressed\n")
                    for i in range(joystick.get_numhats()):
                        if joystick.get_hat(i) != (0, 0):
                            text_area.delete("5.0", tk.END)
                            text_area.insert(tk.END, f"Hat {i}: {joystick.get_hat(i)}\n")
                    test_window.after(20, update_joystick)
                except Exception as e:
                    text_area.insert(tk.END, f"Error: {e}\n")

            update_joystick()
        except Exception as e:
            text_area.insert(tk.END, f"Error initializing joystick: {e}\n")

    def save_settings(self):
        global JOYSTICK_CONFIG
        try:
            hat_scroll_cooldown = float(self.hat_scroll_cooldown_var.get())
            hat_fast_steps = int(self.hat_fast_steps_var.get())
            if not 0.02 <= hat_scroll_cooldown <= 0.2:
                messagebox.showerror("Error", "Fast Scroll Cooldown must be between 0.02 and 0.2 seconds.")
                return
            if not 1 <= hat_fast_steps <= 15:
                messagebox.showerror("Error", "Fast Scroll Initial Steps must be between 1 and 15.")
                return
            JOYSTICK_CONFIG = {
                "axis_y": int(self.axis_y_var.get()),
                "hat_scroll_cooldown": hat_scroll_cooldown,
                "hat_fast_steps": hat_fast_steps,
                "button_up": int(self.button_up_var.get()),
                "button_down": int(self.button_down_var.get()),
                "button_select": int(self.button_select_var.get()),
                "button_settings": int(self.button_settings_var.get()),
                "button_prev_tab": int(self.button_prev_tab_var.get()),
                "button_next_tab": int(self.button_next_tab_var.get())
            }
            save_config()
            messagebox.showinfo("Success", "Joystick settings saved successfully.")
            self.root.master.lift()  # Keep Settings window in focus
            self.root.destroy()
        except ValueError:
            messagebox.showerror("Error", "All joystick configuration values must be valid numbers.")

    def restore_defaults(self):
        global JOYSTICK_CONFIG
        JOYSTICK_CONFIG = DEFAULT_CONFIG["joystick_config"]
        self.axis_y_var.set(str(JOYSTICK_CONFIG["axis_y"]))
        self.hat_scroll_cooldown_var.set(str(JOYSTICK_CONFIG["hat_scroll_cooldown"]))
        self.hat_fast_steps_var.set(str(JOYSTICK_CONFIG["hat_fast_steps"]))
        self.button_up_var.set(str(JOYSTICK_CONFIG["button_up"]))
        self.button_down_var.set(str(JOYSTICK_CONFIG["button_down"]))
        self.button_select_var.set(str(JOYSTICK_CONFIG["button_select"]))
        self.button_settings_var.set(str(JOYSTICK_CONFIG["button_settings"]))
        self.button_prev_tab_var.set(str(JOYSTICK_CONFIG["button_prev_tab"]))
        self.button_next_tab_var.set(str(JOYSTICK_CONFIG["button_next_tab"]))
        save_config()
        messagebox.showinfo("Success", "Default joystick settings restored.")
        self.root.master.lift()  # Keep Settings window in focus
        self.root.destroy()

class SettingsWindow:
    """Window for configuring RetroArch settings."""
    def __init__(self, root, parent_gui, active_tab_name):
        self.root = tk.Toplevel(root)
        self.root.title("Settings")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        self.parent_gui = parent_gui
        self.active_tab_name = active_tab_name

        try:
            icon_path = get_resource_path("icon.ico")
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception:
            pass

        self.retroarch_var = tk.StringVar(value=str(RETROARCH))
        self.retroarch_core_var = tk.StringVar(value=str(RETROARCH_CORE))

        self.create_widgets()
        self.root.lift()  # Ensure Settings window is in foreground

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=7)
        main_frame.pack(fill=tk.BOTH, expand=True)

        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(fill=tk.BOTH, expand=True, anchor="w")

        cmd_frame = ttk.Frame(fields_frame)
        cmd_frame.pack(fill=tk.X, pady=7, anchor="w")
        ttk.Label(cmd_frame, text="RetroArch Executable:", width=24).pack(side="left")
        ttk.Entry(cmd_frame, textvariable=self.retroarch_var, width=50).pack(side="left", padx=5)
        ttk.Button(cmd_frame, text="Browse...", command=self.browse_retroarch, padding=5).pack(side="right", padx=7)

        core_frame = ttk.Frame(fields_frame)
        core_frame.pack(fill=tk.X, pady=7, anchor="w")
        ttk.Label(core_frame, text="RetroArch Core:", width=24).pack(side="left")
        ttk.Entry(core_frame, textvariable=self.retroarch_core_var, width=50).pack(side="left", padx=5)
        ttk.Button(core_frame, text="Browse...", command=self.browse_retroarch_core, padding=5).pack(side="right", padx=7)

        update_frame = ttk.Frame(main_frame)
        update_frame.pack(fill=tk.X, pady=10)
        ttk.Button(update_frame, text="Update All ROMs", command=self.update_all_roms, padding=5).pack(anchor="center")

        info_label = ttk.Label(
            main_frame,
            text=(
                "FinalBurn Neo [Libretro] v1.0.1\n"
                "©2025, gegecom83@gmail.com"
            ),
            wraplength=550
        )
        info_label.pack(anchor="w", pady=7)
    
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(anchor="se", pady=7)
        ttk.Button(buttons_frame, text="Save", command=self.save_settings, padding=5).pack(side="right", padx=7)
        ttk.Button(buttons_frame, text="Reset Defaults", command=self.restore_defaults, padding=5).pack(side="right", padx=7)
        ttk.Button(buttons_frame, text="Joystick Settings", command=lambda: JoystickSettingsWindow(self.root, self.parent_gui), padding=5).pack(side="right", padx=7)
        ttk.Button(buttons_frame, text="Generate ROM Titles", command=self.open_rom_titles_generator, padding=5).pack(side="right", padx=7)

    def browse_retroarch(self):
        filename = filedialog.askopenfilename(title="Select RetroArch Executable", filetypes=[("Executable Files", "*.exe")])
        if filename:
            self.retroarch_var.set(filename)

    def browse_retroarch_core(self):
        filename = filedialog.askopenfilename(title="Select RetroArch Core", filetypes=[("DLL Files", "*.dll")])
        if filename:
            self.retroarch_core_var.set(filename)

    def save_settings(self):
        global RETROARCH, RETROARCH_CORE
        RETROARCH = Path(self.retroarch_var.get())
        RETROARCH_CORE = Path(self.retroarch_core_var.get())
        save_config()
        messagebox.showinfo("Success", "Settings saved successfully.")
        self.root.lift()

    def restore_defaults(self):
        global RETROARCH, RETROARCH_CORE, INPUT_TYPES, ROMS_DIRS, OUTPUT_DIRS, JOYSTICK_CONFIG
        reset_to_defaults()
        self.retroarch_var.set(str(RETROARCH))
        self.retroarch_core_var.set(str(RETROARCH_CORE))
        save_config()
        messagebox.showinfo("Success", "Default settings restored.")
        self.root.lift()

    def open_rom_titles_generator(self):
        RomTitlesGenerator(self.root, self.parent_gui, self.active_tab_name)

    def update_all_roms(self):
        """Update ROM title files and lists for all tabs."""
        updated_tabs = []
        errors = []
        ignore_keys = ["cdromsystemcard", "supercdromsystemcard", "gamesexpresscdcard", "artisttool"]

        for config in TAB_CONFIGS:
            tab_name = config["name"]
            rom_titles_file = config["rom_titles_file"]
            roms_dir = Path(ROMS_DIRS.get(tab_name, config["roms_dir"]))
            input_file = INPUT_TYPES.get(tab_name, "")
            output_dir = Path(OUTPUT_DIRS.get(tab_name, str(get_base_dir())))
            output_file = output_dir / rom_titles_file.name

            # Ensure output directory exists
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"{tab_name}: Cannot create output directory {output_dir}: {e}")
                continue

            if not roms_dir.exists():
                errors.append(f"{tab_name}: ROM directory {roms_dir} does not exist.")
                continue

            try:
                # Generate title file
                if input_file and os.path.exists(input_file):
                    try:
                        tree = ET.parse(input_file)
                        root = tree.getroot()
                        with open(output_file, "w", encoding="utf-8") as f:
                            for game in root.findall(".//game"):
                                rom_key = game.get("name")
                                if rom_key is None or rom_key.lower() in ignore_keys:
                                    continue
                                description = game.find("description")
                                if description is None or description.text is None or description.text.strip().lower() in {"", "untitled"}:
                                    continue
                                rom_name = description.text.strip()
                                year = game.find("year").text.strip() if game.find("year") is not None and game.find("year").text else None
                                developer = game.find("manufacturer").text.strip() if game.find("manufacturer") is not None and game.find("manufacturer").text else None
                                if year is None or developer is None:
                                    continue
                                cleaned_key = rom_key.lower().replace(" ", "").replace("-", "").replace("'", "").replace(".", "")
                                f.write(f'{cleaned_key} "{rom_name}" {year} {developer}\n')
                    except ET.ParseError:
                        errors.append(f"{tab_name}: Invalid XML file {input_file}.")
                        continue
                else:
                    roms = [f for f in roms_dir.rglob('*') if f.is_file() and f.suffix.lower() in {'.zip', '.7z', '.cue'}]
                    if not roms:
                        errors.append(f"{tab_name}: No ROM files found in {roms_dir}.")
                        continue
                    with open(output_file, "w", encoding="utf-8") as f:
                        for rom in roms:
                            rom_key = rom.stem.lower().replace(" ", "").replace("-", "").replace("'", "").replace(".", "")
                            rom_name = rom.stem
                            f.write(f'{rom_key} "{rom_name}"\n')

                # Update the tab content
                if tab_name in self.parent_gui.tab_contents:
                    content = self.parent_gui.tab_contents[tab_name]
                    content.roms_dir = roms_dir
                    content.rom_titles_file = rom_titles_file
                    content.refresh_cache()
                    content.update_list()
                    updated_tabs.append(tab_name)

            except PermissionError:
                errors.append(f"{tab_name}: Permission denied writing to {output_file}.")
            except Exception as e:
                errors.append(f"{tab_name}: Error processing ROM titles: {e}")

        if updated_tabs:
            messagebox.showinfo("Success", f"ROM titles and lists updated for: {', '.join(updated_tabs)}")
        if errors:
            messagebox.showwarning("Warnings", "\n".join(errors))
        if not updated_tabs and not errors:
            messagebox.showwarning("Warning", "No valid ROM directories or files found to update.")
        self.root.lift()

class RomTitlesGenerator:
    """Window for generating ROM titles file."""
    def __init__(self, root, parent_gui, active_tab_name):
        self.root = tk.Toplevel(root)
        self.root.title("ROM Titles Extractor")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        self.parent_gui = parent_gui
        self.active_tab_name = active_tab_name
        self.active_config = next((config for config in TAB_CONFIGS if config["name"] == active_tab_name), TAB_CONFIGS[0])

        try:
            icon_path = get_resource_path("icon.ico")
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception:
            pass

        self.input_file = tk.StringVar(value=INPUT_TYPES.get(active_tab_name, ""))
        self.output_dir = tk.StringVar(value=OUTPUT_DIRS.get(active_tab_name, str(get_base_dir())))
        self.output_file_name = tk.StringVar(value=str(self.active_config["rom_titles_file"].name))
        self.roms_dir_var = tk.StringVar(value=ROMS_DIRS.get(active_tab_name, str(self.active_config["roms_dir"])))

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=7)
        main_frame.pack(fill=tk.BOTH, expand=True)

        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(fill=tk.BOTH, expand=True, anchor="w")

        roms_frame = ttk.Frame(fields_frame)
        roms_frame.pack(fill=tk.X, pady=7, anchor="w")
        ttk.Label(roms_frame, text="ROMs Directory:", width=24).pack(side="left")
        ttk.Entry(roms_frame, textvariable=self.roms_dir_var, width=50).pack(side="left", padx=5)
        ttk.Button(roms_frame, text="Browse...", command=self.browse_roms_dir, padding=5).pack(side="right", padx=7)

        input_frame = ttk.Frame(fields_frame)
        input_frame.pack(fill=tk.X, pady=7, anchor="w")
        ttk.Label(input_frame, text="Input XML File (Optional):", width=24).pack(side="left")
        ttk.Entry(input_frame, textvariable=self.input_file, width=50).pack(side="left", padx=5)
        ttk.Button(input_frame, text="Browse...", command=self.browse_input, padding=5).pack(side="right", padx=7)

        output_dir_frame = ttk.Frame(fields_frame)
        output_dir_frame.pack(fill=tk.X, pady=7, anchor="w")
        ttk.Label(output_dir_frame, text="Output Directory:", width=24).pack(side="left")
        ttk.Entry(output_dir_frame, textvariable=self.output_dir, width=50, state="disabled").pack(side="left", padx=5)

        output_file_frame = ttk.Frame(fields_frame)
        output_file_frame.pack(fill=tk.X, pady=7, anchor="w")
        ttk.Label(output_file_frame, text="Output File Name:", width=24).pack(side="left")
        ttk.Entry(output_file_frame, textvariable=self.output_file_name, width=50, state="disabled").pack(side="left", padx=5)

        info_label = ttk.Label(
            main_frame,
            text=(
                "Only ROMs (.zip, .7z, .cue) are searched in the tab's directory and its subdirectories.\n"
                "For .cue ROMs, the --subsystem neocd argument is automatically added for Neo Geo CD support."
            ),
            wraplength=550
        )
        info_label.pack(anchor="w", pady=7)

        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(anchor="se", pady=7)
        ttk.Button(buttons_frame, text="OK", command=self.process_files, padding=5).pack(side="right", padx=7)
        ttk.Button(buttons_frame, text="Cancel", command=self.root.destroy, padding=5).pack(side="right", padx=7)
        ttk.Button(buttons_frame, text="Extract Titles", command=self.process_files, padding=5).pack(side="right", padx=7)

    def browse_roms_dir(self):
        directory = filedialog.askdirectory(title="Select ROMs Directory")
        if directory:
            self.roms_dir_var.set(directory)
            ROMS_DIRS[self.active_tab_name] = directory
            save_config()
            for tab_name, content in self.parent_gui.tab_contents.items():
                if tab_name == self.active_tab_name:
                    content.roms_dir = Path(directory)
                    content.refresh_cache()
                    content.update_list()
                    break

    def browse_input(self):
        filename = filedialog.askopenfilename(title="Select XML File", filetypes=[("XML Files", "*.xml *.dat")])
        if filename:
            self.input_file.set(filename)
            INPUT_TYPES[self.active_tab_name] = filename
            save_config()

    def process_files(self):
        """Generate ROM titles file from XML or directory scan."""
        input_file = self.input_file.get()
        output_dir = self.output_dir.get()
        output_file_name = self.output_file_name.get().strip()

        if not output_dir or not output_file_name:
            messagebox.showerror("Error", "Please select an output directory and specify an output file name.")
            return

        if not output_file_name.endswith(".txt"):
            output_file_name += ".txt"

        output_file = os.path.join(output_dir, output_file_name)
        roms_dir = Path(self.roms_dir_var.get())
        ignore_keys = ["cdromsystemcard", "supercdromsystemcard", "gamesexpresscdcard", "artisttool"]

        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            if input_file:
                if not os.path.exists(input_file):
                    messagebox.showerror("Error", f"The file {input_file} does not exist.")
                    return
                tree = ET.parse(input_file)
                root = tree.getroot()
                with open(output_file, "w", encoding="utf-8") as f:
                    for game in root.findall(".//game"):
                        rom_key = game.get("name")
                        if rom_key is None or rom_key.lower() in ignore_keys:
                            continue
                        description = game.find("description")
                        if description is None or description.text is None or description.text.strip().lower() in {"", "untitled"}:
                            continue
                        rom_name = description.text.strip()
                        year = game.find("year").text.strip() if game.find("year") is not None and game.find("year").text else None
                        developer = game.find("manufacturer").text.strip() if game.find("manufacturer") is not None and game.find("manufacturer").text else None
                        if year is None or developer is None:
                            continue
                        cleaned_key = rom_key.lower().replace(" ", "").replace("-", "").replace("'", "").replace(".", "")
                        f.write(f'{cleaned_key} "{rom_name}" {year} {developer}\n')
            else:
                if not roms_dir.exists():
                    messagebox.showerror("Error", f"The ROMs directory {roms_dir} does not exist.")
                    return
                roms = [f for f in roms_dir.rglob('*') if f.is_file() and f.suffix.lower() in {'.zip', '.7z', '.cue'}]
                if not roms:
                    messagebox.showerror("Error", f"No ROM files found in {roms_dir}.")
                    return
                with open(output_file, "w", encoding="utf-8") as f:
                    for rom in roms:
                        rom_key = rom.stem.lower().replace(" ", "").replace("-", "").replace("'", "").replace(".", "")
                        rom_name = rom.stem
                        f.write(f'{rom_key} "{rom_name}"\n')

            messagebox.showinfo("Success", f"File {output_file} created successfully.")
            for tab_name, content in self.parent_gui.tab_contents.items():
                if str(content.rom_titles_file) == output_file_name or content.roms_dir == roms_dir:
                    content.refresh_cache()
                    content.update_list()
                    break
            self.root.master.lift()
            self.root.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Error processing files: {e}")

class TabContent:
    """Content for each tab in the GUI."""
    def __init__(self, parent, rom_titles_file: Path, roms_dir: Path, root, gui, tab_names: List[str], tab_name: str):
        self.rom_titles_file = rom_titles_file
        self.roms_dir = Path(ROMS_DIRS.get(tab_name, roms_dir))
        self.root = root
        self.gui = gui
        self.tab_names = tab_names
        self.roms = []
        self.cached_roms = []

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.update_list)

        self.frame_top = ttk.Frame(parent, padding=10)
        self.frame_top.pack(fill="x")

        ttk.Label(self.frame_top, text="Search:").pack(side="left")
        self.entry_search = ttk.Entry(self.frame_top, textvariable=self.search_var, width=30)
        self.entry_search.pack(side="left", padx=(5, 10))

        self.tab_var = tk.StringVar(value=tab_name)
        self.tab_menu = ttk.OptionMenu(self.frame_top, self.tab_var, tab_name, *tab_names, command=self.gui.switch_tab)
        self.tab_menu.pack(side="left", padx=(0, 10))

        self.button_settings = ttk.Button(self.frame_top, text="Settings", command=lambda: SettingsWindow(self.root, self.gui, tab_name), width=15)
        self.button_settings.pack(side="right")

        self.rom_count_var = tk.StringVar()
        self.rom_count_label = ttk.Label(parent, textvariable=self.rom_count_var)
        self.rom_count_label.pack(fill="x", padx=10, pady=(0, 5))

        listbox_frame = ttk.Frame(parent)
        listbox_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.listbox = tk.Listbox(listbox_frame, height=15, activestyle='none')
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar_vert = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.listbox.yview)
        scrollbar_vert.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar_vert.set)

        scrollbar_horiz = ttk.Scrollbar(parent, orient="horizontal", command=self.listbox.xview)
        scrollbar_horiz.pack(fill="x", padx=10, pady=(0, 5))
        self.listbox.config(xscrollcommand=scrollbar_horiz.set)

        self.listbox.bind("<Double-Button-1>", lambda event: self.launch_selected())
        self.listbox.bind("<Return>", lambda event: self.launch_selected())

        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", padx=10, pady=5)

        self.fullscreen_text = tk.StringVar(value="Toggle Fullscreen Mode: <Fn + F11>" if not self.gui.is_fullscreen else "Toggle Desktop Mode: <Fn + F11>")
        self.fullscreen_label = ttk.Label(
            button_frame,
            textvariable=self.fullscreen_text,
            font=("TkDefaultFont", 8)
        )
        self.fullscreen_label.pack(side="left")

        self.refresh_cache()
        self.update_list()

    def refresh_cache(self):
        """Refresh the cached ROM list."""
        self.cached_roms = get_rom_list(self.rom_titles_file, self.roms_dir)

    def update_list(self, *args):
        """Update the listbox with filtered ROMs from cache."""
        search_term = self.search_var.get().lower()
        self.roms = [
            rom for rom in self.cached_roms
            if not search_term or search_term in rom[1].lower()
        ]
        self.listbox.delete(0, tk.END)
        if not self.roms and self.cached_roms:
            self.listbox.insert(tk.END, "No ROMs found. Some ROMs may have been skipped due to invalid titles.")
        elif not self.roms:
            self.listbox.insert(tk.END, "No ROMs found.")
        else:
            for _, title in self.roms:
                self.listbox.insert(tk.END, title)
        self.rom_count_var.set(f"Number of ROMs: {len(self.roms)}")

    def launch_selected(self):
        """Launch the selected ROM."""
        selection = self.listbox.curselection()
        if not selection or not self.roms:
            messagebox.showwarning("Warning", "Please select a ROM.")
            return
        index = selection[0]
        rom_name = self.roms[index][0]
        run_rom(rom_name, self.roms_dir)

class FBNeoGUI:
    """Main GUI for FinalBurn Neo ROM launcher."""
    def __init__(self, root):
        self.root = root
        self.root.title("FinalBurn Neo [Libretro] • Select Game")
        self.root.geometry("640x480")
        self.root.resizable(True, True)

        pygame.init()
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(0) if pygame.joystick.get_count() > 0 else None
        if self.joystick:
            self.joystick.init()
        self.last_button_state = {}
        self.last_hat_x_state = 0
        self.last_hat_y_state = 0
        self.last_hat_x_move_time = 0
        self.last_hat_y_move_time = 0
        self.no_axes_warning_shown = False

        try:
            icon_path = get_resource_path("icon.ico")
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception:
            pass

        self.is_fullscreen = False
        self.root.bind("<F11>", self.toggle_fullscreen)

        self.content_frame = ttk.Frame(self.root)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tab_frames = {}
        self.tab_contents = {}
        tab_names = [config["name"] for config in TAB_CONFIGS]
        self.current_tab = TAB_CONFIGS[0]["name"]
        for config in TAB_CONFIGS:
            tab_frame = ttk.Frame(self.content_frame)
            tab_content = TabContent(tab_frame, config["rom_titles_file"], config["roms_dir"], self.root, self, tab_names, config["name"])
            self.tab_frames[config["name"]] = tab_frame
            self.tab_contents[config["name"]] = tab_content

        self.tab_frames[TAB_CONFIGS[0]["name"]].pack(fill=tk.BOTH, expand=True)
        self.poll_joystick()

    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode."""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)
        for content in self.tab_contents.values():
            content.fullscreen_text.set("Toggle Fullscreen Mode: <Fn + F11>" if not self.is_fullscreen else "Toggle Desktop Mode: <Fn + F11>")

    def switch_tab(self, tab_name: str):
        """Switch to the specified tab."""
        for frame in self.tab_frames.values():
            frame.pack_forget()
        self.tab_frames[tab_name].pack(fill=tk.BOTH, expand=True)
        for content in self.tab_contents.values():
            content.tab_var.set(tab_name)
        self.current_tab = tab_name

    def poll_joystick(self):
        """Poll joystick inputs for navigation."""
        if not self.joystick:
            self.root.after(20, self.poll_joystick)
            return

        try:
            pygame.event.pump()
            current_listbox = self.tab_contents[self.current_tab].listbox
            current_time = time.time()
            num_axes = self.joystick.get_numaxes()
            axis_y_index = JOYSTICK_CONFIG.get("axis_y", -1)
            if num_axes > 0 and axis_y_index >= 0 and axis_y_index < num_axes:
                axis_y = self.joystick.get_axis(axis_y_index)
                steps = 1
                cooldown = JOYSTICK_CONFIG.get("hat_scroll_cooldown", 0.02)
                if current_time - self.last_hat_y_move_time > cooldown:
                    if axis_y < -0.5:
                        current_selection = current_listbox.curselection()
                        new_index = max(0, current_selection[0] - steps) if current_selection else 0
                        current_listbox.selection_clear(0, tk.END)
                        current_listbox.selection_set(new_index)
                        current_listbox.see(new_index)
                        self.last_hat_y_move_time = current_time
                    elif axis_y > 0.5:
                        current_selection = current_listbox.curselection()
                        new_index = min(current_listbox.size() - 1, current_selection[0] + steps) if current_selection else 0
                        current_listbox.selection_clear(0, tk.END)
                        current_listbox.selection_set(new_index)
                        self.last_hat_y_move_time = current_time
            else:
                if not self.no_axes_warning_shown:
                    self.no_axes_warning_shown = True

            num_hats = self.joystick.get_numhats()
            if num_hats > 0:
                hat_value = self.joystick.get_hat(0)
                cooldown = JOYSTICK_CONFIG.get("hat_scroll_cooldown", 0.02)
                steps = JOYSTICK_CONFIG.get("hat_fast_steps", 5)
                if hat_value[1] != self.last_hat_y_state and current_time - self.last_hat_y_move_time > cooldown:
                    if hat_value[1] == 1:
                        current_selection = current_listbox.curselection()
                        new_index = max(0, current_selection[0] - 1) if current_selection else 0
                        current_listbox.selection_clear(0, tk.END)
                        current_listbox.selection_set(new_index)
                        current_listbox.see(new_index)
                        self.last_hat_y_move_time = current_time
                    elif hat_value[1] == -1:
                        current_selection = current_listbox.curselection()
                        new_index = min(current_listbox.size() - 1, current_selection[0] + 1) if current_selection else 0
                        current_listbox.selection_clear(0, tk.END)
                        current_listbox.selection_set(new_index)
                        current_listbox.see(new_index)
                        self.last_hat_y_move_time = current_time
                    self.last_hat_y_state = hat_value[1]
                if current_time - self.last_hat_x_move_time > cooldown:
                    if hat_value[0] == 1:
                        current_selection = current_listbox.curselection()
                        new_index = min(current_listbox.size() - 1, current_selection[0] + steps) if current_selection else 0
                        current_listbox.selection_clear(0, tk.END)
                        current_listbox.selection_set(new_index)
                        current_listbox.see(new_index)
                        self.last_hat_x_move_time = current_time
                    elif hat_value[0] == -1:
                        current_selection = current_listbox.curselection()
                        new_index = max(0, current_selection[0] - steps) if current_selection else 0
                        current_listbox.selection_clear(0, tk.END)
                        current_listbox.selection_set(new_index)
                        current_listbox.see(new_index)
                        self.last_hat_x_move_time = current_time
                    self.last_hat_x_state = hat_value[0]

            def navigate_up():
                current_selection = current_listbox.curselection()
                new_index = max(0, current_selection[0] - 1) if current_selection else 0
                current_listbox.selection_clear(0, tk.END)
                current_listbox.selection_set(new_index)
                current_listbox.see(new_index)

            def navigate_down():
                current_selection = current_listbox.curselection()
                new_index = min(current_listbox.size() - 1, current_selection[0] + 1) if current_selection else 0
                current_listbox.selection_clear(0, tk.END)
                current_listbox.selection_set(new_index)
                current_listbox.see(new_index)

            def check_button(button_index, action, action_name):
                if button_index < 0 or button_index >= self.joystick.get_numbuttons():
                    return
                current_state = self.joystick.get_button(button_index)
                if current_state and not self.last_button_state.get(button_index, 0):
                    action()
                self.last_button_state[button_index] = current_state

            check_button(JOYSTICK_CONFIG.get("button_up", 2), navigate_up, "navigate_up")
            check_button(JOYSTICK_CONFIG.get("button_down", 3), navigate_down, "navigate_down")
            check_button(JOYSTICK_CONFIG.get("button_select", 0), self.tab_contents[self.current_tab].launch_selected, "launch_selected")
            check_button(JOYSTICK_CONFIG.get("button_settings", 7), lambda: SettingsWindow(self.root, self, self.current_tab), "open_settings")
            check_button(JOYSTICK_CONFIG.get("button_prev_tab", 4), lambda: self.switch_tab(TAB_CONFIGS[(TAB_CONFIGS.index(next(config for config in TAB_CONFIGS if config["name"] == self.current_tab)) - 1) % len(TAB_CONFIGS)]["name"]), "prev_tab")
            check_button(JOYSTICK_CONFIG.get("button_next_tab", 5), lambda: self.switch_tab(TAB_CONFIGS[(TAB_CONFIGS.index(next(config for config in TAB_CONFIGS if config["name"] == self.current_tab)) + 1) % len(TAB_CONFIGS)]["name"]), "next_tab")

        except Exception as e:
            messagebox.showerror("Error", f"Joystick error: {e}")

        self.root.after(20, self.poll_joystick)

if __name__ == "__main__":
    if os.name == 'nt':
        root = tk.Tk()
        app = FBNeoGUI(root)
        root.mainloop()
    else:
        messagebox.showerror("Error", "Only runs on Windows.")