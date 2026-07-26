"""Nova Welcome — first-boot experience (Qt / PySide6)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QFont
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

# Shared + local imports (installed under /usr/share/nova/ or monorepo)
_SHARED = Path("/usr/share/nova/shared")
_DEV_SHARED = Path(__file__).resolve().parents[2] / "nova-shared"
for candidate in (_SHARED, _DEV_SHARED):
    if (candidate / "nova_shared").is_dir() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))
        break

from nova_shared.hostname import get_hostname, set_hostname, validate_hostname  # noqa: E402
from nova_shared.launch import open_nova_center  # noqa: E402
from nova_shared.paths import is_welcome_completed, mark_welcome_completed  # noqa: E402
from nova_shared.theme import apply_theme_preference, list_themes  # noqa: E402

from .state import WelcomeState  # noqa: E402

ECOSYSTEM_LINKS = (
    ("GitHub", "https://github.com/NovaEcosystemOfficial/NovaOS"),
    ("Discord", "https://discord.gg/novaos"),
    ("Nova Website", "https://novaos.local"),
    ("Documentazione", "https://github.com/NovaEcosystemOfficial/NovaOS/tree/main/docs"),
)

STYLESHEET = """
QMainWindow, QWidget#root {
  background-color: #f3f6f9;
  color: #0f2744;
  font-size: 14px;
}
QLabel#brand {
  font-size: 28px;
  font-weight: 700;
  color: #0b3d6e;
}
QLabel#title {
  font-size: 22px;
  font-weight: 600;
  color: #12355b;
}
QLabel#body {
  font-size: 14px;
  color: #40566e;
}
QPushButton {
  background-color: #1f6feb;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 18px;
  font-weight: 600;
}
QPushButton:hover { background-color: #185cc4; }
QPushButton:disabled { background-color: #9bb7e0; }
QPushButton#secondary {
  background-color: transparent;
  color: #1f6feb;
  border: 1px solid #1f6feb;
}
QPushButton#link {
  background-color: #e8eef7;
  color: #0b3d6e;
  text-align: left;
}
QLineEdit {
  padding: 10px 12px;
  border: 1px solid #c5d3e3;
  border-radius: 8px;
  background: white;
}
QFrame#card {
  background: white;
  border: 1px solid #d7e1ec;
  border-radius: 12px;
}
QRadioButton { spacing: 10px; padding: 8px; }
"""


class NovaWelcomeWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Nova Welcome")
        self.setMinimumSize(720, 520)
        self.resize(840, 600)
        self.state = WelcomeState(hostname=get_hostname())

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(32, 28, 32, 24)
        layout.setSpacing(16)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

        self.pages = [
            self._page_welcome(),
            self._page_hostname(),
            self._page_theme(),
            self._page_links(),
            self._page_summary(),
            self._page_done(),
        ]
        for page in self.pages:
            self.stack.addWidget(page)

        nav = QHBoxLayout()
        self.btn_back = QPushButton("Indietro")
        self.btn_back.setObjectName("secondary")
        self.btn_back.clicked.connect(self._back)
        self.btn_next = QPushButton("Avanti")
        self.btn_next.clicked.connect(self._next)
        nav.addWidget(self.btn_back)
        nav.addStretch(1)
        nav.addWidget(self.btn_next)
        layout.addLayout(nav)

        self._sync_nav()

    def _card(self, *widgets: QWidget) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        box = QVBoxLayout(card)
        box.setContentsMargins(28, 28, 28, 28)
        box.setSpacing(14)
        for w in widgets:
            box.addWidget(w)
        box.addStretch(1)
        return card

    def _page_welcome(self) -> QWidget:
        brand = QLabel("NovaOS")
        brand.setObjectName("brand")
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title = QLabel("Benvenuto in NovaOS")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body = QLabel(
            "NovaOS è il sistema operativo del Nova Ecosystem: un ambiente "
            "moderno, pensato per essere semplice, coerente e pronto a crescere "
            "con Nova Center, Nova Update e i servizi del progetto."
        )
        body.setObjectName("body")
        body.setWordWrap(True)
        body.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return self._card(brand, title, body)

    def _page_hostname(self) -> QWidget:
        title = QLabel("Nome del computer")
        title.setObjectName("title")
        body = QLabel(
            "Scegli come si chiamerà questa macchina sulla rete. "
            "Il nome verrà applicato subito come hostname di sistema."
        )
        body.setObjectName("body")
        body.setWordWrap(True)
        self.host_edit = QLineEdit(self.state.hostname)
        self.host_edit.setPlaceholderText("es. novaos-fabio")
        self.host_error = QLabel("")
        self.host_error.setStyleSheet("color: #a32020;")
        return self._card(title, body, self.host_edit, self.host_error)

    def _page_theme(self) -> QWidget:
        title = QLabel("Tema")
        title.setObjectName("title")
        body = QLabel(
            "Scegli l’aspetto iniziale. Il catalogo temi è estensibile: "
            "futuri temi Nova verranno aggiunti qui senza cambiare il flusso."
        )
        body.setObjectName("body")
        body.setWordWrap(True)
        self.theme_group = QButtonGroup(self)
        theme_box = QVBoxLayout()
        theme_box.setSpacing(6)
        for i, theme in enumerate(list_themes()):
            radio = QRadioButton(f"{theme.label} — {theme.description}")
            radio.setProperty("theme_id", theme.id)
            self.theme_group.addButton(radio, i)
            if theme.id == self.state.theme_id:
                radio.setChecked(True)
            theme_box.addWidget(radio)
        wrap = QWidget()
        wrap.setLayout(theme_box)
        return self._card(title, body, wrap)

    def _page_links(self) -> QWidget:
        title = QLabel("Nova Ecosystem")
        title.setObjectName("title")
        body = QLabel("Collegamenti utili per restare aggiornato sul progetto.")
        body.setObjectName("body")
        body.setWordWrap(True)
        links_wrap = QVBoxLayout()
        for label, url in ECOSYSTEM_LINKS:
            btn = QPushButton(label)
            btn.setObjectName("link")
            btn.clicked.connect(lambda _=False, u=url: QDesktopServices.openUrl(QUrl(u)))
            links_wrap.addWidget(btn)
        wrap = QWidget()
        wrap.setLayout(links_wrap)
        return self._card(title, body, wrap)

    def _page_summary(self) -> QWidget:
        title = QLabel("Riepilogo")
        title.setObjectName("title")
        self.summary_label = QLabel()
        self.summary_label.setObjectName("body")
        self.summary_label.setWordWrap(True)
        return self._card(title, self.summary_label)

    def _page_done(self) -> QWidget:
        title = QLabel("NovaOS è pronto.")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body = QLabel(
            "La configurazione iniziale è completa. "
            "Puoi aprire Nova Center per gestire il sistema oppure uscire e iniziare a usare NovaOS."
        )
        body.setObjectName("body")
        body.setWordWrap(True)
        body.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_open_center = QPushButton("Apri Nova Center")
        self.btn_open_center.clicked.connect(self._finish_open_center)
        self.btn_exit = QPushButton("Esci")
        self.btn_exit.setObjectName("secondary")
        self.btn_exit.clicked.connect(self._finish_exit)
        return self._card(title, body, self.btn_open_center, self.btn_exit)

    def _sync_nav(self) -> None:
        idx = self.stack.currentIndex()
        last = len(self.pages) - 1
        self.btn_back.setEnabled(idx > 0 and idx < last)
        self.btn_back.setVisible(idx < last)
        self.btn_next.setVisible(idx < last)
        if idx == 0:
            self.btn_next.setText("Iniziamo")
        elif idx == last - 1:
            self.btn_next.setText("Completa")
        else:
            self.btn_next.setText("Avanti")
        if idx == 4:
            self._refresh_summary()

    def _refresh_summary(self) -> None:
        theme = next(
            (t for t in list_themes() if t.id == self.state.theme_id),
            None,
        )
        lines = [
            f"• Computer: {self.state.hostname or '—'}",
            f"• Hostname applicato: {'sì' if self.state.hostname_applied else 'no'}",
            f"• Tema: {theme.label if theme else self.state.theme_id}",
            "• Collegamenti Ecosystem: disponibili",
        ]
        if self.state.hostname_error:
            lines.append(f"• Nota hostname: {self.state.hostname_error}")
        self.summary_label.setText("\n".join(lines))

    def _back(self) -> None:
        idx = self.stack.currentIndex()
        if idx > 0:
            self.stack.setCurrentIndex(idx - 1)
            self._sync_nav()

    def _next(self) -> None:
        idx = self.stack.currentIndex()
        if idx == 1 and not self._apply_hostname_page():
            return
        if idx == 2:
            self._apply_theme_page()
        if idx == 3:
            self.state.links_seen = True
        if idx == 4:
            # Completa → pagina finale + marker + apri Nova Center
            mark_welcome_completed()
            self.stack.setCurrentIndex(5)
            self._sync_nav()
            if not open_nova_center():
                QMessageBox.information(
                    self,
                    "Nova Welcome",
                    "Configurazione salvata. Apri Nova Center dal menu Applicazioni quando vuoi.",
                )
            return
        if idx < len(self.pages) - 1:
            self.stack.setCurrentIndex(idx + 1)
            self._sync_nav()

    def _apply_hostname_page(self) -> bool:
        raw = self.host_edit.text()
        ok, msg = validate_hostname(raw)
        if not ok:
            self.host_error.setText(msg)
            return False
        applied, result = set_hostname(msg)
        self.state.hostname = msg if applied else msg
        self.state.hostname_applied = applied
        self.state.hostname_error = "" if applied else result
        if not applied:
            self.host_error.setText(
                f"Hostname salvato nella procedura, ma non applicato ora: {result}"
            )
            # Still allow continuing — preference recorded in state for summary
            return True
        self.host_error.setText("")
        return True

    def _apply_theme_page(self) -> None:
        checked = self.theme_group.checkedButton()
        if checked is not None:
            theme_id = checked.property("theme_id")
            info = apply_theme_preference(str(theme_id))
            self.state.theme_id = info.id

    def _complete_and_quit(self, open_center: bool) -> None:
        mark_welcome_completed()
        if open_center:
            if not open_nova_center():
                QMessageBox.warning(
                    self,
                    "Nova Welcome",
                    "Nova Center non è disponibile su questo sistema.",
                )
        self.close()

    def _finish_open_center(self) -> None:
        self._complete_and_quit(open_center=True)

    def _finish_exit(self) -> None:
        self._complete_and_quit(open_center=False)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Nova Welcome — first boot")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Esegui anche se welcome-completed è già presente",
    )
    args = parser.parse_args(argv)

    if is_welcome_completed() and not args.force:
        return 0

    app = QApplication(sys.argv)
    app.setApplicationName("Nova Welcome")
    app.setOrganizationName("NovaOS")
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)
    # Prefer a clean UI font without relying on desktop defaults branded elsewhere
    font = QFont("Sans Serif", 11)
    app.setFont(font)

    win = NovaWelcomeWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
