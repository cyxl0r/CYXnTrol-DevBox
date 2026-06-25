from __future__ import annotations

import hashlib
from pathlib import Path

from PySide6.QtCore import QObject, QTimer
from PySide6.QtNetwork import QLocalServer, QLocalSocket

from subscripts.main_gui_devbox_log import get_devbox_logger


LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


class DevBoxSingleInstance(QObject):
    """Keep exactly one DevBox GUI active for one project root."""

    def __init__(self, project_root_path: Path) -> None:
        super().__init__()
        normalized_root = str(Path(project_root_path).resolve()).casefold()
        root_hash = hashlib.sha256(normalized_root.encode("utf-8")).hexdigest()[:20]
        self.server_name = f"cyxlabs_cyxntrol_devbox_{root_hash}"
        self.server = QLocalServer(self)
        self.window = None
        self.server.newConnection.connect(self._handle_connection)

    def claim_or_activate(self) -> bool:
        """Claim the local server, or activate an already running DevBox."""
        if self._signal_existing_instance():
            LOGGER.info("Existing DevBox instance activated.")
            return False

        QLocalServer.removeServer(self.server_name)

        if self.server.listen(self.server_name):
            LOGGER.info("Single-instance server started.", self.server_name)
            return True

        if self._signal_existing_instance():
            LOGGER.info("Existing DevBox instance activated after server retry.")
            return False

        error_text = self.server.errorString()
        LOGGER.error("Could not create DevBox single-instance server.", error_text)
        raise RuntimeError(
            "DevBox single-instance protection could not be initialized: "
            f"{error_text}"
        )

    def attach_window(self, window) -> None:
        self.window = window

    def close(self) -> None:
        if self.server.isListening():
            self.server.close()
        QLocalServer.removeServer(self.server_name)
        LOGGER.info("Single-instance server closed.")

    def _signal_existing_instance(self) -> bool:
        socket = QLocalSocket(self)
        socket.connectToServer(self.server_name)

        if not socket.waitForConnected(250):
            return False

        socket.write(b"activate")
        socket.flush()
        socket.waitForBytesWritten(250)
        socket.disconnectFromServer()
        return True

    def _handle_connection(self) -> None:
        while self.server.hasPendingConnections():
            socket = self.server.nextPendingConnection()
            socket.disconnectFromServer()

            if self.window is None:
                continue

            LOGGER.info("Received activation request from another DevBox start.")
            QTimer.singleShot(0, self.window.activate_existing_instance)
