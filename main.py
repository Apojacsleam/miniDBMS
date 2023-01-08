import sys
from LoginGUI import Ui_Form
from PyQt5 import QtWidgets

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainGUI = Ui_Form()
    mainGUI.show()
    sys.exit(app.exec())