from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt
from PySide6.QtWidgets import (
    QApplication, QFrame, QLabel, QMainWindow, QPushButton,
    QVBoxLayout, QWidget,
)

from jarvis.commands import handle_command
from jarvis.tts import speak
from jarvis.voice import transcribe_once

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "vosk-id"


class VoiceWorker(QObject):
    recognized = Signal(str, str)
    failed = Signal(str)
    finished = Signal()

    @Slot()
    def run(self):
        try:
            transcript = transcribe_once(str(MODEL_PATH))
            response = handle_command(transcript) if transcript else "Maaf Master, suara belum terbaca. Silakan coba lagi."
            self.recognized.emit(transcript, response)
            speak(response)
        except Exception as exc:
            self.failed.emit(str(exc))
        finally:
            self.finished.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JARVIS — Offline MVP")
        self.resize(760, 520)
        self.setMinimumSize(520, 420)
        self.thread = None
        self.worker = None

        root = QWidget()
        root.setObjectName("root")
        layout = QVBoxLayout(root)
        layout.setContentsMargins(48, 42, 48, 42)
        layout.setSpacing(22)

        title = QLabel("J A R V I S")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.status = QLabel("SYSTEM READY  •  OFFLINE MODE")
        self.status.setObjectName("status")
        self.status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status)

        ring = QLabel("◉")
        ring.setObjectName("ring")
        ring.setAlignment(Qt.AlignCenter)
        layout.addWidget(ring, 1)

        panel = QFrame()
        panel.setObjectName("panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setSpacing(10)
        self.heard = QLabel("YOU: —")
        self.answer = QLabel("JARVIS: Menunggu perintah, Master.")
        for label in (self.heard, self.answer):
            label.setWordWrap(True)
            panel_layout.addWidget(label)
        layout.addWidget(panel)

        self.button = QPushButton("MULAI DENGARKAN (6 DETIK)")
        self.button.clicked.connect(self.start_listening)
        layout.addWidget(self.button)

        hint = QLabel('Coba ucapkan: "Siapa gua?" / "Halo Jarvis" / "Siapa kamu?"')
        hint.setObjectName("hint")
        hint.setAlignment(Qt.AlignCenter)
        hint.setWordWrap(True)
        layout.addWidget(hint)
        self.setCentralWidget(root)
        self.setStyleSheet("""
            QWidget#root { background: #06111f; color: #d5f6ff; font-family: 'Segoe UI'; }
            QLabel#title { color: #59dfff; font-size: 38px; font-weight: 700; }
            QLabel#status { color: #72aabb; font-size: 13px; }
            QLabel#ring { color: #18c8f5; font-size: 126px; }
            QFrame#panel { background: #0d2637; border: 1px solid #1d6681; border-radius: 12px; padding: 12px; }
            QFrame#panel QLabel { font-size: 15px; }
            QPushButton { background: #087da4; color: white; border: 1px solid #45d7ff;
                          border-radius: 9px; padding: 15px; font-size: 15px; font-weight: 700; }
            QPushButton:hover { background: #0b9dc7; }
            QPushButton:disabled { background: #315060; color: #a8b9c0; }
            QLabel#hint { color: #7f9da8; font-size: 12px; }
        """)
        if not MODEL_PATH.is_dir():
            self.status.setText("MODEL VOSK BELUM TERPASANG — LIHAT README")

    @Slot()
    def start_listening(self):
        if not MODEL_PATH.is_dir():
            self.status.setText("ERROR: MODEL TIDAK DITEMUKAN")
            self.answer.setText("JARVIS: Letakkan model Bahasa Indonesia di models/vosk-id.")
            return
        self.button.setEnabled(False)
        self.status.setText("LISTENING  •  BICARA SEKARANG (6 DETIK)")
        self.heard.setText("YOU: Mendengarkan...")
        self.answer.setText("JARVIS: —")
        self.thread = QThread(self)
        self.worker = VoiceWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.recognized.connect(self.on_recognized)
        self.worker.failed.connect(self.on_failed)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.on_finished)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    @Slot(str, str)
    def on_recognized(self, transcript, response):
        self.heard.setText(f"YOU: {transcript or '(tidak terdeteksi)'}")
        self.answer.setText(f"JARVIS: {response}")
        self.status.setText("RESPONDING  •  SPEAKING")

    @Slot(str)
    def on_failed(self, message):
        self.status.setText("AUDIO ERROR")
        self.answer.setText(f"JARVIS: {message}")

    @Slot()
    def on_finished(self):
        self.button.setEnabled(True)
        if self.status.text() != "AUDIO ERROR":
            self.status.setText("SYSTEM READY  •  OFFLINE MODE")
        self.thread = None
        self.worker = None


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
