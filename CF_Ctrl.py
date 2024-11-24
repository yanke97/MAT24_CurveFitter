from pathlib import Path
import pandas as pd

from functools import partial
from datetime import datetime
from PyQt5.QtWidgets import QLineEdit

from CF_Gui import CFAppGui
from CF_Errors import FileError, ExportPointNoError
from CF_ExportDialog import ExportDialog


class CfCtrl:
    def __init__(self, gui: CFAppGui, model):
        self._gui = gui
        self._model = model
        self._data = pd.DataFrame()
        self._fitted_data = []
        self._mat_characteristics = []
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

        self._gui.btn_export.clicked.connect(self._export)

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

        if file_type == "*.csv":
            self._update_tb(self._gui.tb_in_path, str(path))
            self._get_data(path)
        else:
            self._update_tb(self._gui.tb_out_path, str(path))

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
        self._gui.plot_data(self._data, "output_1")
        self._data, self._mat_characteristics = self._model.comp_material_data(
            self._data)

        self._update_status("Material properties calculated.")

        self._gui.plot_data(
            [self._data["eng_strain"][0:self._mat_characteristics[3]],
                self._data["eng_strain"][0:self._mat_characteristics[3]]*self._mat_characteristics[0]],
            "output_1", name=f"Youngs Modulus ({self._mat_characteristics[0]:.2f})")
        self._gui.plot_data([self._data["strain"][self._mat_characteristics[3]],
                            self._mat_characteristics[1]], "output_1", "o", name=f"Rp_02 ({self._mat_characteristics[1]:.2f})")
        self._gui.plot_data(
            [self._data["strain"][self._mat_characteristics[4]], self._mat_characteristics[2]], "output_1", "o", name=f"Rm ({self._mat_characteristics[2]:.2f})")

        self._gui.plot_data([self._data["plastic_strain"],
                            self._data["plastic_stress"]], "output_2", name="input data")

        self._fitted_data = self._model.extrapolate(
            [self._data, self._mat_characteristics[3], self._mat_characteristics[4], self._mat_characteristics[5], self._mat_characteristics[2]], "Swift")

        self._gui.plot_data(self._fitted_data, "output_2",
                            name="Swift-extrapolation")

        self._update_status("Curve Extrapolated.")

    def _export(self):
        export_dlg = ExportDialog(
            round(self._mat_characteristics[6], 2), self._gui)
        if export_dlg.exec() == 1:

            title = export_dlg.tb_title.text()
            mid = export_dlg.tb_mid.text()
            rho = export_dlg.tb_rho.text()
            poisons_ratio = export_dlg.tb_poisons_ratio.text()
            fail = export_dlg.tb_fail.text()
            point_no = export_dlg.tb_point_no.text()
            if export_dlg.rdbtn_equi.isChecked() is True:
                spacing = "equi"
            else:
                spacing = "uneven"

            try:
                self._model.export_data(title, mid, rho, poisons_ratio,
                                        fail, int(
                                            point_no), spacing, self._fitted_data,
                                        self._mat_characteristics[0], self._gui.tb_out_path.text())
            except ExportPointNoError as error:
                self._update_status(
                    f"{type(error).__name__} - {error.args[0]}", "error")
                self._export()

        else:
            print("Fail")
