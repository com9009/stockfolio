

import sys

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout

from test_gui import MyApp
from worker import WorkerQueue




if __name__ == '__main__':

    q = WorkerQueue(5)
    q.start()

    app = QApplication(sys.argv)

    ex = MyApp()


    sys.exit(app.exec_())
