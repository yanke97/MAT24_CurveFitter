from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QSizePolicy, QGridLayout, QLineEdit, QMenu,
                             QFileDialog, QStatusBar, QToolBar, QAction, QMenuBar)

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
        self._create_actns()
        self._create_status_bar()
        self._create_tool_bar()
        self._create_menu_bar()

        self._central_widget = QWidget()
        self._central_widget.setLayout(self._main_layout)
        self.setCentralWidget(self._central_widget)

        self._layout_graphs.addWidget(self.graph_input, 0, 0, 2, 1)
        self._layout_graphs.addWidget(self.graph_output_1, 0, 1)
        self._layout_graphs.addWidget(self.graph_output_2, 1, 1)

        self._tool_bar.addAction(self.import_action)
        self._tool_bar.addAction(self.fit_action)
        self._tool_bar.addAction(self.export_action)

        self._file_menu.addAction(self.settings_action)
        self._file_menu.addSeparator()
        self._file_menu.addAction(self.exit_action)

    def _create_layouts(self) -> None:
        self._main_layout = QVBoxLayout()
        self._layout_graphs = QGridLayout()
        self._layout_btns = QHBoxLayout()

        self._main_layout.addLayout(self._layout_btns)
        self._main_layout.addLayout(self._layout_graphs)

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
        self.axes_input.set_title("Stress - Strain (eng.)")
        self.axes_input.grid(True)

        self.graph_output_1 = FigureCanvas(plt.figure())
        self.graph_output_1.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.axes_output_1 = self.graph_output_1.figure.subplots()
        self.axes_output_1.set_title("True Stress - True Strain")
        self.axes_output_1.grid(True)

        self.graph_output_2 = FigureCanvas(plt.figure())
        self.graph_output_2.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.axes_output_2 = self.graph_output_2.figure.subplots()
        self.axes_output_2.set_title("Yield Curve")
        self.axes_output_2.grid(True)

    def _create_tbs(self) -> None:
        self.tb_in_path = QLineEdit()
        self.tb_in_path.setBaseSize(175, 25)
        self.tb_in_path.setFont(self._font)
        self.tb_in_path.setPlaceholderText("Enter path to input .csv-file")

        self.tb_out_path = QLineEdit()
        self.tb_out_path.setBaseSize(175, 25)
        self.tb_out_path.setFont(self._font)
        self.tb_out_path.setPlaceholderText("Enter path to output .k-file")

    def _create_actns(self) -> None:
        self.import_action = QAction("Import .csv-file")
        self.import_action.setFont(self._font)
        self.import_action.setIcon(
            QIcon(r"e:\15_MAT24_Curve fitter\00_Daten\file-import.png"))

        self.fit_action = QAction("Fit and Extrapolate Curve")
        self.fit_action.setFont(self._font)
        self.fit_action.setIcon(
            QIcon(r"E:\15_MAT24_Curve fitter\00_Daten\graph-curve.png"))

        self.export_action = QAction("Export to .k-file")
        self.export_action.setFont(self._font)
        self.export_action.setIcon(
            QIcon(r"E:\15_MAT24_Curve fitter\00_Daten\file-export.png"))

        self.settings_action = QAction("Settings...")
        self.exit_action = QAction("Exit")

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

    def _create_tool_bar(self) -> None:
        self._tool_bar = QToolBar()
        self.addToolBar(self._tool_bar)

    def _create_menu_bar(self) -> None:
        self._menu_bar = QMenuBar()
        self.setMenuBar(self._menu_bar)
        self._file_menu = QMenu("&File", self)
        self._menu_bar.addMenu(self._file_menu)

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

    def plot_data(self, data, graph: str, line_type="-", name: str = "") -> None:
        if type(data) == pd.DataFrame and graph == "input":
            self.axes_input.plot(data["eng_strain"],
                                 data["eng_stress"], line_type)
            self.axes_input.set_xlim(0)
            self.axes_input.set_ylim(0)
            self.graph_input.draw_idle()

        elif type(data) == pd.DataFrame and graph == "output_1":
            self.axes_output_1.plot(
                data["strain"], data["stress"], line_type, label=name)
            self.axes_output_1.set_xlim(0)
            self.axes_output_1.set_ylim(0)
            self.axes_output_1.legend()
            self.graph_output_1.draw_idle()

        elif type(data) == list and graph == "output_1":
            self.axes_output_1.plot(data[0], data[1], line_type, label=name)
            self.axes_output_1.legend()
            self.graph_output_1.draw_idle()

        elif type(data) == list and graph == "output_2":
            self.axes_output_2.plot(data[0], data[1], line_type, label=name)
            self.axes_output_2.set_xlim(0, 1.2)
            self.axes_output_2.set_ylim(0, (data[1].max())*1.2)
            self.axes_output_2.legend()
            self.graph_output_2.draw_idle()

    def clear_graphs(self, graph: str) -> None:
        if graph == "input":
            self.axes_input.cla()
            self.axes_input.grid(True)
            self.axes_input.set_title("Stress - Strain (eng.)")
        if graph == "output_1":
            self.axes_output_1.cla()
            self.axes_output_1.grid(True)
            self.axes_output_1.set_title("True Stress - True Strain")
        if graph == "output_2":
            self.axes_output_2.cla()
            self.axes_output_2.grid(True)
            self.axes_output_2.set_title("Yield Curve")
