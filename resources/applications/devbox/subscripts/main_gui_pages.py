from __future__ import annotations

import sys
from pathlib import Path

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


from PySide6.QtCore import QProcess, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from subscripts.main_gui_config import DEMO_DEVICES, DOCUMENT_CATEGORIES, WORKSHOP_PROFILES
from subscripts.main_gui_widgets import DemoDeviceCard, RepositoryImageDropBox


def build_profile_page(studio, page_key: str, title_text: str, subtitle_text: str, profiles: list[tuple[str, str]]) -> QWidget:
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(10, 12, 10, 10)
    layout.setSpacing(14)
    add_title(layout, title_text, subtitle_text)

    grid_container = QWidget()
    grid_container.setObjectName("GridContainer")
    grid = QGridLayout(grid_container)
    grid.setContentsMargins(14, 14, 14, 14)
    grid.setHorizontalSpacing(12)
    grid.setVerticalSpacing(10)

    for col, text in enumerate(("Bereich", "Snapshot erstellen")):
        label = QLabel(text)
        label.setObjectName("HeaderLabel")
        grid.addWidget(label, 0, col)

    for row, (title, desc) in enumerate(profiles, start=1):
        area = QLabel(f"{title}\n{desc}")
        area.setObjectName("AreaLabel")
        grid.addWidget(area, row, 0)

        snap_button = QPushButton("Snapshot")
        snap_button.setObjectName("SnapshotButton")
        snap_button.clicked.connect(lambda _=False, p=page_key: studio.preview_action(p, "Snapshot ist in dieser GUI-Vorschau abgekoppelt."))
        grid.addWidget(snap_button, row, 1)

    grid.setColumnStretch(0, 2)
    grid.setColumnStretch(1, 1)
    layout.addWidget(grid_container)

    implement_layout = QHBoxLayout()
    implement_hint = QLabel("Result-ZIPs im Downloads-Ordner automatisch erkennen. In dieser isolierten Version ist die Implementierung nicht verbunden.")
    implement_hint.setWordWrap(True)
    implement_hint.setObjectName("Subtitle")
    implement_layout.addWidget(implement_hint, stretch=1)

    implement_button = QPushButton("Resultat automatisch implementieren")
    implement_button.setObjectName("ImplementButton")
    implement_button.clicked.connect(lambda _=False, p=page_key: studio.preview_action(p, "Automatische Implementierung ist abgekoppelt."))
    implement_layout.addWidget(implement_button)
    layout.addLayout(implement_layout)

    add_status_and_log(studio, layout, page_key)
    return page


def build_document_page(studio) -> QWidget:
    page_key = "documents"
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(10, 12, 10, 10)
    layout.setSpacing(14)
    add_title(layout, "Doku-Snapshots", "Snapshots nach Dokumentationskategorien oder einzelnen Dokumentarten. Die Backend-Erzeugung ist hier bewusst entfernt.")

    grid_container = QWidget()
    grid_container.setObjectName("GridContainer")
    grid = QGridLayout(grid_container)
    grid.setContentsMargins(14, 14, 14, 14)
    grid.setHorizontalSpacing(12)
    grid.setVerticalSpacing(10)

    for col, text in enumerate(("Kategorie", "Kategorie-Snapshot", "Dokument-Snapshots")):
        label = QLabel(text)
        label.setObjectName("HeaderLabel")
        grid.addWidget(label, 0, col)

    for row, (title, desc, docs) in enumerate(DOCUMENT_CATEGORIES, start=1):
        category_label = QLabel(f"{title}\n{desc}")
        category_label.setObjectName("AreaLabel")
        grid.addWidget(category_label, row, 0)

        category_button = QPushButton(title)
        category_button.setObjectName("SnapshotButton")
        category_button.clicked.connect(lambda _=False, p=page_key: studio.preview_action(p, "Doku-Snapshot ist abgekoppelt."))
        grid.addWidget(category_button, row, 1)

        document_button_box = QWidget()
        document_button_layout = QHBoxLayout(document_button_box)
        document_button_layout.setContentsMargins(0, 0, 0, 0)
        document_button_layout.setSpacing(8)
        for doc_title in docs:
            document_button = QPushButton(doc_title)
            document_button.setObjectName("DocSnapshotButton")
            document_button.clicked.connect(lambda _=False, p=page_key: studio.preview_action(p, "Dokument-Snapshot ist abgekoppelt."))
            document_button_layout.addWidget(document_button)
        document_button_layout.addStretch(1)
        grid.addWidget(document_button_box, row, 2)

    grid.setColumnStretch(0, 2)
    grid.setColumnStretch(1, 1)
    grid.setColumnStretch(2, 3)
    layout.addWidget(grid_container)

    implement_layout = QHBoxLayout()
    implement_hint = QLabel("Result-ZIPs im Downloads-Ordner automatisch erkennen. Die Zuordnung läuft in dieser Vorschau nicht.")
    implement_hint.setWordWrap(True)
    implement_hint.setObjectName("Subtitle")
    implement_layout.addWidget(implement_hint, stretch=1)

    implement_button = QPushButton("Resultat automatisch implementieren")
    implement_button.setObjectName("ImplementButton")
    implement_button.clicked.connect(lambda _=False, p=page_key: studio.preview_action(p, "Automatische Implementierung ist abgekoppelt."))
    implement_layout.addWidget(implement_button)
    layout.addLayout(implement_layout)

    add_status_and_log(studio, layout, page_key)
    return page


def build_eventlab_page(studio) -> QWidget:
    page_key = "eventlab"
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(10, 12, 10, 10)
    layout.setSpacing(12)
    add_title(layout, "EventLab", "Integrierte EventLab-Ansicht als reine GUI-Vorschau. Daemon, Datenbank und Schaltbefehle sind nicht angebunden.")

    top = QHBoxLayout()
    top.setSpacing(8)
    module_label = QLabel("Gerätemodul:")
    module_label.setObjectName("HeaderLabel")
    top.addWidget(module_label)

    module_button = QPushButton("Demo-Module ▼")
    module_button.setObjectName("ModuleButton")
    module_button.setMinimumWidth(280)
    module_button.clicked.connect(lambda _=False: studio.preview_action(page_key, "Modul-Menü ist in der Vorschau abgekoppelt."))
    top.addWidget(module_button)

    refresh_button = QPushButton("Aktualisieren")
    refresh_button.setObjectName("SecondaryButton")
    refresh_button.clicked.connect(lambda _=False: studio.preview_action(page_key, "Aktualisieren ist in der Vorschau abgekoppelt."))
    top.addWidget(refresh_button)
    top.addStretch(1)

    start_stop_button = QPushButton("EventLab starten")
    start_stop_button.setObjectName("SnapshotButton")
    start_stop_button.clicked.connect(lambda _=False: studio.preview_action(page_key, "EventLab-Daemon ist abgekoppelt."))
    top.addWidget(start_stop_button)
    layout.addLayout(top)

    info_label = QLabel("Demo-Geräte zur optischen Kontrolle. Es wird keine EventLab-DB gelesen.")
    info_label.setWordWrap(True)
    info_label.setObjectName("Subtitle")
    layout.addWidget(info_label)

    legend = QLabel("Buttonfarbe = SQL-Sollwert | Umrandung = Live-Istwert | Gelb = Schaltung läuft | Grau = offline/ignoriert")
    legend.setObjectName("SubtitleSmall")
    layout.addWidget(legend)

    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setFrameShape(QFrame.Shape.NoFrame)
    grid_widget = QWidget()
    grid_layout = QGridLayout(grid_widget)
    grid_layout.setContentsMargins(2, 8, 2, 8)
    grid_layout.setSpacing(12)
    for index, (model, name, power, desired_on, live_on) in enumerate(DEMO_DEVICES):
        grid_layout.addWidget(DemoDeviceCard(name, model, power, desired_on, live_on), index // 3, index % 3)
    for column in range(3):
        grid_layout.setColumnStretch(column, 1)
    scroll_area.setWidget(grid_widget)
    layout.addWidget(scroll_area, stretch=1)

    add_status_and_log(studio, layout, page_key)
    return page


def build_repository_page(studio) -> QWidget:
    page_key = "repositories"
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(10, 12, 10, 10)
    layout.setSpacing(14)
    add_title(
        layout,
        "Repositorys",
        "Repository- und Pushbereich. Für DevBox startet der spezielle "
        "DevBox-Repositoryprozess; weitere Produktschemata folgen später.",
    )

    repository_panel = QFrame()
    repository_panel.setObjectName("GridContainer")
    panel_layout = QVBoxLayout(repository_panel)
    panel_layout.setContentsMargins(14, 14, 14, 14)
    panel_layout.setSpacing(10)

    selection_row = QHBoxLayout()
    selection_row.setSpacing(10)
    selection_label = QLabel("Repository")
    selection_label.setObjectName("HeaderLabel")
    selection_row.addWidget(selection_label)

    repository_combo = QComboBox()
    repository_combo.setObjectName("RepositoryProductCombo")
    repository_combo.setMinimumWidth(300)
    load_repository_product_choices(studio, repository_combo)
    selection_row.addWidget(repository_combo, stretch=1)

    push_button = QPushButton("Push to Git")
    push_button.setObjectName("RepositoryPushButton")
    push_button.setMinimumWidth(160)
    selection_row.addWidget(push_button)
    panel_layout.addLayout(selection_row)

    hint_label = QLabel(
        "Bilder und Commit-Text sind optional. Die Verarbeitung wird erst "
        "durch das jeweils ausgewählte Repository-Schema ausgeführt."
    )
    hint_label.setWordWrap(True)
    hint_label.setObjectName("SubtitleSmall")
    panel_layout.addWidget(hint_label)

    input_row = QHBoxLayout()
    input_row.setSpacing(12)

    commit_box = QVBoxLayout()
    commit_label = QLabel("Commit-Text")
    commit_label.setObjectName("HeaderLabel")
    commit_box.addWidget(commit_label)
    commit_text = QTextEdit()
    commit_text.setObjectName("CommitTextBox")
    commit_text.setPlaceholderText("Commit-Text optional...")
    commit_text.setMinimumHeight(142)
    commit_box.addWidget(commit_text)
    input_row.addLayout(commit_box, stretch=4)

    drop_box = QVBoxLayout()
    drop_label = QLabel("Bilder")
    drop_label.setObjectName("HeaderLabel")
    drop_box.addWidget(drop_label)
    image_drop = RepositoryImageDropBox()
    drop_box.addWidget(image_drop)
    input_row.addLayout(drop_box, stretch=1)

    panel_layout.addLayout(input_row)
    layout.addWidget(repository_panel)

    add_status_and_log(studio, layout, page_key)

    repository_combo.currentIndexChanged.connect(
        lambda _index: repository_selection_changed(
            studio,
            page_key,
            repository_combo,
            push_button,
        )
    )
    image_drop.files_changed.connect(
        lambda file_paths: repository_images_changed(
            studio,
            page_key,
            file_paths,
        )
    )
    push_button.clicked.connect(
        lambda _checked=False: launch_selected_repository_schema(
            studio,
            page_key,
            repository_combo,
            push_button,
            commit_text,
            image_drop,
        )
    )

    repository_selection_changed(
        studio,
        page_key,
        repository_combo,
        push_button,
    )
    return page


def load_repository_product_choices(studio, combo: QComboBox) -> None:
    """Fill the selector from the product table while keeping DevBox visible.

    Repository connection fields are intentionally not read or changed here.
    This is only navigation/UI preparation for the later push schemas.
    """
    choices: list[tuple[str, str]] = []
    database_file = (
        studio.project_root_path
        / "resources"
        / "organization"
        / "devbox_db.r0b"
    )

    try:
        import sqlite3

        if database_file.is_file():
            connection = sqlite3.connect(database_file)
            connection.row_factory = sqlite3.Row
            try:
                cursor = connection.execute(
                    'SELECT rowid, * FROM "product_credentials"'
                )
                for row in cursor.fetchall():
                    values = dict(row)
                    label = next(
                        (
                            str(values[column]).strip()
                            for column in (
                                "product_display_name",
                                "product_name",
                                "product_short_name",
                                "product_slug",
                            )
                            if values.get(column)
                            and str(values[column]).strip()
                        ),
                        f"Produkt {values.get('rowid', '')}".strip(),
                    )
                    slug = str(values.get("product_slug") or "").strip().lower()
                    if not slug and label.casefold() == "devbox":
                        slug = "devbox"
                    choices.append((label, slug))
            finally:
                connection.close()
    except Exception as exc:
        LOGGER.warning(
            "Repository product choices could not be loaded.",
            f"{type(exc).__name__}: {exc}",
        )

    if not any(slug == "devbox" or label.casefold() == "devbox" for label, slug in choices):
        choices.append(("DevBox", "devbox"))

    choices.sort(key=lambda item: (item[1] != "devbox", item[0].casefold()))
    combo.blockSignals(True)
    combo.clear()
    for label, slug in choices:
        combo.addItem(label, {"label": label, "slug": slug})
    combo.blockSignals(False)


def selected_repository_slug(combo: QComboBox) -> str:
    data = combo.currentData()
    if isinstance(data, dict):
        slug = str(data.get("slug") or "").strip().lower()
        label = str(data.get("label") or "").strip().lower()
        return slug or ("devbox" if label == "devbox" else label)
    return ""


def repository_selection_changed(
    studio,
    page_key: str,
    combo: QComboBox,
    push_button: QPushButton,
) -> None:
    slug = selected_repository_slug(combo)
    label = combo.currentText().strip() or "kein Produkt"
    push_button.setEnabled(bool(slug))

    if slug == "devbox":
        push_button.setToolTip("DevBox-Repositoryprozess starten")
        studio.set_status("DevBox-Repositoryprozess bereit.", "neutral", page_key)
        return

    push_button.setToolTip(
        "Für dieses Produkt ist noch kein Repository-Schema hinterlegt."
    )
    studio.set_status(
        f"Für {label} ist noch kein Repository-Schema hinterlegt.",
        "warning",
        page_key,
    )


def repository_images_changed(studio, page_key: str, file_paths: list[Path]) -> None:
    if not file_paths:
        studio.append_log("Keine optionalen Bilddateien ausgewählt.", page_key)
        return

    studio.append_log(
        f"{len(file_paths)} optionale Bilddatei(en) für den späteren "
        "Repositoryprozess vorgemerkt.",
        page_key,
    )


def launch_selected_repository_schema(
    studio,
    page_key: str,
    combo: QComboBox,
    push_button: QPushButton,
    commit_text: QTextEdit,
    image_drop: RepositoryImageDropBox,
) -> None:
    slug = selected_repository_slug(combo)
    label = combo.currentText().strip() or "das ausgewählte Produkt"

    if slug != "devbox":
        studio.set_status(
            f"Für {label} ist noch kein Repository-Schema hinterlegt.",
            "warning",
            page_key,
        )
        studio.append_log(
            f"Push abgebrochen: Kein Repository-Schema für {label}.",
            page_key,
        )
        return

    schema_script = (
        studio.project_root_path
        / "resources"
        / "applications"
        / "devbox"
        / "functions"
        / "push_to_git_schema_devbox.py"
    )
    if not schema_script.is_file():
        studio.set_status(
            "DevBox-Repositoryprozess ist noch nicht angelegt.",
            "warning",
            page_key,
        )
        studio.append_log(
            f"Erwartetes DevBox-Schema nicht gefunden: {schema_script}",
            page_key,
        )
        return

    active_process = getattr(studio, "repository_push_process", None)
    if active_process is not None and active_process.state() != QProcess.ProcessState.NotRunning:
        studio.set_status("Ein Repositoryprozess läuft bereits.", "warning", page_key)
        return

    python_executable = Path(sys.executable).resolve()
    if python_executable.name.casefold() == "pythonw.exe":
        candidate = python_executable.with_name("python.exe")
        if candidate.is_file():
            python_executable = candidate

    command = [str(schema_script), "--product-slug", slug]
    normalized_commit_text = commit_text.toPlainText().strip()
    if normalized_commit_text:
        command.extend(["--commit-text", normalized_commit_text])
    for image_path in image_drop.image_files():
        command.extend(["--image", str(image_path)])

    process = QProcess(studio)
    process.setProgram(str(python_executable))
    process.setArguments(command)
    process.setWorkingDirectory(str(schema_script.parent))
    process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)

    def append_process_output() -> None:
        output = bytes(process.readAllStandardOutput()).decode("utf-8", "replace").strip()
        if output:
            studio.append_log(output, page_key)

    def finished(exit_code: int, _exit_status) -> None:
        append_process_output()
        push_button.setEnabled(selected_repository_slug(combo) == "devbox")
        if exit_code == 0:
            studio.set_status("DevBox-Repositoryprozess abgeschlossen.", "success", page_key)
            studio.append_log("Push-to-Git-Prozess erfolgreich beendet.", page_key)
        else:
            studio.set_status("DevBox-Repositoryprozess mit Fehler beendet.", "error", page_key)
            studio.append_log(f"Push-to-Git-Prozess beendet mit Code {exit_code}.", page_key)

    def process_error(_error) -> None:
        studio.append_log(
            f"Repositoryprozess konnte nicht gestartet werden: {process.errorString()}",
            page_key,
        )

    process.readyReadStandardOutput.connect(append_process_output)
    process.finished.connect(finished)
    process.errorOccurred.connect(process_error)
    studio.repository_push_process = process
    push_button.setEnabled(False)
    studio.set_status("DevBox-Repositoryprozess läuft.", "running", page_key)
    studio.append_log(
        "DevBox-Repositoryprozess gestartet: "
        f"{schema_script.name}; Bilder: {len(image_drop.image_files())}; "
        f"Commit-Text: {'ja' if normalized_commit_text else 'nein'}",
        page_key,
    )
    process.start()


def add_title(layout: QVBoxLayout, title: str, subtitle: str) -> None:
    page_title = QLabel(title)
    page_title.setObjectName("HeaderLabel")
    title_font = QFont()
    title_font.setPointSize(13)
    title_font.setBold(True)
    page_title.setFont(title_font)
    layout.addWidget(page_title)

    page_subtitle = QLabel(subtitle)
    page_subtitle.setWordWrap(True)
    page_subtitle.setObjectName("Subtitle")
    layout.addWidget(page_subtitle)


def add_status_and_log(studio, layout: QVBoxLayout, page_key: str) -> None:
    status_label = QLabel("GUI isoliert")
    status_label.setObjectName("StatusPanel")
    status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    status_font = QFont()
    status_font.setPointSize(17)
    status_font.setBold(True)
    status_label.setFont(status_font)
    status_label.setMinimumHeight(58)
    layout.addWidget(status_label)

    log_header_layout = QHBoxLayout()
    log_label = QLabel("Ausgabe")
    log_label.setObjectName("HeaderLabel")
    log_header_layout.addWidget(log_label)
    log_header_layout.addStretch(1)

    copy_button = QPushButton("Kopiere Log in Zwischenablage")
    copy_button.setObjectName("SecondaryButton")
    copy_button.clicked.connect(lambda _=False, p=page_key: studio.copy_log_to_clipboard(p))
    log_header_layout.addWidget(copy_button)

    clear_button = QPushButton("Log leeren")
    clear_button.setObjectName("SecondaryButton")
    clear_button.clicked.connect(lambda _=False, p=page_key: studio.clear_log(p))
    log_header_layout.addWidget(clear_button)
    layout.addLayout(log_header_layout)

    log = QTextEdit()
    log.setReadOnly(True)
    log.setObjectName("LogBox")
    layout.addWidget(log, stretch=1)
    studio.pages[page_key] = {"status": status_label, "log": log}
