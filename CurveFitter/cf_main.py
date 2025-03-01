import sys
from pathlib import Path

from cf_gui import CFAppGui
import cf_model
from cf_ctrl import CfCtrl

from PyQt5.QtWidgets import (QApplication)


def _get_cwd() -> Path:
    """
    Get the current working directory
    ...

    Parametes
    ---------
    None

    Returns
    -------
    cwd: Path
        current working directory
    """

    # determine if application is a script file or frozen exe
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent.parent
    elif __file__:
        return Path(__file__).parent.parent


def main() -> None:
    """
    Main function of *Mat24_CurveFitter
    ...

    Parametes
    ---------
    None

    Returns
    -------
    None
    """

    app = QApplication(sys.argv)
    # sys.argv calls the list of all arguments passed when executing the script
    # from the command line. It can be replaced by an empty list but calling the
    # argument list provides ability to manipulate script behaviour during
    # program call

    cwd = _get_cwd()

    gui = CFAppGui(cwd)
    gui.show()

    CfCtrl(gui, cf_model, cwd)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
