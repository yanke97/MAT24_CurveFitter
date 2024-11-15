from pathlib import Path

from functools import partial
from datetime import datetime
from PyQt5.QtWidgets import QLineEdit

from CF_Gui import CFAppGui
from CF_Errors import FileError


class CfCtrl:
    def __init__(self, gui: CFAppGui, model):
        self._gui = gui
        self._model = model
        self._data = []
        self._connect_signals()
        self._update_status("Application started.")

    def _connect_signals(self):
        # functions (slots) triggered by events (signals) usually need to be
        # able to be called with out additonal arguments. But some times it
        # might be necessary to call a function with arguments.
        # partial asures that the assigned function can be called without the
        # amount of additional arguments expected (0 or more). This is even
        # necessary when callng a function with no argument since in a GUI
        # context there might arise issues caused by additional functenalities
        # executed when calling a function(eg. need to manage GUI updates or
        # retrieve data that the button click affects) resulting in more
        # arguments than expected.
        # https://realpython.com/python-pyqt-gui-calculator/#creating-a-calculator-app-with-python-and-pyqt

        self._gui.btn_file_in.clicked.connect(
            partial(self._file_dialog, "*.csv"))

        self._gui.btn_file_out.clicked.connect(
            partial(self._file_dialog, "*.k"))

        self._gui.tb_in_path.returnPressed.connect(self._get_data)

        self._gui.btn_fit.clicked.connect(self._fit_extrap)

    def _update_status(self, text: str, msg_type: str = "") -> None:
        """
        Update Statusbar with the given string
        ...

        Parameters
        ----------
        text: str
            text to be displayed in the status bar
        msg_type: str
            string defining the type of message. 
            Either "error" or empty. Defaults to empty.

        Returns
        -------
        None
        """

        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        self._gui.statusBar().showMessage(f"{timestamp} >>> {text}", 3600000)

        if msg_type == "error":
            self._gui.statusBar().setStyleSheet("background-color : red")
        else:
            self._gui.statusBar().setStyleSheet("background-color : #BDD5E7")

    def _file_dialog(self, file_type: str) -> None:
        path, _ = self._gui.file_dialog(file_type)

        self._update_tb(self._gui.tb_in_path, str(path))
        self._get_data(path)

    def _update_tb(self, tb: QLineEdit, text: str) -> None:
        tb.setText(text)

    def _get_data(self, user_input: str = "") -> None:
        if not user_input:
            file_path: Path = Path(
                self._gui.tb_in_path.text().replace("\"", ""))
        else:
            file_path: Path = Path(user_input)

        try:
            self._data = self._model.get_data_from_file(file_path)
            self._gui.plot_data(self._data, "input")
            self._update_status(
                f"Updated plot with data from {file_path.name}")
        except FileError as error:
            self._update_status(
                f"{type(error).__name__} - {error.args[0]}", "error")

    def _fit_extrap(self) -> None:
        self._data = self._model.comp_real_stress_strain(self._data)
        self._gui.plot_data(self._data, "output")
        E, Rp_02, Rm, Rp_02_I, Rm_I = self._model.comp_material_data(
            self._data)
        print(Rm)
        self._gui.plot_data(
            [self._data["eng_strain"][0:300], self._data["eng_strain"][0:300]*E],
            "output", name="Youngs Modulus")
        self._gui.plot_data([self._data["strain"][Rp_02_I],
                            Rp_02], "output", "o", "Rp_02")
        self._gui.plot_data(
            [self._data["strain"][Rm_I], Rm], "output", "o", "Rm")
