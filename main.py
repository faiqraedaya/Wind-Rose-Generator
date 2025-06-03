import sys
from PyQt5.QtWidgets import QApplication
from windrose.windrose_app import WindRoseApp

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WindRoseApp()
    window.show()
    sys.exit(app.exec_()) 