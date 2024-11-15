from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QSizePolicy, QGridLayout, QLineEdit, QPushButton,
                             QFileDialog, QStatusBar)

from PyQt5.QtGui import (QFont, QIcon)

from pathlib import Path
import pandas as pd


class CFAppGui(QMainWindow):

    def __init__(self) -> None:
        """
        Gui init method
        """

        super().__init__()

        self.setWindowTitle("*MAT_024 Curve Fitter")
        self.resize(1160, 700)

        self._create_layouts()
        self._create_graphs()
        self._create_fonts()
        self._create_tbs()
        self._create_btns()
        self._create_status_bar()

        self._central_widget = QWidget()
        self._central_widget.setLayout(self._main_layout)
        self.setCentralWidget(self._central_widget)

        self._input_layout.addWidget(self.graph_input, 1, 0, 1, 2)
        self._input_layout.addWidget(self.tb_in_path, 0, 1)
        self._input_layout.addWidget(self.btn_file_in, 0, 0)

        self._output_layout.addWidget(self.graph_output, 1, 0, 1, 2)
        self._output_layout.addWidget(self.tb_out_path, 0, 1)
        self._output_layout.addWidget(self.btn_file_out, 0, 0)

        self._processing_layout.addWidget(self.btn_fit, 0, 0)

    def _create_layouts(self) -> None:
        self._main_layout = QHBoxLayout()
        self._input_layout = QGridLayout()
        self._processing_layout = QGridLayout()
        self._output_layout = QGridLayout()

        self._main_layout.addLayout(self._input_layout)
        self._main_layout.addLayout(self._processing_layout)
        self._main_layout.addLayout(self._output_layout)

    def _create_graphs(self) -> None:
        """
        Create graph
        ...

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.graph_input = FigureCanvas(plt.figure())
        self.graph_input.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.axes_input = self.graph_input.figure.subplots()
        self.axes_input.set_title("Curve from file")
        self.axes_input.grid(True)

        self.graph_output = FigureCanvas(plt.figure())
        self.graph_output.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.axes_output = self.graph_output.figure.subplots()
        self.axes_output.set_title("Curve to file")
        self.axes_output.grid(True)

    def _create_tbs(self) -> None:
        self.tb_in_path = QLineEdit()
        self.tb_in_path.setBaseSize(175, 25)
        self.tb_in_path.setFont(self._font)
        self.tb_in_path.setPlaceholderText("Enter path to input .csv-file")

        self.tb_out_path = QLineEdit()
        self.tb_out_path.setBaseSize(175, 25)
        self.tb_out_path.setFont(self._font)
        self.tb_out_path.setPlaceholderText("Enter path to output .k-file")

    def _create_btns(self) -> None:
        self.btn_file_in = QPushButton()
        self.btn_file_in.setBaseSize(25, 25)
        self.btn_file_in.setIcon(
            QIcon(r"e:\15_MAT24_Curve fitter\00_Daten\open-folder.png"))

        self.btn_file_out = QPushButton()
        self.btn_file_out.setBaseSize(25, 25)
        self.btn_file_out.setIcon(
            QIcon(r"e:\15_MAT24_Curve fitter\00_Daten\open-folder.png"))

        self._font = QFont()
        self._font.setFamily("Calibri")
        self._font.setPointSize(12)

        self.btn_fit = QPushButton("Fit and Extrap")
        self.btn_fit.setBaseSize(175, 25)
        self.btn_fit.setFont(self._font)

    def _create_fonts(self) -> None:
        """
        Create the fonts used in the GUI
        ...

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        self._font_desc = QFont()
        self._font_desc.setFamily("Calibir Light")
        self._font_desc.setPointSize(12)
        self._font_desc.setBold(True)

        self._font = QFont()
        self._font.setFamily("Calibri")
        self._font.setPointSize(12)

    def _create_status_bar(self) -> None:
        """
        Create the Status Bar of the GUI
        ...

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        status = QStatusBar()

        self.setStatusBar(status)

    def file_dialog(self, file_type: str) -> tuple:
        """
        Open file dialog window and return the path to selected folder.

        Parameter
        ---------
        None

        Return
        ------
        path: Path
            path pointing to the folder where the banking data is stored

        """
        return QFileDialog.getOpenFileName(
            self, "Select file", "", file_type)

    def plot_data(self, data, plot: str, line_type="-", name: str = "") -> None:
        if type(data) == pd.DataFrame and plot == "input":
            self.axes_input.plot(data["eng_strain"], data["eng_stress"], line_type)
            self.axes_input.set_xlim(0)
            self.axes_input.set_ylim(0)
            self.axes_input.set_xlabel("Eng. strain")
            self.axes_input.set_ylabel("Eng. stress")
            self.graph_input.draw_idle()

        elif type(data) == pd.DataFrame and plot == "output":
            self.axes_output.plot(data["strain"], data["stress"], line_type, label=name)
            self.axes_output.set_xlim(0)
            self.axes_output.set_ylim(0)
            self.axes_output.set_xlabel("strain")
            self.axes_output.set_ylabel("stress")
            self.axes_output.legend()
            self.graph_output.draw_idle()

        elif type(data) == list and plot == "output":
            self.axes_output.plot(data[0], data[1], line_type, label=name)
            self.axes_output.legend()
            self.graph_output.draw_idle()
