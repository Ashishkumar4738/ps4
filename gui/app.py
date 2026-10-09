
import sys
from gui.pipeline import PipelineSession
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt, QTimer
from audio.control import is_speech_enabled, set_speech_enabled
from internet_control import is_internet_enabled, toggle_internet


class NovaDesktop(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PS4 | Nova Assistant")
        self.resize(1100, 720)
        self.setMinimumSize(850, 580)

        self.listening = False
        self.session = None
        self.init_ui()
        self.internet_timer = QTimer(self)
        self.internet_timer.timeout.connect(
            self.refresh_internet_status
        )
        self.internet_timer.start(500)

    def init_ui(self):
        root = QWidget()
        self.setCentralWidget(root)

        main = QHBoxLayout(root)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        side = QVBoxLayout(sidebar)
        side.setContentsMargins(22, 28, 22, 22)
        side.setSpacing(14)

        brand = QLabel("◈  NOVA")
        brand.setObjectName("brand")
        side.addWidget(brand)

        subtitle = QLabel("PERSONAL AI ASSISTANT")
        subtitle.setObjectName("muted")
        side.addWidget(subtitle)
        side.addSpacing(28)

        self.nav_buttons = []
        for name in ["⌂   Overview", "◉   Voice Assistant",
                     "▤   Meetings & Documents", "≋   Activity Logs"]:
            button = QPushButton(name)
            button.setObjectName("nav")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            side.addWidget(button)
            self.nav_buttons.append(button)

        side.addStretch()

        self.service_status = QLabel("●  GUI Preview")
        self.service_status.setObjectName("status")
        side.addWidget(self.service_status)

        note = QLabel("PS4 PROJECT\nLinux Desktop")
        note.setObjectName("muted")
        side.addWidget(note)

        # Main content
        content = QWidget()
        content.setObjectName("content")
        body = QVBoxLayout(content)
        body.setContentsMargins(34, 28, 34, 28)
        body.setSpacing(22)

        header = QHBoxLayout()
        titles = QVBoxLayout()

        heading = QLabel("Nova Assistant")
        heading.setObjectName("heading")

        description = QLabel(
            "Your local AI workspace"
        )
        description.setObjectName("muted")

        titles.addWidget(heading)
        titles.addWidget(description)
        header.addLayout(titles)
        header.addStretch()

        self.connection = QLabel("●  Backend not connected")
        self.connection.setObjectName("warning")
        header.addWidget(self.connection, alignment=Qt.AlignmentFlag.AlignTop)
        body.addLayout(header)

        # Welcome panel
        hero = QFrame()
        hero.setObjectName("hero")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(26, 24, 26, 24)
        hero_layout.setSpacing(12)

        eyebrow = QLabel("YOUR LOCAL AI ASSISTANT")
        eyebrow.setObjectName("accent")

        welcome = QLabel("Hello, I'm Nova.")
        welcome.setObjectName("welcome")

        intro = QLabel(
            "Voice interaction, meeting assistance and document "
            "summaries in one workspace."
        )
        intro.setObjectName("heroText")
        intro.setWordWrap(True)

        hero_layout.addWidget(eyebrow)
        hero_layout.addWidget(welcome)
        hero_layout.addWidget(intro)
        body.addWidget(hero)

        # Service cards
        cards = QHBoxLayout()
        cards.setSpacing(14)

        for title, detail in [
            ("Whisper", "Speech recognition"),
            ("Ollama / Llama", "Local language model"),
            ("SQLite", "Project data"),
        ]:
            card = QFrame()
            card.setObjectName("card")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(18, 18, 18, 18)

            name = QLabel(title)
            name.setObjectName("cardTitle")
            info = QLabel(detail)
            info.setObjectName("muted")
            state = QLabel("Not checked")
            state.setObjectName("smallStatus")

            layout.addWidget(name)
            layout.addWidget(info)
            layout.addStretch()
            layout.addWidget(state)
            cards.addWidget(card)

        body.addLayout(cards)

        # Voice controls
        voice_title = QLabel("Voice Assistant")
        voice_title.setObjectName("sectionTitle")
        body.addWidget(voice_title)

        voice_row = QHBoxLayout()
        voice_row.setSpacing(12)

        self.listen_button = QPushButton("▶   Start Listening")
        self.listen_button.setObjectName("primary")
        self.listen_button.setMinimumHeight(44)
        self.listen_button.clicked.connect(self.toggle_listening)

        self.stop_button = QPushButton("■   Stop")
        self.stop_button.setObjectName("secondary")
        self.stop_button.setMinimumHeight(44)
        self.stop_button.clicked.connect(self.stop_listening)
        self.stop_button.setEnabled(False)

        voice_row.addWidget(self.listen_button)
        voice_row.addWidget(self.stop_button)
        voice_row.addStretch()
        body.addLayout(voice_row)

        # Speech and Internet controls
        control_title = QLabel("System Controls")
        control_title.setObjectName("sectionTitle")
        body.addWidget(control_title)

        control_row = QHBoxLayout()
        control_row.setSpacing(12)

        self.speech_button = QPushButton()
        self.speech_button.setObjectName("secondary")
        self.speech_button.setMinimumHeight(44)
        self.speech_button.clicked.connect(self.toggle_speech)
        control_row.addWidget(self.speech_button)

        self.internet_button = QPushButton()
        self.internet_button.setObjectName("secondary")
        self.internet_button.setMinimumHeight(44)
        self.internet_button.clicked.connect(self.toggle_internet_access)
        control_row.addWidget(self.internet_button)

        body.addLayout(control_row)

        self.internet_status = QLabel()
        self.internet_status.setObjectName("smallStatus")
        body.addWidget(self.internet_status)

        self.refresh_speech_status()
        self.refresh_internet_status()


        # Activity area
        log_title = QLabel("Recent Activity")
        log_title.setObjectName("sectionTitle")
        body.addWidget(log_title)

        self.logs = QPlainTextEdit()
        self.logs.setObjectName("logs")
        self.logs.setReadOnly(True)
        self.logs.setMaximumBlockCount(300)
        self.logs.setPlaceholderText("Application activity will appear here.")
        self.logs.appendPlainText(
            "[SYSTEM] Nova desktop interface initialized."
        )
        self.logs.appendPlainText(
            "[INFO] GUI preview mode. Backend integration is pending."
        )
        body.addWidget(self.logs, 1)

        main.addWidget(sidebar)
        main.addWidget(content, 1)

        self.apply_styles()


    def toggle_listening(self):
        if self.session is not None or self.listening:
            return

        session = PipelineSession()
        self.session = session

        session.log_message.connect(
            self.logs.appendPlainText
        )
        session.transcription_received.connect(
            self.show_transcription
        )
        session.response_received.connect(
            self.show_response
        )
        session.status_changed.connect(
            self.show_status
        )
        session.finished.connect(
            self.handle_session_finished
        )

        self.listen_button.setEnabled(False)
        self.service_status.setText("● Starting...")
        self.connection.setText("● Starting backend")

        if session.start():
            self.listening = True
            self.listen_button.setText("◉ Listening")
            self.stop_button.setEnabled(True)
        else:
            self.listening = False
            self.listen_button.setEnabled(True)
            self.listen_button.setText("▶   Start Listening")
            self.stop_button.setEnabled(False)


    def refresh_speech_status(self):
        enabled = is_speech_enabled()
        self.speech_button.setText(
            "🔇  Stop Speaking" if enabled
            else "🔊  Resume Speech"
        )

    def toggle_speech(self):
        enabled = is_speech_enabled()
        set_speech_enabled(not enabled)
        self.refresh_speech_status()

        message = (
            "Speech enabled."
            if not enabled
            else "Speech disabled."
        )
        self.logs.appendPlainText(f"[TTS] {message}")

    def refresh_internet_status(self):
        enabled = is_internet_enabled()

        self.internet_button.setText(
            "🌐  Disable Internet" if enabled
            else "🌐  Enable Internet"
        )

        self.internet_status.setText(
            "● Internet access enabled"
            if enabled
            else "● Internet access disabled"
        )

    def toggle_internet_access(self):
        enabled = toggle_internet()

        self.refresh_internet_status()

        message = (
            "Internet access enabled."
            if enabled
            else "Internet access disabled."
        )
        self.logs.appendPlainText(f"[INTERNET] {message}")


    def stop_listening(self):
        if self.session is None:
            return

        if not self.listening:
            return

        self.stop_button.setEnabled(False)
        self.logs.appendPlainText(
            "[SYSTEM] Stop requested."
        )

        self.session.stop()

    def show_transcription(self, text):
        self.logs.appendPlainText(
            f"[TRANSCRIPTION] {text}"
        )

    def show_response(self, text):
        self.logs.appendPlainText(
            f"[NOVA RESPONSE] {text}"
        )

    def show_status(self, status):
        self.service_status.setText(
            f"●  {status}"
        )

        if status == "Listening":
            self.connection.setText("● Backend connected")
        elif status == "Stopping":
            self.connection.setText("● Stopping backend")
        elif status == "Stopped":
            self.connection.setText("● Backend idle")
        elif status == "Error":
            self.connection.setText("● Backend error")

    def handle_session_finished(self, success, message):
        self.listening = False
        self.listen_button.setEnabled(True)
        self.listen_button.setText("▶   Start Listening")
        self.stop_button.setEnabled(False)

        self.logs.appendPlainText(
            f"[SYSTEM] {message}"
        )

        if success:
            self.service_status.setText("● Ready")
            self.connection.setText("● Backend idle")
        else:
            self.service_status.setText("● Error")
            self.connection.setText("● Backend error")

        self.session = None

    def closeEvent(self, event):
        # Ensure recording and transcription workers finish
        # before the application exits.
        if self.session is not None:
            self.session.stop(wait=True)

        event.accept()


    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow, QWidget#content {
                background: #10131b;
                color: #edf0f7;
            }
            QWidget {
                font-family: "DejaVu Sans";
                font-size: 12px;
            }
            QFrame#sidebar {
                background: #171b26;
                border-right: 1px solid #292e3c;
            }
            QLabel#brand {
                font-size: 25px;
                font-weight: bold;
                color: #b6a4ff;
            }
            QLabel#heading {
                font-size: 27px;
                font-weight: bold;
            }
            QLabel#muted {
                color: #929bb0;
                font-size: 11px;
            }
            QPushButton#nav {
                color: #b9c1d2;
                text-align: left;
                padding: 12px 10px;
                border: none;
                border-radius: 7px;
                background: transparent;
            }
            QPushButton#nav:hover {
                background: #272c3b;
                color: white;
            }
            QLabel#status {
                color: #b6a4ff;
                padding: 8px 0;
            }
            QLabel#warning {
                color: #f0c674;
                padding: 8px 12px;
                background: #29251d;
                border-radius: 7px;
            }
            QFrame#hero {
                background: #20243a;
                border: 1px solid #373653;
                border-radius: 14px;
            }
            QLabel#accent {
                color: #b6a4ff;
                font-weight: bold;
                font-size: 10px;
            }
            QLabel#welcome {
                font-size: 28px;
                font-weight: bold;
            }
            QLabel#heroText {
                color: #c0c6d7;
                font-size: 13px;
            }
            QFrame#card {
                background: #191e29;
                border: 1px solid #2b3140;
                border-radius: 10px;
                min-height: 95px;
            }
            QLabel#cardTitle {
                font-size: 14px;
                font-weight: bold;
            }
            QLabel#smallStatus {
                color: #929bb0;
                font-size: 10px;
            }
            QLabel#sectionTitle {
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton#primary {
                background: #8065e8;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 18px;
                font-weight: bold;
            }
            QPushButton#primary:hover {
                background: #927bf2;
            }
            QPushButton#secondary {
                background: #252b39;
                color: #e5e9f4;
                border: 1px solid #3a4254;
                border-radius: 8px;
                padding: 10px 18px;
            }
            QPushButton#secondary:hover {
                background: #303749;
            }
            QPlainTextEdit#logs {
                background: #0c0f16;
                color: #b7c8d9;
                border: 1px solid #2b3140;
                border-radius: 8px;
                padding: 10px;
                font-family: monospace;
                font-size: 11px;
            }
        """)


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("DejaVu Sans", 10))

    window = NovaDesktop()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
