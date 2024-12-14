from sys import exit as sys_exit
from configparser import ConfigParser
from pathlib import Path
import pandas as pd

from functools import partial
from datetime import datetime
from PyQt5.QtWidgets import QLineEdit

from CF_Gui import CFAppGui
from CF_Errors import FileError, ExportPointNoError, DataError
from CF_ExportDialog import ExportDialog
from CF_SettingsDialog import SettingsDialog


class CfCtrl:
    def __init__(self, gui: CFAppGui, model):
        self._gui = gui
        self._export_dlg = None
        self._settings_dlg = None
        self._model = model
        self._data = pd.DataFrame()
        self._fitted_data = []
        self._mat_characteristics = []
        self._extrap_method: str = ""
        self._e_start: int = 0
        self._e_end: int = 0
        self._template_path_str: str = ""

        self._read_ini()
        self._connect_signals()
        self._update_status("Application started.")

    def _read_ini(self) -> None:
        parser = ConfigParser()
        parser.read(r"e:\15_MAT24_Curve fitter\CF.ini")

        self._extrap_method: int = parser.getint(
            "extrapolation_fitting", "extrapolation_method")
        self._e_start: int = parser.getint(
            "extrapolation_fitting", "e_extrap_start")
        self._e_end: int = parser.getint(
            "extrapolation_fitting", "e_extrap_end")
        self._template_path_str: str = parser.get("export", "template_path")

    def _write_ini(self, e_start: str, e_end: str, extrap_method: str,
                   template_path_str: str) -> None:
        parser = ConfigParser()
        parser.read(r"e:\15_MAT24_Curve fitter\CF.ini")
        parser.set("extrapolation_fitting", "e_extrap_start", e_start)
        parser.set("extrapolation_fitting", "e_extrap_end", e_end)
        parser.set("extrapolation_fitting",
                   "extrapolation_method", extrap_method)
        parser.set("export", "template_path", template_path_str)

        with open(r"e:\15_MAT24_Curve fitter\CF.ini", "w") as configfile:
            parser.write(configfile)

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

        self._gui.import_action.triggered.connect(
            partial(self._file_dialog, "*.csv"))

        self._gui.fit_action.triggered.connect(self._fit_extrap)

        self._gui.settings_action.triggered.connect(self._settings)

        self._gui.export_action.triggered.connect(self._export)

        self._gui.exit_action.triggered.connect(self._exit_app)

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

    def _file_dialog(self, file_type: str, identifier: str) -> None:
        path, _ = self._gui.file_dialog(file_type)

        if file_type == "*.csv":
            self._update_tb(self._gui.tb_in_path, str(path))
            self._get_data(path)
        elif file_type == "*.k" and identifier == "export":
            self._update_tb(self._export_dlg.tb_out_path, str(path))
        elif file_type == "*.k" and identifier == "setting":
            self._update_tb(self._settings_dlg.tb_template_path, str(path))

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
            self._gui.clear_graphs("input")
            self._gui.plot_data(self._data, "input")
            self._update_status(
                f"Updated plot with data from {file_path.name}")
        except (FileError, DataError) as error:
            self._update_status(
                f"{type(error).__name__} - {error.args[0]}", "error")

    def _fit_extrap(self) -> None:
        if self._data.empty:
            self._update_status("No data found, please import data.", "error")

        else:
            self._mat_characteristics = self._model.comp_material_data(
                self._data, self._e_start, self._e_end)
    
            self._data = self._model.comp_true_stress_strain(
                self._data, self._mat_characteristics[3], self._mat_characteristics[4])
            self._update_status("Material properties calculated.")
    
            self._fitted_data = self._model.extrapolate(
                [self._data, self._mat_characteristics[3], self._mat_characteristics[4],
                 self._mat_characteristics[5], self._mat_characteristics[2]], self._extrap_method)
            self._update_status("Yield Curve computed.")
    
            self._gui.fill_lbls(self._mat_characteristics,
                                self._extrap_method, self._fitted_data[2])
    
            self._gui.clear_graphs("output_1")
            self._gui.plot_data(self._data, "output_1")
    
            self._gui.plot_data(
                [self._data["eng_strain"][0:self._mat_characteristics[3]],
                    self._data["eng_strain"][0:self._mat_characteristics[3]]*self._mat_characteristics[0]],
                "output_1", name=f"Youngs Modulus ({self._mat_characteristics[0]:.2f})")
    
            self._gui.clear_graphs("output")
            self._gui.plot_data([self._data["plst_strain"],
                                 self._data["plst_stress"]], "output", name="Input Data")
            self._gui.plot_data(self._fitted_data, "output",
                                name="Fitted Yield Curve")

    def _export(self):
        if not self._mat_characteristics:
            self._update_status("No Data to Export.", "error")

        else:
            self._export_dlg = ExportDialog(
                round(self._mat_characteristics[6], 2), self._gui)

            # when the firs btn in the box (Save) is clicked an accepted signal is
            # emitted since this btn has a acceptive role in the GUI. This signal
            # is than connected to the accept method of the dialog. Similar is true
            # for the secend btn which has a rejective role in the GUI
            self._export_dlg.btnbx.accepted.connect(self._export_dlg.accept)
            self._export_dlg.btnbx.rejected.connect(self._export_dlg.reject)
            self._export_dlg.btn_file_out.clicked.connect(
                partial(self._file_dialog, "*.k", "export"))

            if self._export_dlg.exec() == 1:

                title = self._export_dlg.tb_title.text()
                mid = self._export_dlg.tb_mid.text()
                rho = self._export_dlg.tb_rho.text()
                poisons_ratio = self._export_dlg.tb_poisons_ratio.text()
                fail = self._export_dlg.tb_fail.text()
                point_no = int(self._export_dlg.tb_point_no.text())
                export_path = self._export_dlg.tb_out_path.text()
                if self._export_dlg.rdbtn_equi.isChecked() is True:
                    spacing = "equi"
                else:
                    spacing = "uneven"

                try:
                    self._model.export_data(title, mid, rho, poisons_ratio,
                                            fail, point_no, spacing, self._fitted_data,
                                            self._mat_characteristics[0], export_path, self._template_path_str)
                    self._update_status(
                        f"Succesfully exported curve to {export_path}.")

                except (ExportPointNoError, FileError) as error:
                    self._update_status(
                        f"{type(error).__name__} - {error.args[0]}", "error")
                    self._export()

    def _exit_app(self):
        sys_exit()

    def _settings(self):
        extrap_methods = ["Swift", "Voce", "Swift-Voce"]
        self._settings_dlg = SettingsDialog(extrap_methods, self._extrap_method, self._e_start,
                                            self._e_end, self._template_path_str,
                                            self._gui)

        self._settings_dlg.btnbx.rejected.connect(self._settings_dlg.reject)
        self._settings_dlg.btnbx.accepted.connect(self._settings_dlg.accept)
        self._settings_dlg.btn_temp_path.clicked.connect(
            partial(self._file_dialog, "*.k", "settings"))

        if self._settings_dlg.exec() == 1:
            if int(self._settings_dlg.tb_e_end.text()) - int(self._settings_dlg.tb_e_start.text()) < 50:
                self._update_status(
                    "It is recommended to use at least 50 data points to fit the Youngs Modulus. Changes discarded.", "error")
                self._settings()
            else:
                self._e_start = int(self._settings_dlg.tb_e_start.text())
                self._e_end = int(self._settings_dlg.tb_e_end.text())
                self._extrap_method = self._settings_dlg.cmb_extrap_method.currentIndex()
                self._template_path_str = self._settings_dlg.tb_template_path.text()

                self._write_ini(str(self._e_start), str(self._e_end), str(self._extrap_method),
                                self._template_path_str)

                self._update_status("New Settings saved.")
        else:
            self._update_status("Changed Settings discarded.")
