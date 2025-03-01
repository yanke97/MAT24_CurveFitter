from pathlib import Path
from PyQt5.QtWidgets import (QDialog, QPushButton, QDialogButtonBox, QLineEdit,
                             QLabel, QFormLayout, QSpacerItem, QRadioButton, QSizePolicy)
from PyQt5.QtGui import (QFont, QIcon)


class ExportDialog(QDialog):
    """
    Dialog window to recieve user input for data export.
    """

    def __init__(self, cwd: Path, failure_strain: float, parent=None) -> None:
        """
        Export Dialogs init function.
        ...

        Parameter
        ---------
        cwd: Path
            path to current working directory
        failure strain: float
            failure strain of material.
        parent:_ default= None
            parent widget of the dialog.

        Return
        ------
        None
        """
        super().__init__(parent)

        self.setWindowTitle("Export")
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._create_fonts()
        self._create_btns(cwd)
        self._create_lbls()
        self._create_tbs(failure_strain)
        self._create_rdbtn()
        self._layout = QFormLayout()
        self._spacer = QSpacerItem(10, 20)
        self.setLayout(self._layout)

        self._layout.addRow(self._lbl_info)
        self._layout.addRow(self.btn_file_out, self.tb_out_path)
        self._layout.addRow(self._lbl_title, self.tb_title)
        self._layout.addRow(self._lbl_mid, self.tb_mid)
        self._layout.addRow(self._lbl_rho, self.tb_rho)
        self._layout.addRow(self._lbl_poisons_ratio, self.tb_poisons_ratio)
        self._layout.addRow(self._lbl_fail, self.tb_fail)
        self._layout.addItem(self._spacer)
        self._layout.addRow(self._lbl_point_no)
        self._layout.addRow(self.tb_point_no)
        self._layout.addRow(self.rdbtn_uneven)
        self._layout.addRow(self.rdbtn_equi)
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

        self.btn_file_out = QPushButton()
        self.btn_file_out.setBaseSize(25, 25)
        self.btn_file_out.setIcon(QIcon(str(cwd/"data"/"open-folder.png")))

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
        self._lbl_info = QLabel(
            "Additional information for material card:")
        self._lbl_info.setFont(self._titel_font)
        self._lbl_title = QLabel("Title")
        self._lbl_title.setFont(self._font)
        self._lbl_mid = QLabel("Material ID")
        self._lbl_mid.setFont(self._font)
        self._lbl_rho = QLabel("Density")
        self._lbl_rho.setFont(self._font)
        self._lbl_poisons_ratio = QLabel("Poisson’s Ratio")
        self._lbl_poisons_ratio.setFont(self._font)
        self._lbl_fail = QLabel("Failure Strain")
        self._lbl_fail.setFont(self._font)

        self._lbl_point_no = QLabel("No of datapoints to export:")
        self._lbl_point_no.setFont(self._font)

    def _create_tbs(self, failure_strain: int) -> None:
        """
        Create the textboxes necessary for the dialog.
        ...

        Parameter
        ---------
        failure_strain: int
            failure strain of the material

        Return
        ------
        None
        """
        self.tb_title = QLineEdit("Test")
        self.tb_title.setFont(self._font)
        self.tb_mid = QLineEdit("20000000")
        self.tb_mid.setFont(self._font)
        self.tb_rho = QLineEdit("7.89e-9")
        self.tb_rho.setFont(self._font)
        self.tb_poisons_ratio = QLineEdit("0.3")
        self.tb_poisons_ratio.setFont(self._font)
        self.tb_fail = QLineEdit(f"{failure_strain}")
        self.tb_fail.setFont(self._font)

        self.tb_point_no = QLineEdit("100")
        self.tb_point_no.setFont(self._font)
        self.tb_point_no.setFixedSize(100, 25)

        self.tb_out_path = QLineEdit()
        self.tb_out_path.setBaseSize(100, 25)
        self.tb_out_path.setFont(self._font)
        self.tb_out_path.setPlaceholderText("Enter path to output .k-file")

    def _create_rdbtn(self) -> None:
        """
        Create the radio buttons needed for the dialog.
        ...

        Parameter
        ---------
        None

        Return
        ------
        None
        """

        self.rdbtn_equi = QRadioButton("Equidistant Spacing")
        self.rdbtn_equi.setFont(self._font)

        self.rdbtn_uneven = QRadioButton("Uneven Sapcing")
        self.rdbtn_uneven.setChecked(True)
        self.rdbtn_uneven.setFont(self._font)

    def _create_fonts(self) -> None:
        """
        Create the dialogs fonts.
        ...

        Parameter
        ---------
        None

        Return
        ------
        None
        """

        self._titel_font = QFont("Calibri", 12, QFont.Bold)
        self._font = QFont("Calibri", 12)
