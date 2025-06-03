import sys
import os
import subprocess
import json
import time
from pathlib import Path
import xml.etree.ElementTree as ET

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QLineEdit, QPushButton, QLabel, QFileDialog, QMessageBox,
    QDialog, QFormLayout, QComboBox, QGroupBox, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon

import pygame

TAB_CONFIGS = [
    {"name": "Arcade", "rom_titles_file": "rom_titles_arcade.txt"},
    {"name": "CBS ColecoVision", "rom_titles_file": "rom_titles_coleco.txt"},
    {"name": "Fairchild ChannelF", "rom_titles_file": "rom_titles_channelf.txt"},
    {"name": "MSX 1", "rom_titles_file": "rom_titles_msx.txt"},
    {"name": "Nec PC-Engine", "rom_titles_file": "rom_titles_pce.txt"},
    {"name": "Nec SuperGrafX", "rom_titles_file": "rom_titles_sgx.txt"},
    {"name": "Nec TurboGrafx-16", "rom_titles_file": "rom_titles_tg16.txt"},
    {"name": "Nintendo Entertainment System", "rom_titles_file": "rom_titles_nes.txt"},
    {"name": "Nintendo Family Disk System", "rom_titles_file": "rom_titles_fds.txt"},
    {"name": "Super Nintendo Entertainment System", "rom_titles_file": "rom_titles_snes.txt"},
    {"name": "Sega GameGear", "rom_titles_file": "rom_titles_gamegear.txt"},
    {"name": "Sega Master System", "rom_titles_file": "rom_titles_sms.txt"},
    {"name": "Sega Megadrive", "rom_titles_file": "rom_titles_megadrive.txt"},
    {"name": "Sega SG-1000", "rom_titles_file": "rom_titles_sg1000.txt"},
    {"name": "SNK Neo-Geo Pocket", "rom_titles_file": "rom_titles_ngp.txt"},
    {"name": "SNK Neo-Geo CD", "rom_titles_file": "rom_titles_neocd.txt"},
    {"name": "ZX Spectrum", "rom_titles_file": "rom_titles_spectrum.txt"}
]

CONFIG_FILE = Path("config.json")
DEFAULT_CONFIG = {
    "RETROARCH": "",
    "RETROARCH_CORE": "",
    "roms_dirs": {config["name"]: "" for config in TAB_CONFIGS},
    "xml_dat_files": {config["name"]: "" for config in TAB_CONFIGS},
    "joystick_config": {
        "hat_scroll_cooldown": 0.02,
        "hat_fastest_steps": 30,
        "hat_fastest_delay": 0.5,
        "button_up": 2,
        "button_down": 3,
        "button_select": 0,
        "button_settings": 7,
        "button_prev_tab": 4,
        "button_next_tab": 5
    }
}

def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        jc = cfg.get("joystick_config", {})
        if "hat_fastest_steps" not in jc:
            jc["hat_fastest_steps"] = 30
        if "hat_fastest_delay" not in jc:
            jc["hat_fastest_delay"] = 0.5
        cfg["joystick_config"] = jc
        if "xml_dat_files" not in cfg:
            cfg["xml_dat_files"] = {config["name"]: "" for config in TAB_CONFIGS}
        return cfg
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4)

def load_rom_titles(filename: str):
    rom_titles = {}
    if not os.path.exists(filename):
        return rom_titles
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split(maxsplit=1)
            if len(parts) >= 2:
                key = parts[0].lower()
                title = parts[1].strip('"')
                if not title or title.lower() in {"untitled", "unknown", "no title"}:
                    continue
                rom_titles[key] = title
    return rom_titles

def parse_dat_metadata(xml_path):
    meta = {}
    if not xml_path or not os.path.exists(xml_path):
        return meta
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        for entry in root.findall(".//game") + root.findall(".//machine"):
            name = entry.attrib.get("name") or entry.attrib.get("romname") or ""
            title_node = entry.find("description")
            year_node = entry.find("year")
            manuf_node = entry.find("manufacturer")
            title = title_node.text.strip() if title_node is not None and title_node.text else name
            year = year_node.text.strip() if year_node is not None and year_node.text else ""
            manuf = manuf_node.text.strip() if manuf_node is not None and manuf_node.text else ""
            if name:
                meta[name.lower()] = (title, year, manuf)
    except Exception as e:
        print(f"Failed to parse {xml_path}: {e}")
    return meta

def auto_create_rom_titles(roms_dir, xml_path, system_name, rom_titles_file):
    roms = []
    if system_name == "SNK Neo-Geo CD":
        for root, dirs, files in os.walk(roms_dir):
            for f in files:
                if f.lower().endswith('.cue'):
                    rel_path = os.path.relpath(os.path.join(root, f), roms_dir)
                    roms.append(rel_path)
    else:
        roms = [
            f for f in os.listdir(roms_dir)
            if os.path.isfile(os.path.join(roms_dir, f)) and f.lower().endswith(('.zip', '.7z', '.cue'))
        ]
    rom_bases = [Path(f).stem.lower() for f in roms]
    meta = parse_dat_metadata(xml_path) if xml_path else {}
    lines = []
    for rom, base in zip(roms, rom_bases):
        if base in meta:
            title, year, manuf = meta[base]
            lines.append(f"{base} \"{title}\" \"{year}\" \"{manuf}\"")
        else:
            lines.append(f"{base} \"{base}\"")
    try:
        with open(rom_titles_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return True, len(lines)
    except Exception as e:
        return False, str(e)

def get_rom_list_cached(rom_titles_file, roms_dir, system_name, xml_dat_file, cache_dict):
    cache_key = (roms_dir, system_name, xml_dat_file)
    cache = cache_dict.get(cache_key)
    if cache is not None:
        return cache
    rom_titles = load_rom_titles(rom_titles_file)
    meta = parse_dat_metadata(xml_dat_file) if xml_dat_file else {}
    if not roms_dir or not os.path.exists(roms_dir):
        cache_dict[cache_key] = []
        return []
    roms = []
    if system_name == "SNK Neo-Geo CD":
        for root, dirs, files in os.walk(roms_dir):
            for f in files:
                if f.lower().endswith('.cue'):
                    rel_path = os.path.relpath(os.path.join(root, f), roms_dir)
                    roms.append(rel_path)
    else:
        roms = [
            f for f in os.listdir(roms_dir)
            if os.path.isfile(os.path.join(roms_dir, f)) and f.lower().endswith(('.zip', '.7z', '.cue'))
        ]
    rom_list = []
    for rom in roms:
        stem = Path(rom).stem
        if system_name == "SNK Neo-Geo CD":
            if stem.lower() in meta:
                title, year, manuf = meta[stem.lower()]
            else:
                title = rom_titles.get(stem.lower(), stem)
                year = ""
                manuf = ""
            rom_list.append((rom, title, year, manuf))
        else:
            if meta and stem.lower() not in meta:
                continue
            if stem.lower() in meta:
                title, year, manuf = meta[stem.lower()]
            else:
                title = rom_titles.get(stem.lower(), stem)
                year = ""
                manuf = ""
            rom_list.append((rom, title, year, manuf))
    rom_list_sorted = sorted(rom_list, key=lambda x: x[1].lower())
    cache_dict[cache_key] = rom_list_sorted
    return rom_list_sorted

def filter_rom_list(rom_list, search="", year_filter="", manuf_filter=""):
    filtered = []
    for rom, title, year, manuf in rom_list:
        if year_filter and year_filter not in year:
            continue
        if manuf_filter and manuf_filter.lower() not in manuf.lower():
            continue
        if not search or search in title.lower():
            filtered.append((rom, title, year, manuf))
    return filtered

def run_rom(rom, roms_dir, retroarch, core, system_name, win):
    rom_path = os.path.join(roms_dir, rom)
    if not os.path.exists(rom_path):
        QMessageBox.critical(win, "Error", f"ROM file not found: {rom_path}")
        return
    # --- CROSS-PLATFORM EXECUTABLE CHECK ---
    if not os.path.exists(retroarch) or not os.access(retroarch, os.X_OK):
        QMessageBox.critical(win, "Error", f"Invalid RetroArch executable: {retroarch}")
        return
    # --- CROSS-PLATFORM CORE CHECK ---
    if not os.path.exists(core):
        QMessageBox.critical(win, "Error", f"Invalid RetroArch core: {core}")
        return
    if not (core.lower().endswith(".dll") or core.lower().endswith(".so") or core.lower().endswith(".dylib")):
        QMessageBox.critical(
            win,
            "Error",
            f"Core file must end with .dll (Windows), .so (Linux), or .dylib (macOS): {core}"
        )
        return
    cmd = [retroarch, "-L", core]
    if system_name == "SNK Neo-Geo CD" or rom.lower().endswith(".cue"):
        cmd.extend(["--subsystem", "neocd"])
    cmd.append(rom_path)
    try:
        subprocess.Popen(cmd)
    except Exception as e:
        QMessageBox.critical(win, "Error", f"Failed to launch ROM: {e}")

class SettingsDialog(QDialog):
    def __init__(self, cfg, parent, current_system_callback, auto_create_titles_callback, update_rom_list_callback):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.cfg = cfg
        self.current_system_callback = current_system_callback
        self.auto_create_titles_callback = auto_create_titles_callback
        self.update_rom_list_callback = update_rom_list_callback

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        main_widget = QWidget()
        scroll.setWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # General group
        general_group = QGroupBox("General")
        general_layout = QFormLayout()
        self.retroarch_edit = QLineEdit(str(cfg["RETROARCH"]))
        self.retroarch_btn = QPushButton("Choose…")
        self.retroarch_btn.setMaximumWidth(80)
        self.retroarch_btn.clicked.connect(self.choose_retroarch)
        retroarch_row = QHBoxLayout()
        retroarch_row.addWidget(self.retroarch_edit)
        retroarch_row.addWidget(self.retroarch_btn)

        self.core_edit = QLineEdit(str(cfg["RETROARCH_CORE"]))
        self.core_btn = QPushButton("Choose…")
        self.core_btn.setMaximumWidth(80)
        self.core_btn.clicked.connect(self.choose_core)
        core_row = QHBoxLayout()
        core_row.addWidget(self.core_edit)
        core_row.addWidget(self.core_btn)
        # Add a hint label under the RetroArch Core field
        core_hint = QLabel("(RetroArch/cores/fbneo_libretro*.dll/*.so)")
        core_hint.setStyleSheet("color: gray; font-size: 10pt; margin-bottom: 6px;")
        core_hint.setContentsMargins(0, 0, 0, 4)

        general_layout.addRow("RetroArch Executable:", retroarch_row)
        general_layout.addRow("RetroArch Core:", core_row)
        general_layout.addRow("", core_hint)
        general_group.setLayout(general_layout)

        # Joystick group
        joystick_group = QGroupBox("Joystick Buttons")
        joystick_layout = QFormLayout()
        jc = cfg["joystick_config"]
        self.hat_scroll_cooldown = QLineEdit(str(jc.get("hat_scroll_cooldown", 0.02)))
        self.hat_fastest_steps = QLineEdit(str(jc.get("hat_fastest_steps", 30)))
        self.hat_fastest_delay = QLineEdit(str(jc.get("hat_fastest_delay", 0.5)))
        self.button_up = QLineEdit(str(jc.get("button_up", 2)))
        self.button_down = QLineEdit(str(jc.get("button_down", 3)))
        self.button_select = QLineEdit(str(jc.get("button_select", 0)))
        self.button_settings = QLineEdit(str(jc.get("button_settings", 7)))
        self.button_prev_tab = QLineEdit(str(jc.get("button_prev_tab", 4)))
        self.button_next_tab = QLineEdit(str(jc.get("button_next_tab", 5)))
        joystick_layout.addRow("Hat Scroll Cooldown (s):", self.hat_scroll_cooldown)
        joystick_layout.addRow("Hat Fastest Steps (hold):", self.hat_fastest_steps)
        joystick_layout.addRow("Hat Fastest Delay (s):", self.hat_fastest_delay)
        joystick_layout.addRow("Button Up Index:", self.button_up)
        joystick_layout.addRow("Button Down Index:", self.button_down)
        joystick_layout.addRow("Button Select Index:", self.button_select)
        joystick_layout.addRow("Button Settings Index:", self.button_settings)
        joystick_layout.addRow("Button Prev System Index:", self.button_prev_tab)
        joystick_layout.addRow("Button Next System Index:", self.button_next_tab)
        joystick_group.setLayout(joystick_layout)

        # System group with dropdown
        sys_group = QGroupBox("System")
        sys_layout = QFormLayout()
        self.sys_dropdown = QComboBox()
        self.sys_dropdown.addItems([config["name"] for config in TAB_CONFIGS])
        self.sys_dropdown.currentIndexChanged.connect(self.update_sys_fields)
        sys_layout.addRow("System:", self.sys_dropdown)

        self.rom_folder_edit = QLineEdit()
        self.rom_folder_btn = QPushButton("Choose…")
        self.rom_folder_btn.setMaximumWidth(80)
        self.rom_folder_btn.clicked.connect(self.choose_rom_folder)
        rom_folder_row = QHBoxLayout()
        rom_folder_row.addWidget(self.rom_folder_edit)
        rom_folder_row.addWidget(self.rom_folder_btn)
        sys_layout.addRow("ROMs Folder:", rom_folder_row)

        self.xml_file_edit = QLineEdit()
        self.xml_file_btn = QPushButton("Choose…")
        self.xml_file_btn.setMaximumWidth(80)
        self.xml_file_btn.clicked.connect(self.choose_xml_file)
        xml_file_row = QHBoxLayout()
        xml_file_row.addWidget(self.xml_file_edit)
        xml_file_row.addWidget(self.xml_file_btn)
        sys_layout.addRow("XML/DAT File:", xml_file_row)

        self.auto_titles_btn = QPushButton("Auto-create ROM Titles")
        self.auto_titles_btn.clicked.connect(self.auto_create_titles)
        sys_layout.addRow(self.auto_titles_btn)
        sys_group.setLayout(sys_layout)

        # Save button
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save)

        layout.addWidget(general_group)
        layout.addWidget(joystick_group)
        layout.addWidget(sys_group)
        layout.addWidget(self.save_btn)

        # Set scroll area as dialog layout
        dlg_layout = QVBoxLayout(self)
        dlg_layout.addWidget(scroll)
        self.setLayout(dlg_layout)

        self.update_sys_fields(self.sys_dropdown.currentIndex())

        self.setMinimumSize(460, 320)
        self.resize(640, min(595, QApplication.primaryScreen().availableGeometry().height()-80))

    def choose_retroarch(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Select RetroArch Executable", "", "All Files (*)")
        if fname:
            self.retroarch_edit.setText(fname)

    def choose_core(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Select RetroArch Core", "", "All Files (*)")
        if fname:
            self.core_edit.setText(fname)

    def update_sys_fields(self, idx):
        sys_name = self.sys_dropdown.currentText()
        self.rom_folder_edit.setText(str(self.cfg["roms_dirs"].get(sys_name, "")))
        self.xml_file_edit.setText(str(self.cfg["xml_dat_files"].get(sys_name, "")))

    def choose_rom_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select ROMs Folder")
        if folder:
            self.rom_folder_edit.setText(folder)

    def choose_xml_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Select XML/DAT File", "", "XML/DAT Files (*.xml *.dat);;All Files (*)")
        if fname:
            self.xml_file_edit.setText(fname)

    def auto_create_titles(self):
        sys_name = self.sys_dropdown.currentText()
        rom_folder = self.rom_folder_edit.text()
        xml_file = self.xml_file_edit.text()
        rom_titles_file = [c["rom_titles_file"] for c in TAB_CONFIGS if c["name"] == sys_name][0]
        if not rom_folder or not os.path.isdir(rom_folder):
            QMessageBox.warning(self, "Error", "Please set the ROMs folder for this system first.")
            return
        ok, info = auto_create_rom_titles(rom_folder, xml_file, sys_name, rom_titles_file)
        if ok:
            QMessageBox.information(self, "ROM Titles", f"Created/Updated {rom_titles_file} ({info} entries)")
            self.auto_create_titles_callback()
        else:
            QMessageBox.critical(self, "Write Error", f"Could not write file:\n{info}")

    def save(self):
        self.cfg["RETROARCH"] = self.retroarch_edit.text()
        self.cfg["RETROARCH_CORE"] = self.core_edit.text()
        jc = self.cfg["joystick_config"]
        try:
            jc["hat_scroll_cooldown"] = float(self.hat_scroll_cooldown.text())
            jc["hat_fastest_steps"] = int(self.hat_fastest_steps.text())
            jc["hat_fastest_delay"] = float(self.hat_fastest_delay.text())
            jc["button_up"] = int(self.button_up.text())
            jc["button_down"] = int(self.button_down.text())
            jc["button_select"] = int(self.button_select.text())
            jc["button_settings"] = int(self.button_settings.text())
            jc["button_prev_tab"] = int(self.button_prev_tab.text())
            jc["button_next_tab"] = int(self.button_next_tab.text())
        except Exception:
            pass
        # Save only the currently selected system's fields
        sys_name = self.sys_dropdown.currentText()
        self.cfg["roms_dirs"][sys_name] = self.rom_folder_edit.text()
        self.cfg["xml_dat_files"][sys_name] = self.xml_file_edit.text()
        save_config(self.cfg)
        self.update_rom_list_callback()
        self.accept()

# ----------- About Dialog ------------

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        layout = QVBoxLayout(self)
        label = QLabel(
            "FinalBurn Neo [Libretro] v1.0.1\n"
            "© 2025, gegecom83@gmail.com"
        )
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        self.setMinimumSize(350, 120)

# ----------- Main Window ------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FinalBurn Neo [Libretro] • Select Game")
        if sys.platform.startswith("win") and os.path.exists("icon.ico"):
            self.setWindowIcon(QIcon("icon.ico"))
        elif sys.platform.startswith("linux") and os.path.exists("icon.png"):
            self.setWindowIcon(QIcon("icon.png"))

        self.cfg = load_config()
        self.is_active = True

        self.systems_combo = QComboBox()
        self.systems_combo.addItems([c["name"] for c in TAB_CONFIGS])
        self.systems_combo.currentIndexChanged.connect(self.update_rom_list)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search ROMs...")
        self.search_edit.textChanged.connect(self.update_rom_list)

        self.year_edit = QLineEdit()
        self.year_edit.setPlaceholderText("Year")
        self.year_edit.setMaximumWidth(80)
        self.year_edit.textChanged.connect(self.update_rom_list)

        self.manuf_edit = QLineEdit()
        self.manuf_edit.setPlaceholderText("Manufacturer")
        self.manuf_edit.setMaximumWidth(150)
        self.manuf_edit.textChanged.connect(self.update_rom_list)

        self.roms_list = QListWidget()
        self.roms_list.itemDoubleClicked.connect(self.launch_selected_rom)
        self.roms_list.installEventFilter(self)

        self.rom_count_label = QLabel()
        self.rom_count_label.setSizePolicy(self.rom_count_label.sizePolicy().horizontalPolicy(), self.rom_count_label.sizePolicy().verticalPolicy())

        self.settings_btn = QPushButton("Settings")
        self.settings_btn.setMaximumWidth(80)
        self.settings_btn.setMinimumHeight(24)
        self.settings_btn.clicked.connect(self.show_settings)

        settings_row = QHBoxLayout()
        settings_row.addWidget(self.rom_count_label)
        settings_row.addStretch(1)
        settings_row.addWidget(self.settings_btn)

        layout = QVBoxLayout()
        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("System:"))
        top_row.addWidget(self.systems_combo)
        top_row.addWidget(QLabel("Search:"))
        top_row.addWidget(self.search_edit)
        top_row.addWidget(QLabel("Year:"))
        top_row.addWidget(self.year_edit)
        top_row.addWidget(QLabel("Manufacturer:"))
        top_row.addWidget(self.manuf_edit)
        layout.addLayout(top_row)
        layout.addWidget(self.roms_list)
        layout.addLayout(settings_row)
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

        self.roms = []
        self.rom_cache = {}
        self.update_rom_list()

        pygame.init()
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(0) if pygame.joystick.get_count() > 0 else None
        if self.joystick:
            self.joystick.init()
        self.last_hat = (0, 0)
        self.last_hat_move_time = time.time()
        self.last_hat_held = {"left": False, "right": False}
        self.last_hat_held_time = {"left": 0, "right": 0}
        self.last_button_state = {}
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll_joystick)
        self.timer.start(20)

        self.is_fullscreen = False
        self.installEventFilter(self)
        self.roms_list.installEventFilter(self)

        self.activateWindow()
        self.setFocusPolicy(Qt.StrongFocus)
        self.roms_list.setFocusPolicy(Qt.StrongFocus)
        self.roms_list.setFocus()

        self.adjust_main_window_size()

    def adjust_main_window_size(self):
        self.setMinimumSize(400, 320)
        self.resize(self.sizeHint())
        self.setMaximumSize(16777215, 16777215)  # Remove any max size restriction

    def show_about(self):
        dlg = AboutDialog(self)
        dlg.exec_()

    def eventFilter(self, obj, event):
        if event.type() == event.WindowActivate:
            self.is_active = True
        elif event.type() == event.WindowDeactivate:
            self.is_active = False
        if event.type() == event.KeyPress:
            if obj == self.roms_list and event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.launch_selected_rom()
                return True
            if event.key() == Qt.Key_F11:
                self.toggle_fullscreen()
                return True
            # TAB key opens About window unless focus is in a text input
            if event.key() == Qt.Key_Tab and not isinstance(self.focusWidget(), QLineEdit):
                self.show_about()
                return True
        return super().eventFilter(obj, event)

    def toggle_fullscreen(self):
        if self.is_fullscreen:
            self.showNormal()
            self.is_fullscreen = False
        else:
            self.showFullScreen()
            self.is_fullscreen = True

    def current_system(self):
        idx = self.systems_combo.currentIndex()
        sys_cfg = TAB_CONFIGS[idx]
        roms_dir = self.cfg["roms_dirs"].get(sys_cfg["name"], "")
        return sys_cfg, roms_dir

    def update_rom_list(self):
        sys_cfg = self.current_system()[0]
        sys_name = sys_cfg["name"]
        roms_dir = self.cfg["roms_dirs"].get(sys_name, "")
        rom_titles_file = sys_cfg["rom_titles_file"]
        search = self.search_edit.text().lower()
        xml_file = self.cfg["xml_dat_files"].get(sys_name, "")
        year_filter = self.year_edit.text().strip()
        manuf_filter = self.manuf_edit.text().strip()
        all_roms = get_rom_list_cached(
            rom_titles_file, roms_dir, sys_name, xml_file, self.rom_cache
        )
        self.roms = filter_rom_list(all_roms, search, year_filter, manuf_filter)
        self.roms_list.clear()
        for fn, title, year, manuf in self.roms:
            display = title
            if year or manuf:
                display += f" [{year}]" if year else ""
                display += f" ({manuf})" if manuf else ""
            self.roms_list.addItem(display)
        count = len(self.roms)
        self.rom_count_label.setText(f"ROMs found: {count}")
        if not self.roms_list.count():
            self.roms_list.addItem("No ROMs found.")

    def launch_selected_rom(self, *args):
        idx = self.roms_list.currentRow()
        if idx < 0 or not self.roms or self.roms_list.item(idx).text() == "No ROMs found.":
            QMessageBox.warning(self, "Warning", "Select a ROM.")
            return
        rom = self.roms[idx][0]
        sys_cfg = self.current_system()[0]
        sys_name = sys_cfg["name"]
        run_rom(rom, self.cfg["roms_dirs"].get(sys_name, ""), self.cfg["RETROARCH"], self.cfg["RETROARCH_CORE"], sys_name, self)

    def show_settings(self):
        dlg = SettingsDialog(
            self.cfg,
            self,
            self.current_system,
            self.clear_rom_cache_and_update,
            self.update_rom_list
        )
        dlg.exec_()
        self.update_rom_list()

    def clear_rom_cache_and_update(self):
        self.rom_cache.clear()
        self.update_rom_list()

    def poll_joystick(self):
        if not self.isActiveWindow() or not self.is_active:
            return
        if not self.joystick:
            return
        pygame.event.pump()
        jc = self.cfg["joystick_config"]
        fastest_steps = jc.get("hat_fastest_steps", 30)
        fastest_delay = jc.get("hat_fastest_delay", 0.5)
        now = time.time()
        list_widget = self.roms_list
        idx = list_widget.currentRow()
        size = list_widget.count()

        if self.joystick.get_numhats() > 0:
            hat = self.joystick.get_hat(0)
            # Up/down single step per press (no hold-to-scroll)
            if hat[1] == 1 and (self.last_hat[1] != 1):
                list_widget.setCurrentRow(max(0, idx - 1))
            elif hat[1] == -1 and (self.last_hat[1] != -1):
                list_widget.setCurrentRow(min(size - 1, idx + 1))
            # Left/right: fast/continuous scroll if held
            hat_left = hat[0] == -1
            hat_right = hat[0] == 1

            if hat_left:
                if not self.last_hat_held["left"]:
                    list_widget.setCurrentRow(max(0, idx - fastest_steps))
                    self.last_hat_held_time["left"] = now
                elif now - self.last_hat_held_time["left"] > fastest_delay:
                    list_widget.setCurrentRow(max(0, list_widget.currentRow() - fastest_steps))
                    self.last_hat_held_time["left"] = now - (fastest_delay - 0.05)
                elif now - self.last_hat_held_time["left"] > 0.2:
                    list_widget.setCurrentRow(max(0, list_widget.currentRow() - fastest_steps))
                    self.last_hat_held_time["left"] = now
                self.last_hat_held["left"] = True
            else:
                self.last_hat_held["left"] = False

            if hat_right:
                if not self.last_hat_held["right"]:
                    list_widget.setCurrentRow(min(size - 1, idx + fastest_steps))
                    self.last_hat_held_time["right"] = now
                elif now - self.last_hat_held_time["right"] > fastest_delay:
                    list_widget.setCurrentRow(min(size - 1, list_widget.currentRow() + fastest_steps))
                    self.last_hat_held_time["right"] = now - (fastest_delay - 0.05)
                elif now - self.last_hat_held_time["right"] > 0.2:
                    list_widget.setCurrentRow(min(size - 1, list_widget.currentRow() + fastest_steps))
                    self.last_hat_held_time["right"] = now
                self.last_hat_held["right"] = True
            else:
                self.last_hat_held["right"] = False

            self.last_hat = hat

        def check_button(btn_key, action):
            idx = jc.get(btn_key, -1)
            if idx < 0 or idx >= self.joystick.get_numbuttons():
                return
            pressed = self.joystick.get_button(idx)
            if pressed and not self.last_button_state.get(btn_key, False):
                action()
            self.last_button_state[btn_key] = pressed

        check_button("button_up", lambda: self.roms_list.setCurrentRow(max(0, self.roms_list.currentRow() - 1)))
        check_button("button_down", lambda: self.roms_list.setCurrentRow(min(self.roms_list.count() - 1, self.roms_list.currentRow() + 1)))
        check_button("button_select", self.launch_selected_rom)
        check_button("button_settings", self.show_settings)
        check_button("button_prev_tab", lambda: self.systems_combo.setCurrentIndex((self.systems_combo.currentIndex() - 1) % self.systems_combo.count()))
        check_button("button_next_tab", lambda: self.systems_combo.setCurrentIndex((self.systems_combo.currentIndex() + 1) % self.systems_combo.count()))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.resize(900, 675)
    win.show()
    sys.exit(app.exec_())