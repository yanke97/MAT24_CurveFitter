from PyQt5.QtWidgets import (QDialog, QPushButton, QDialogButtonBox, QLineEdit,
                             QLabel, QFormLayout, QSpacerItem, QRadioButton, QSizePolicy)
from PyQt5.QtGui import (QFont, QIcon)
from PyQt5.QtCore import Qt


class ExportDialog(QDialog):
    def __init__(self, failure_strain=None, parent=None, ):
        super().__init__(parent)

        self.setWindowTitle("Export")
        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        self._create_fonts()
        self._create_btns()
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

    def _create_btns(self) -> None:
        btns = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.btnbx = QDialogButtonBox(btns)

        self.btn_file_out = QPushButton()
        self.btn_file_out.setBaseSize(25, 25)
        self.btn_file_out.setIcon(
            QIcon(r"e:\15_MAT24_Curve fitter\00_Daten\open-folder.png"))

    def _create_lbls(self) -> None:
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

    def _create_tbs(self, failure_strain) -> None:
        self.tb_title = QLineEdit("Tet")
        self.tb_title.setFont(self._font)
        self.tb_mid = QLineEdit("20000000")
        self.tb_mid.setFont(self._font)
        self.tb_rho = QLineEdit("7.89e-9")
        self.tb_rho.setFont(self._font)
        self.tb_poisons_ratio = QLineEdit("0.3")
        self.tb_poisons_ratio.setFont(self._font)
        self.tb_fail = QLineEdit(f"{failure_strain}")
        self.tb_fail.setFont(self._font)

        self.tb_point_no = QLineEdit("50")
        self.tb_point_no.setFont(self._font)
        self.tb_point_no.setFixedSize(100, 25)

        self.tb_out_path = QLineEdit()
        self.tb_out_path.setBaseSize(100, 25)
        self.tb_out_path.setFont(self._font)
        self.tb_out_path.setPlaceholderText("Enter path to output .k-file")
        # self.tb_out_path.setAlignment(Qt.AlignRight)

    def _create_rdbtn(self) -> None:
        self.rdbtn_equi = QRadioButton("Equidistant Spacing")
        self.rdbtn_equi.setFont(self._font)

        self.rdbtn_uneven = QRadioButton("Uneven Sapcing")
        self.rdbtn_uneven.setChecked(True)
        self.rdbtn_uneven.setFont(self._font)

    def _create_fonts(self) -> None:
        self._titel_font = QFont("Calibri", 12, QFont.Bold)
        self._font = QFont("Calibri", 12)
