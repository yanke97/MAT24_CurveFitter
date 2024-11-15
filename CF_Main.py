import sys
from CF_Gui import CFAppGui
from PyQt5.QtWidgets import (QApplication)

from CF_Ctrl import CfCtrl
import CF_Model


def main():
    app = QApplication(sys.argv)
    # sys.argv calls the list of all arguments passed when executing the script
    # from the command line. It can be replaced by an empty list but calling the
    # argument list provides ability to manipulate script behaviour during
    # program call

    gui = CFAppGui()
    gui.show()

    CfCtrl(gui, CF_Model)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
