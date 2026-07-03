from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import QProcess, QProcessEnvironment
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget

from subscripts.main_gui_pages import add_status_and_log
from subscripts.main_gui_widgets import RepositoryImageDropBox


PAGE_KEY = "desknode_repository"
PROJECT_ROOT_ENV_NAME = "_CYXLABS_DEVBOX_PROJECT_ROOT_PATH"


def _python_executable() -> Path:
    executable = Path(sys.executable).resolve()
    if executable.name.casefold() == "pythonw.exe":
        candidate = executable.with_name("python.exe")
        if candidate.is_file():
            return candidate
    return executable


def _schema_script(studio) -> Path:
    return (
        Path(studio.project_root_path)
        / "applications"
        / "deskNode"
        / "resources"
        / "scripts"
        / "push_to_git_schema_desknode.py"
    )


def build_desknode_repository_view(studio, return_to_execution: Callable[[], None]) -> QWidget:
    page = QWidget()
    page.setObjectName("DeskNodeRepositoryView")
    layout = QVBoxLayout(page)
    layout.setContentsMargins(10, 12, 10, 10)
    layout.setSpacing(14)

    toolbar = QHBoxLayout()
    toolbar.setSpacing(10)
    back_button = QPushButton("Zurück")
    back_button.setObjectName("DeskNodeUxBackButton")
    back_button.setMinimumWidth(145)
    back_button.clicked.connect(lambda _checked=False: return_to_execution())
    toolbar.addWidget(back_button)
    title = QLabel("Repository: deskNode")
    title.setObjectName("DeskNodeUxTitle")
    toolbar.addWidget(title)
    toolbar.addStretch(1)
    layout.addLayout(toolbar)

    description = QLabel(
        "Veröffentlicht den bereinigten deskNode-Stand in das hinterlegte Repository. "
        "Commit-Text und Bilder sind optional. Bilder werden unter assets/pictures ergänzt "
        "und bei späteren Pushes nicht entfernt."
    )
    description.setObjectName("Subtitle")
    description.setWordWrap(True)
    layout.addWidget(description)

    repository_panel = QFrame()
    repository_panel.setObjectName("GridContainer")
    panel_layout = QVBoxLayout(repository_panel)
    panel_layout.setContentsMargins(14, 14, 14, 14)
    panel_layout.setSpacing(10)

    top_row = QHBoxLayout()
    label = QLabel("Repository")
    label.setObjectName("HeaderLabel")
    top_row.addWidget(label)
    product_label = QLabel("CYXnTrol deskNode")
    product_label.setObjectName("PathLabel")
    top_row.addWidget(product_label, stretch=1)
    push_button = QPushButton("Push to Git")
    push_button.setObjectName("RepositoryPushButton")
    push_button.setMinimumWidth(160)
    top_row.addWidget(push_button)
    panel_layout.addLayout(top_row)

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

    add_status_and_log(studio, layout, PAGE_KEY)

    def set_controls_enabled(enabled: bool) -> None:
        push_button.setEnabled(enabled)
        commit_text.setEnabled(enabled)
        image_drop.setEnabled(enabled)
        back_button.setEnabled(enabled)

    def launch_push() -> None:
        schema_script = _schema_script(studio)
        if not schema_script.is_file():
            studio.set_status("deskNode-Repositoryprozess ist noch nicht angelegt.", "warning", PAGE_KEY)
            studio.append_log(f"Erwartetes deskNode-Schema nicht gefunden: {schema_script}", PAGE_KEY)
            return

        active_process = getattr(studio, "desknode_repository_push_process", None)
        if active_process is not None and active_process.state() != QProcess.ProcessState.NotRunning:
            studio.set_status("Ein deskNode-Repositoryprozess läuft bereits.", "warning", PAGE_KEY)
            return

        arguments = [str(schema_script), "--product-slug", "desknode"]
        normalized_commit_text = commit_text.toPlainText().strip()
        if normalized_commit_text:
            arguments.extend(["--commit-text", normalized_commit_text])
        for image_path in image_drop.image_files():
            arguments.extend(["--image", str(image_path)])

        process = QProcess(studio)
        environment = QProcessEnvironment.systemEnvironment()
        environment.insert(PROJECT_ROOT_ENV_NAME, str(studio.project_root_path))
        process.setProcessEnvironment(environment)
        process.setProgram(str(_python_executable()))
        process.setArguments(arguments)
        process.setWorkingDirectory(str(schema_script.parent))
        process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)

        def append_output() -> None:
            output = bytes(process.readAllStandardOutput()).decode("utf-8", "replace").strip()
            if output:
                studio.append_log(output, PAGE_KEY)

        def finished(exit_code: int, _exit_status) -> None:
            append_output()
            set_controls_enabled(True)
            push_button.setText("Push to Git")
            if exit_code == 0:
                studio.set_status("deskNode-Repositoryprozess abgeschlossen.", "success", PAGE_KEY)
                studio.append_log("deskNode Push-to-Git-Prozess erfolgreich beendet.", PAGE_KEY)
            else:
                studio.set_status("deskNode-Repositoryprozess mit Fehler beendet.", "error", PAGE_KEY)
                studio.append_log(f"deskNode Push-to-Git-Prozess beendet mit Code {exit_code}.", PAGE_KEY)

        def process_error(_error) -> None:
            studio.append_log(f"deskNode-Repositoryprozess konnte nicht gestartet werden: {process.errorString()}", PAGE_KEY)

        process.readyReadStandardOutput.connect(append_output)
        process.finished.connect(finished)
        process.errorOccurred.connect(process_error)
        studio.desknode_repository_push_process = process
        set_controls_enabled(False)
        push_button.setText("Push läuft …")
        studio.set_status("deskNode-Repositoryprozess läuft.", "running", PAGE_KEY)
        studio.append_log(
            "deskNode-Repositoryprozess gestartet: "
            f"{schema_script.name}; Bilder: {len(image_drop.image_files())}; "
            f"Commit-Text: {'ja' if normalized_commit_text else 'nein'}",
            PAGE_KEY,
        )
        process.start()

    image_drop.files_changed.connect(
        lambda files: studio.append_log(
            f"{len(files)} optionale Bilddatei(en) für den deskNode-Repositoryprozess vorgemerkt."
            if files else "Keine optionalen Bilddateien ausgewählt.",
            PAGE_KEY,
        )
    )
    push_button.clicked.connect(lambda _checked=False: launch_push())
    studio.set_status("deskNode-Repositoryprozess bereit.", "neutral", PAGE_KEY)
    studio.append_log("deskNode-Repositoryseite bereit.", PAGE_KEY)
    return page
