import sys
import cv2
import os
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QSlider, QListWidget, QListWidgetItem, QHBoxLayout, QMessageBox


class VideoPlayerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.video_folder = 'output_videos'
        self.video_files = [f for f in os.listdir(
            self.video_folder) if f.endswith('.mp4')]
        self.video_index = 0
        self.current_video_path = os.path.join(
            self.video_folder, self.video_files[self.video_index])

        self.cap = cv2.VideoCapture(self.current_video_path)
        self.frame_rate = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.current_frame = 0
        self.playing = False

        self.initUI()

        if self.frame_rate > 0:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(1000 // self.frame_rate)

    # Configure the UI Designs
    def initUI(self):
        self.setWindowTitle("Video Player")
        self.setGeometry(100, 100, 800, 600)

        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setScaledContents(True)
        # The Buttons are set up here
        self.play_pause_button = QPushButton("Play")
        self.fast_forward_button = QPushButton("Fast Forward")
        self.rewind_button = QPushButton("Rewind")
        self.duration_slider = QSlider(Qt.Horizontal)

        self.playlist_widget = QListWidget(self)
        playlist_header = QListWidgetItem(
            "Double-click on the files below and press 'PLAY'")
        playlist_header.setFlags(Qt.ItemIsEnabled)
        header_font = playlist_header.font()
        header_font.setBold(True)
        playlist_header.setFont(header_font)
        self.playlist_widget.insertItem(0, playlist_header)
        self.playlist_widget.addItems(self.video_files)
        self.playlist_widget.itemDoubleClicked.connect(
            self.load_selected_video)

        self.remove_clip_button = QPushButton("Remove Clip")
        self.remove_clip_button.clicked.connect(self.remove_selected_clip)

        self.close_button = QPushButton("Close App")
        self.close_button.clicked.connect(self.close)
        # Button layouts
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.play_pause_button)
        buttons_layout.addWidget(self.fast_forward_button)
        buttons_layout.addWidget(self.rewind_button)
        buttons_layout.addWidget(self.duration_slider)

        playlist_layout = QVBoxLayout()
        playlist_layout.addWidget(self.playlist_widget)
        playlist_layout.addWidget(self.remove_clip_button)
        playlist_layout.addWidget(self.close_button)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.video_label, 3)
        main_layout.addLayout(playlist_layout, 1)

        lower_layout = QVBoxLayout()
        lower_layout.addLayout(main_layout)
        lower_layout.addLayout(buttons_layout)

        self.setLayout(lower_layout)

        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        self.fast_forward_button.clicked.connect(self.fast_forward)
        self.rewind_button.clicked.connect(self.rewind)
        self.duration_slider.valueChanged.connect(self.seek_video)

    # Play/Pause Function
    def toggle_play_pause(self):
        if self.playing:
            self.play_pause_button.setText("Play")
            self.playing = False
        else:
            self.play_pause_button.setText("Pause")
            self.playing = True

    # Rewind Function
    def rewind(self):
        # Rewind by 10 seconds
        new_frame = max(0, self.current_frame - self.frame_rate * 10)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
        self.current_frame = new_frame
        self.duration_slider.setValue(new_frame)
    # Fastword Function

    def fast_forward(self):
        new_frame = min(self.total_frames, self.current_frame +
                        self.frame_rate * 10)  # Fast forward by 10 seconds
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
        self.current_frame = new_frame
        self.duration_slider.setValue(new_frame)
    # Progress Bar

    def seek_video(self):
        new_frame = self.duration_slider.value()
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
        self.current_frame = new_frame
    # Playlist function

    def load_selected_video(self, item):
        selected_video = item.text()
        self.video_index = self.video_files.index(selected_video)
        self.current_video_path = os.path.join(
            self.video_folder, selected_video)
        self.cap.release()
        self.cap = cv2.VideoCapture(self.current_video_path)
        self.frame_rate = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.current_frame = 0
        self.duration_slider.setMaximum(self.total_frames)
        self.toggle_play_pause()
    # Delete Function

    def remove_selected_clip(self):
        selected_item = self.playlist_widget.currentItem()
        if selected_item is None:
            QMessageBox.warning(
                self, "Warning", "Please choose a file to delete")
            return

        selected_video = selected_item.text()
        selected_index = self.playlist_widget.row(selected_item)

        # Check if the selected item is the header or if no video is currently playing
        if selected_video == "Double-click on the files below and press 'PLAY'" or self.current_video_path is None:
            QMessageBox.warning(
                self, "Warning", "Please choose a valid video file to delete")
            return

        # Check if the selected video is the currently playing video
        if selected_video == os.path.basename(self.current_video_path):
            confirmation = QMessageBox.question(
                self, "Confirmation",
                f"Are you sure you want to delete '{selected_video}'?\n The Playback will Stop",
                QMessageBox.Yes | QMessageBox.No
            )

            if confirmation == QMessageBox.Yes:
                self.cap.release()
                self.current_video_path = None
                self.video_label.clear()
                self.video_files.remove(selected_video)
                self.playlist_widget.takeItem(selected_index)
                video_path = os.path.join(self.video_folder, selected_video)
                os.remove(video_path)
            return

        # For other selected videos
        confirmation = QMessageBox.question(
            self, "Confirmation",
            f"Are you sure you want to delete '{selected_video}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmation == QMessageBox.Yes:
            video_path = os.path.join(self.video_folder, selected_video)
            os.remove(video_path)
            self.video_files.remove(selected_video)
            self.playlist_widget.takeItem(selected_index)

    def update_frame(self):
        if self.playing:
            if self.current_video_path is None:
                return  # Display a blank screen if no current video

            ret, frame = self.cap.read()
            if ret:
                self.current_frame += 1
                self.duration_slider.setValue(self.current_frame)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame_rgb.shape
                bytes_per_line = ch * w
                frame_qimg = QImage(frame_rgb.data, w, h,
                                    bytes_per_line, QImage.Format_RGB888)
                frame_pixmap = QPixmap.fromImage(frame_qimg)
                self.video_label.setPixmap(frame_pixmap)
            else:
                self.toggle_play_pause()


def main():
    app = QApplication(sys.argv)
    window = VideoPlayerApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
