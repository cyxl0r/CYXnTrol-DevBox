from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


PROGRAM_NAME = "DevBox GUI - isolated"

WORKSHOP_PROFILES = [
    ("DeskPowerManager", "Produktiver Code"),
    ("EventLab", "Vendor-Modul-Labor"),
    ("EXE-Code", "resources/exe_code_in_py"),
    ("Tools", "Studio, Builder und Werkbank"),
]

DOCUMENT_CATEGORIES = [
    ("Einstieg", "Übersicht / Overview", ["Übersicht"]),
    ("Regelwerk", "Regeln / Rulebook", ["Regelwerk"]),
    ("Architektur", "Architektur und EventLab-Zugangsdaten-GUI", ["Architektur", "EventLab-Credential-GUI"]),
    ("Projektsteuerung", "Arbeitsplan, Phasenhistorie und Änderungsverlauf", ["Arbeitsplan / TODO", "Phasenhistorie", "Änderungsverlauf"]),
    ("Endnutzer", "Lizenz und README", ["Lizenz", "README"]),
]

DEMO_DEVICES = [
    ("Tapo P115", "Monitor", 7.2, True, True),
    ("Shelly Plug M", "Scanner", 0.0, False, False),
    ("FRITZ!DECT 200", "Drucker", 3.8, True, True),
    ("Shelly Plug", "NAS", 18.4, True, True),
    ("Tapo P115", "Plattenspieler", 0.0, False, True),
    ("FRITZ!DECT", "Ladegerät", 1.1, True, True),
]

COLOR_DESIRED_ON = "#0e1720"
COLOR_DESIRED_OFF = "#120d10"
COLOR_LIVE_ON = "#23ead7"
COLOR_LIVE_OFF = "#ff4365"
COLOR_PENDING = "#f4ff5b"

PAGE_KEYS = ["workshop", "documents", "eventlab", "repositories"]
TAB_KEYS = ["platform", *PAGE_KEYS]
