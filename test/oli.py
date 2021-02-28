

import sys

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout


from test_gui import MyApp


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
