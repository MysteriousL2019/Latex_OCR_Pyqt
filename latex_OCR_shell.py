import sys
import time
import pyperclip
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PIL import ImageGrab
from pix2tex.cli import LatexOCR
from PyQt5.QtWidgets import QMessageBox,QGroupBox,QLabel,QTextEdit,QScrollArea


class LatexRecognitionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.last_message_box = None  # 用于跟踪上一个消息框
        self.last_message_box_confirmed = False  # 用于标记上一个消息框是否被确认


    def init_ui(self):
        self.setWindowTitle('OCR LaTeX Recognition')
        self.setGeometry(100, 100, 350, 300)
        self.setFixedSize(350, 300)
        self.label = QLabel("OCR LaTeX Recognition")
        # layout = QVBoxLayout()
        self.button_group = QGroupBox('OCR LaTeX Recognition')
        layout = QVBoxLayout(self.button_group)

        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-family: Alias, sans-serif; font-size: 24px; font-weight: bold;")

        self.start_button = QPushButton('Start', self)
        self.start_button.setObjectName('start-button')
        self.quit_button = QPushButton('Quit', self)
        self.quit_button.setObjectName('quit-button')
        self.text_edit = QTextEdit(self)  # 添加一个文本框
        self.text_edit.setReadOnly(True)  # 禁止编辑
        self.text_edit.setPlaceholderText("Text from clipboard will appear here")
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.text_edit)
        layout.addWidget(self.label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.quit_button)
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)
        #  创建 QSS 样式表，将样式属性应用到按钮
        qss = """
        #start-button {
            background-color: #007AFF;
            color: #fff;
            font-size: 16px;
            padding: 10px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        #quit-button {
            background-color: #FF3B30;
            color: #fff;
            font-size: 16px;
            padding: 10px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        .quit {
            background-color: #FF3B30;
            color: #fff;
            font-size: 16px;
            padding: 10px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        QGroupBox {
            max-width: 300px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fff;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        }
        """
        self.setStyleSheet(qss)

        self.start_button.clicked.connect(self.start_ocr)
        self.quit_button.clicked.connect(self.quit_application)

        self.ocr_thread = OcrThread()
        self.ocr_thread.ocr_signal.connect(self.update_latex)
        

    def start_ocr(self):
        self.ocr_thread.start()
        print('begin')
        if self.last_message_box_confirmed:
            pass
        else:
            self.show_message_box('OCR process started.')


    def update_latex(self, latex):
        if latex:
            clipboard = QApplication.clipboard()
            clipboard_text = clipboard.text()
            latex_code = f'\\begin{{align}}{latex}\\end{{align}}'
            pyperclip.copy(latex_code)
            if clipboard_text:
                self.text_edit.setPlainText(clipboard_text)
            if self.last_message_box_confirmed:
                pass
            else:
                self.show_message_box('OCR process completed and LaTeX copied to clipboard.')

    def show_message_box(self, message):
        self.last_message_box_confirmed = True

        message_box = QMessageBox()
        message_box.setWindowTitle('Information')
        message_box.setText(message)
        message_box.exec_()
        if message_box.clickedButton() == message_box.button(QMessageBox.Ok):
            self.last_message_box_confirmed = False
        self.last_message_box = message_box

    def quit_application(self):
        result = QMessageBox.question(self, 'Warning', 'Are you sure you want to quit the application?', 
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if result == QMessageBox.Yes:
            self.ocr_thread.stop()
            print('end')
            app.quit()
        else:
            return

class OcrThread(QThread):
    ocr_signal = pyqtSignal(str)
    running = True

    def run(self):
        model = LatexOCR()
        while self.running:
            img = ImageGrab.grabclipboard()
            if img!=None:
                latex = str(model(img))
                self.ocr_signal.emit(latex)
            time.sleep(0.5)

    def stop(self):
        self.running = False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LatexRecognitionApp()
    window.show()
    sys.exit(app.exec_())


