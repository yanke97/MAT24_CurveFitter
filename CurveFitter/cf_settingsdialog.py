from PyQt5.QtWidgets import (QDialog, QPushButton, QDialogButtonBox, QLineEdit,
                             QLabel, QFormLayout, QSpacerItem, QComboBox, QSizePolicy, QFrame)
from PyQt5.QtGui import (QFont, QIcon)
from pathlib import Path


class SettingsDialog(QDialog):
    def __init__(self, cwd: Path, extrap_methods: list[str], extrap_index: int, e_start: int, e_end: int,
                 template_path_str: str, parent=None) -> None:
        """
        Settings Dialogs init function.
        ...

        Parameter
        ---------
        cwd: Path
            path to current working directory
        extrap_methods: list[str]
            list containing the available extrapolation methods
        extrap_index: int
            the currently used extrapolation method represented by an integer
        e_start:int
            index of the datapoint at which the interval for the youngs modulus extrapolation starts.
        e_end:int
            index of the datapoint at which the interval for the youngs modulus extrapolation ends.
        template_path_str:
            path to the .k-file template as a string.
        parent: QWidget
            parent widget of the dialog, defaults to None.

        Return
        ------
        None
        """

        super().__init__(parent)

        self.setWindowTitle("Settings")
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._create_fonts()
        self._create_btns(cwd)
        self._create_lbls()
        self._create_tbs(e_start, e_end, template_path_str)
        self._create_cmbs(extrap_methods, extrap_index)
        self._create_line()
        self._create_spacers()
        self._layout = QFormLayout()
        self.setLayout(self._layout)

        self._layout.addRow(self._lbl_title_fit_extrap)
        self._layout.addRow(self._lbl_e_points)
        self._layout.addItem(self._spacer_1)
        self._layout.addRow(self._lbl_e_start, self._lbl_e_end)
        self._layout.addRow(self.tb_e_start, self.tb_e_end)
        self._layout.addItem(self._spacer_2)
        self._layout.addRow(self._lbl_extrap_method)
        self._layout.addRow(self.cmb_extrap_method)
        self._layout.addRow(self._line)
        self._layout.addRow(self._lbl_title_export)
        self._layout.addRow(self._lbl_template_path)
        self._layout.addRow(self.btn_temp_path, self.tb_template_path)
        self._layout.addItem(self._spacer_3)
        self._layout.addRow(self.btnbx)

    def _create_btns(self, cwd: Path) -> None:
        """
        Create the buttons for the dialog.
        ...

        Parameter
        ---------
        cwd: Path
            path to current working directory

        Return
        ------
        None
        """

        btns = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.btnbx = QDialogButtonBox(btns)

        self.btn_temp_path = QPushButton()
        self.btn_temp_path.setBaseSize(25, 25)
        self.btn_temp_path.setIcon(
            QIcon(str(cwd/"data"/"open-folder.png")))

    def _create_lbls(self) -> None:
        """
        Create the labels necessary for the dialog.
        ...

        Parameter
        ---------
        None

        Returns
        -------
        None
        """

        self._lbl_title_fit_extrap = QLabel(
            "Curve Fitting & Extrapolation")
        self._lbl_title_fit_extrap.setFont(self._title_font)
        self._lbl_e_points = QLabel(
            "Datapoint Range for Youngs Modulus fitting")
        self._lbl_e_points.setFont(self._font)
        self._lbl_e_start = QLabel("Start")
        self._lbl_e_start.setFont(self._font)
        self._lbl_e_end = QLabel("End")
        self._lbl_e_end.setFont(self._font)
        self._lbl_extrap_method = QLabel("Extrapolation Method")
        self._lbl_extrap_method.setFont(self._font)

        self._lbl_title_export = QLabel("Export")
        self._lbl_title_export.setFont(self._title_font)
        self._lbl_template_path = QLabel("Template File")
        self._lbl_template_path.setFont(self._font)

    def _create_tbs(self, e_start: int, e_end: int, template_path_str: str) -> None:
        """
        Create the textboxes necessary for the dialog.
        ...

        Parameter
        ---------
        e_start:int
            index of the datapoint at which the interval for the youngs modulus extrapolation starts.
        e_end:int
            index of the datapoint at which the interval for the youngs modulus extrapolation ends.
        template_path_str:
            path to the .k-file template as a string.

        Return
        ------
        None
        """

        self.tb_e_start = QLineEdit(str(e_start))
        self.tb_e_start.setFont(self._font)
        self.tb_e_start.setFixedSize(50, 25)
        self.tb_e_end = QLineEdit(str(e_end))
        self.tb_e_end.setFont(self._font)
        self.tb_e_end.setFixedSize(50, 25)
        self.tb_template_path = QLineEdit(template_path_str)
        self.tb_template_path.setFont(self._font)
        self.tb_template_path.setFixedSize(200, 25)

    def _create_cmbs(self, extrap_methods: list[str], extrap_index: int) -> None:
        """
        Create the comboboxes necessary for the dialog.
        ...

        Parameter
        ---------
        extrap_methods: list[str]
            list containing the available extrapolation methods
        extrap_index: int
            the currently used extrapolation method represented by an integer

        Returns
        -------
        None
        """

        self.cmb_extrap_method = QComboBox()
        self.cmb_extrap_method.setFixedSize(175, 25)
        self.cmb_extrap_method.setFont(self._font)
        self.cmb_extrap_method.addItems(extrap_methods)
        self.cmb_extrap_method.setCurrentIndex(extrap_index)

    def _create_fonts(self) -> None:
        """
        Create the fonts necessary for the dialog.
        ...

        Parameter
        ---------
        None

        Returns
        -------
        None
        """

        self._title_font = QFont("Calibri", 12, QFont.Bold)
        self._font = QFont("Calibri", 12)

    def _create_line(self) -> None:
        """
        Create a horizontal line.
        ...

        Parameter
        ---------
        None

        Returns
        -------
        None
        """

        self._line = QFrame()
        self._line.setFrameShape(QFrame.HLine)
        self._line.setFrameShadow(QFrame.Sunken)

    def _create_spacers(self) -> None:
        """
        Create a create_spacers.
        ...

        Parameter
        ---------
        None

        Returns
        -------
        None
        """

        self._spacer_1 = QSpacerItem(5, 1)
        self._spacer_2 = QSpacerItem(5, 5)
        self._spacer_3 = QSpacerItem(5, 5)
