from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit

# from test_module import work_test



class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.message = ""


    def initUI(self):


        self.lbl1 = QLabel("results :")
        self.textedit = QTextEdit()
        self.textedit.setAcceptRichText(False)

        self.btn1 = QPushButton('test button', self)
        # self.btn1.clicked.connect(self.work_test)

        # self.btn1.clicked.connect(q.add(self.work_test))

        vbox = QVBoxLayout()
        vbox.addStretch()
        vbox.addWidget(self.lbl1)
        vbox.addWidget(self.textedit)
        vbox.addWidget(self.btn1)
        vbox.addStretch()

        
        self.setLayout(vbox)

        self.setWindowTitle("stockfolio test")
        self.setGeometry(300, 300, 300, 300)
        self.show()


    def work_test(self):
        self.message += "hello\n"
        self.textedit.setText(self.message)