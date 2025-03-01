from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QMainWindow, QWidget, QFrame,
                             QSizePolicy, QGridLayout, QLineEdit, QMenu,
                             QFileDialog, QStatusBar, QToolBar, QAction, QMenuBar, QLabel)

from PyQt5.QtGui import (QFont, QIcon)
from PyQt5.QtCore import Qt

from pathlib import Path
import pandas as pd


class CFAppGui(QMainWindow):

    def __init__(self, cwd: Path) -> None:
        """
        Gui init method
        """

        super().__init__()

        self.setWindowTitle("*MAT_024 Curve Fitter")
        self.resize(1160, 700)

        self._create_layouts()
        self._create_line()
        self._create_graphs()
        self._create_fonts()
        self._create_lbls()
        self._create_tbs()
        self._create_actns(cwd)
        self._create_status_bar()
        self._create_tool_bar()
        self._create_menu_bar()

        self._central_widget = QWidget()
        self._central_widget.setLayout(self._main_layout)
        self.setCentralWidget(self._central_widget)

        self._main_layout.addWidget(self.graph_input, 0, 0, 2, 1)
        self._main_layout.addWidget(self.graph_output, 0, 1)
        self._layout_data.addWidget(
            self._lbl_chars, 0, 0, 1, 2, alignment=Qt.AlignCenter)
        self._layout_data.addWidget(self._lbl_char1, 2, 0)
        self._layout_data.addWidget(self._lbl_char2, 3, 0)
        self._layout_data.addWidget(self._lbl_char3, 4, 0)
        self._layout_data.addWidget(self._lbl_char_data1, 2, 1)
        self._layout_data.addWidget(self._lbl_char_data2, 3, 1)
        self._layout_data.addWidget(self._lbl_char_data3, 4, 1)

        self._layout_data.addWidget(self._v_line, 0, 2, 9, 1)
        self._layout_data.addWidget(self._h_line, 1, 0, 1, 5)

        self._layout_data.addWidget(
            self._lbl_paras, 0, 3, 1, 2, alignment=Qt.AlignCenter)
        self._layout_data.addWidget(self._lbl_para1, 2, 3)
        self._layout_data.addWidget(self._lbl_para2, 3, 3)
        self._layout_data.addWidget(self._lbl_para3, 4, 3)
        self._layout_data.addWidget(self._lbl_para4, 5, 3)
        self._layout_data.addWidget(self._lbl_para5, 6, 3)
        self._layout_data.addWidget(self._lbl_para6, 7, 3)
        self._layout_data.addWidget(self._lbl_para7, 8, 3)
        self._layout_data.addWidget(self._lbl_para_data1, 2, 4)
        self._layout_data.addWidget(self._lbl_para_data2, 3, 4)
        self._layout_data.addWidget(self._lbl_para_data3, 4, 4)
        self._layout_data.addWidget(self._lbl_para_data4, 5, 4)
        self._layout_data.addWidget(self._lbl_para_data5, 6, 4)
        self._layout_data.addWidget(self._lbl_para_data6, 7, 4)
        self._layout_data.addWidget(self._lbl_para_data7, 8, 4)

        self._tool_bar.addAction(self.import_action)
        self._tool_bar.addAction(self.fit_action)
        self._tool_bar.addAction(self.export_action)

        self._file_menu.addAction(self.settings_action)
        self._file_menu.addSeparator()
        self._file_menu.addAction(self.exit_action)

    def _create_layouts(self) -> None:
        """
        Create layouts for the GUI.
        ...

        Parameter
        ---------
        None

        Returns
        -------
        None
        """
        self._main_layout = QGridLayout()
        self._layout_data = QGridLayout()

        self._main_layout.addLayout(self._layout_data, 1, 1)

    def _create_line(self) -> None:
        """
        Create a vertical line.
        ...

        Parameter
        ---------
        None

        Returns
        -------
        None
        """
        self._v_line = QFrame()
        self._v_line.setFrameShape(QFrame.VLine)

        self._h_line = QFrame()
        self._h_line.setFrameShape(QFrame.HLine)

    def _create_graphs(self) -> None:
        """
        Create graphs.
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

        self.graph_output = FigureCanvas(plt.figure())
        self.graph_output.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.axes_output = self.graph_output.figure.subplots()
        self.axes_output.set_title("Yield Curve")
        self.axes_output.grid(True)

    def _create_tbs(self) -> None:
        """
        Create textboxes for the GUI.
        ...

        Parameter
        ---------
        None

        Returns
        -------
        None
        """
        self.tb_in_path = QLineEdit()
        self.tb_in_path.setBaseSize(175, 25)
        self.tb_in_path.setFont(self._font)
        self.tb_in_path.setPlaceholderText("Enter path to input .csv-file")

        self.tb_out_path = QLineEdit()
        self.tb_out_path.setBaseSize(175, 25)
        self.tb_out_path.setFont(self._font)
        self.tb_out_path.setPlaceholderText("Enter path to output .k-file")

    def _create_lbls(self) -> None:
        """
        Create textboxes for the GUI.
        ...

        Parameter
        ---------
        None

        Returns
        -------
        None
        """
        self._lbl_chars = QLabel("Material Characteristics")
        self._lbl_chars.setFont(self._titel_font)

        self._lbl_char1 = QLabel("Youngs Modulus")
        self._lbl_char1.setFont(self._font)
        self._lbl_char2 = QLabel("Yield Stress")
        self._lbl_char2.setFont(self._font)
        self._lbl_char3 = QLabel("Tensile Strength")
        self._lbl_char3.setFont(self._font)
        self._lbl_char_data1 = QLabel()
        self._lbl_char_data1.setFont(self._font)
        self._lbl_char_data2 = QLabel()
        self._lbl_char_data2.setFont(self._font)
        self._lbl_char_data3 = QLabel()
        self._lbl_char_data3.setFont(self._font)

        self._lbl_paras = QLabel("Fitted Parameters")
        self._lbl_paras.setFont(self._titel_font)
        self._lbl_para1 = QLabel()
        self._lbl_para1.setFont(self._font)
        self._lbl_para2 = QLabel()
        self._lbl_para2.setFont(self._font)
        self._lbl_para3 = QLabel()
        self._lbl_para3.setFont(self._font)
        self._lbl_para4 = QLabel()
        self._lbl_para4.setFont(self._font)
        self._lbl_para5 = QLabel()
        self._lbl_para5.setFont(self._font)
        self._lbl_para6 = QLabel()
        self._lbl_para6.setFont(self._font)
        self._lbl_para7 = QLabel()
        self._lbl_para7.setFont(self._font)
        self._lbl_para_data1 = QLabel()
        self._lbl_para_data1.setFont(self._font)
        self._lbl_para_data2 = QLabel()
        self._lbl_para_data2.setFont(self._font)
        self._lbl_para_data3 = QLabel()
        self._lbl_para_data3.setFont(self._font)
        self._lbl_para_data4 = QLabel()
        self._lbl_para_data4.setFont(self._font)
        self._lbl_para_data5 = QLabel()
        self._lbl_para_data5.setFont(self._font)
        self._lbl_para_data6 = QLabel()
        self._lbl_para_data6.setFont(self._font)
        self._lbl_para_data7 = QLabel()
        self._lbl_para_data7.setFont(self._font)

    def _create_actns(self, cwd: Path) -> None:
        """
        Create actions for the GUI.
        ...

        Parameter
        ---------
        None

        Returns
        -------
        None
        """

        self.import_action = QAction("Import .csv-file")
        self.import_action.setFont(self._font)
        self.import_action.setIcon(
            QIcon(str(cwd/"data"/"file-import.png")))

        self.fit_action = QAction("Fit and Extrapolate Curve")
        self.fit_action.setFont(self._font)
        self.fit_action.setIcon(
            QIcon(str(cwd/"data"/"graph-curve.png")))

        self.export_action = QAction("Export to .k-file")
        self.export_action.setFont(self._font)
        self.export_action.setIcon(
            QIcon(str(cwd/"data"/"file-export.png")))

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
        self._titel_font = QFont("Calibri", 12, QFont.Bold)
        self._font = QFont("Calibri", 12)

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
        """
        Create the tool bar for the GUI.
        ...

        Parameter
        ---------
        None

        Returns
        -------
        None
        """

        self._tool_bar = QToolBar()
        self.addToolBar(self._tool_bar)

    def _create_menu_bar(self) -> None:
        """
        Create the menu bar for the GUI.
        ...

        Parameter
        ---------
        None

        Returns
        -------
        None
        """
        self._menu_bar = QMenuBar()
        self.setMenuBar(self._menu_bar)
        self._file_menu = QMenu("&File", self)
        self._menu_bar.addMenu(self._file_menu)

    def file_dialog(self, file_type: str) -> tuple:
        """
        Open file dialog window and return the path to selected folder.
        ...

        Parameter
        ---------
        file_type: str
            filetype necessary to preselect files.

        Return
        ------
        _: tuple
            a tuple containing the file path and file extension.
        """

        return QFileDialog.getOpenFileName(
            self, "Select file", "", file_type)

    def plot_data(self, data: pd.DataFrame | list, graph: str, line_type: str = "-", name: str = "") -> None:
        """
        Plot data to a graph.
        ...

        Parameter
        ---------
        data: Dataframe|list
            data to be plotted

        graph: str
           string specifiying to which graph ("input" or "output") the data shall be plotted

        line_type: str
            string specifiying the line type in which the data is plotted.

        name: str 
            text to be written in the curve label 

        Returns
        -------
        None
        """

        if type(data) == pd.DataFrame and graph == "input":
            self.axes_input.plot(data["eng_strain"],
                                 data["eng_stress"], line_type)
            self.axes_input.set_xlim(0)
            self.axes_input.set_ylim(0)
            self.graph_input.draw_idle()

        elif type(data) == list and graph == "output":
            self.axes_output.plot(data[0], data[1], line_type, label=name)
            self.axes_output.set_xlim(0, 1.2)
            self.axes_output.set_ylim(0, (data[1].max())*1.2)
            self.axes_output.legend()
            self.graph_output.draw_idle()

    def clear_graphs(self, graph: str) -> None:
        """
        Clear the graphs
        ...

        Parameter
        ---------
        None

        Returns
        -------
        None
        """

        if graph == "input":
            self.axes_input.cla()
            self.axes_input.grid(True)
            self.axes_input.set_title("Stress - Strain (eng.)")
        if graph == "output":
            self.axes_output.cla()
            self.axes_output.grid(True)
            self.axes_output.set_title("Yield Curve")

    def fill_lbls(self, mat_char: list[float], extrap_type: int, paras: list[float]) -> None:
        """
        Fill labels representing the fitted datas parameter and characteristics.
        ...

        Parameter
        ---------
        mat_char: list[float]
            list of material characteristics

        extrap_type: int
            etrapolation type represented by an integer

        paras: list[float]
            the parameter of the fitted curve

        Return
        ------
        None
        """

        self._lbl_char_data1.setText(f"{mat_char[0]:.2f}")
        self._lbl_char_data2.setText(f"{mat_char[1]:.2f}")
        self._lbl_char_data3.setText(f"{mat_char[2]:.2f}")

        if extrap_type == 0:
            self._lbl_para1.setText("c")
            self._lbl_para2.setText("phi")
            self._lbl_para3.setText("n")
            self._lbl_para4.setText("")
            self._lbl_para5.setText("")
            self._lbl_para6.setText("")
            self._lbl_para7.setText("")
            self._lbl_para_data1.setText(f"{paras[0]:.5f}")
            self._lbl_para_data2.setText(f"{paras[1]:.5f}")
            self._lbl_para_data3.setText(f"{paras[2]:.5f}")
            self._lbl_para_data4.setText("")
            self._lbl_para_data5.setText("")
            self._lbl_para_data6.setText("")
            self._lbl_para_data7.setText("")

        elif extrap_type == 1:
            self._lbl_para1.setText("sigma")
            self._lbl_para2.setText("R")
            self._lbl_para3.setText("B")
            self._lbl_para4.setText("")
            self._lbl_para5.setText("")
            self._lbl_para6.setText("")
            self._lbl_para7.setText("")
            self._lbl_para_data1.setText(f"{paras[0]:.5f}")
            self._lbl_para_data2.setText(f"{paras[1]:.5f}")
            self._lbl_para_data3.setText(f"{paras[2]:.5f}")
            self._lbl_para_data4.setText("")
            self._lbl_para_data5.setText("")
            self._lbl_para_data6.setText("")
            self._lbl_para_data7.setText("")

        elif extrap_type == 2:
            self._lbl_para1.setText("alpha")
            self._lbl_para2.setText("c")
            self._lbl_para3.setText("phi")
            self._lbl_para4.setText("n")
            self._lbl_para5.setText("sigma")
            self._lbl_para6.setText("R")
            self._lbl_para7.setText("B")
            self._lbl_para_data1.setText(f"{paras[0]:.2f}")
            self._lbl_para_data2.setText(f"{paras[1]:.5f}")
            self._lbl_para_data3.setText(f"{paras[2]:.5f}")
            self._lbl_para_data4.setText(f"{paras[3]:.5f}")
            self._lbl_para_data5.setText(f"{paras[4]:.5f}")
            self._lbl_para_data6.setText(f"{paras[5]:.5f}")
            self._lbl_para_data7.setText(f"{paras[6]:.5f}")
