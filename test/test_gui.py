from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout

from test_module import work_test

class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        btn1 = QPushButton('test button', self)
        btn1.clicked.connect(work_test)

        self.setWindowTitle("stockfolio")
        self.move(300, 300)
        self.resize(400, 200)
        self.show()