from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt
from PySide6.QtWidgets import (
    QApplication, QFrame, QLabel, QMainWindow, QPushButton, QProgressBar,
    QVBoxLayout, QWidget,
)

from jarvis.commands import handle_command
from jarvis.tts import speak
from jarvis.voice import transcribe_once

MODEL_NAME = "small"


class VoiceWorker(QObject):
    status_changed = Signal(str)
    audio_level = Signal(int, float)
    recognized = Signal(str, str)
    failed = Signal(str)
    finished = Signal()

    @Slot()
    def run(self):
        try:
            transcript = transcribe_once(MODEL_NAME, on_status=self.status_changed.emit,
                                       on_audio_level=self.audio_level.emit)
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

        self.voice_indicator = QLabel("MICROPHONE  •  STANDBY")
        self.voice_indicator.setObjectName("voice_indicator")
        self.voice_indicator.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.voice_indicator)

        self.audio_meter = QProgressBar()
        self.audio_meter.setRange(0, 100)
        self.audio_meter.setValue(0)
        self.audio_meter.setTextVisible(False)
        layout.addWidget(self.audio_meter)

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
            QLabel#voice_indicator { color: #8cb4c2; font-size: 13px; font-weight: 600; }
            QProgressBar { background: #0d2637; border: 1px solid #1d6681; border-radius: 6px; height: 13px; }
            QProgressBar::chunk { background: #18c8f5; border-radius: 5px; }
            QLabel#hint { color: #7f9da8; font-size: 12px; }
        """)

    @Slot()
    def start_listening(self):
        self.button.setEnabled(False)
        self.status.setText("PREPARING  •  MENYIAPKAN WHISPER")
        self.heard.setText("YOU: Menunggu rekaman...")
        self.voice_indicator.setText("MICROPHONE  •  MENYIAPKAN")
        self.audio_meter.setValue(0)
        self.answer.setText("JARVIS: —")
        self.thread = QThread(self)
        self.worker = VoiceWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.status_changed.connect(self.on_status_changed)
        self.worker.audio_level.connect(self.on_audio_level)
        self.worker.recognized.connect(self.on_recognized)
        self.worker.failed.connect(self.on_failed)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.on_finished)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    @Slot(str)
    def on_status_changed(self, message):
        self.status.setText(message)
        if message.startswith("LOADING"):
            self.voice_indicator.setText("MICROPHONE  •  MENUNGGU MODEL")
        elif message.startswith("PROCESSING"):
            self.voice_indicator.setText("MICROPHONE  •  REKAMAN SELESAI")
            self.audio_meter.setValue(0)

    @Slot(int, float)
    def on_audio_level(self, level, remaining):
        self.audio_meter.setValue(level)
        detected = level >= 8
        self.voice_indicator.setText(
            f"{'SUARA TERDETEKSI' if detected else 'MENDENGARKAN'}"
            f"  •  {remaining:.1f} DETIK TERSISA"
        )
        self.voice_indicator.setStyleSheet(
            "color: #52f5ab;" if detected else "color: #8cb4c2;"
        )

    @Slot(str, str)
    def on_recognized(self, transcript, response):
        self.heard.setText(f"YOU: {transcript or '(tidak terdeteksi)'}")
        self.answer.setText(f"JARVIS: {response}")
        self.status.setText("RESPONDING  •  SPEAKING")

    @Slot(str)
    def on_failed(self, message):
        self.status.setText("AUDIO ERROR")
        self.voice_indicator.setText("MICROPHONE  •  ERROR")
        self.audio_meter.setValue(0)
        self.answer.setText(f"JARVIS: {message}")

    @Slot()
    def on_finished(self):
        self.button.setEnabled(True)
        self.audio_meter.setValue(0)
        self.voice_indicator.setText("MICROPHONE  •  STANDBY")
        self.voice_indicator.setStyleSheet("")
        if self.status.text() != "AUDIO ERROR":
            self.status.setText("SYSTEM READY  •  OFFLINE MODE")
        self.thread = None
        self.worker = None


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
