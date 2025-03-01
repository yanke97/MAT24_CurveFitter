from pathlib import Path
from csv import Sniffer
from math import log, e
from string import Template

import pandas as pd
import numpy as np
from scipy.optimize import curve_fit

from cf_errors import FileError, ExportPointNoError, TemplateError, DataError


class LsDynaTemplate(Template):
    """
    Template class inheriting form strings Template.
    Delimiter is changed to prevent interference with 
    Ls-Dynas comment character.
    """
    delimiter = "$%"


def _hooks_straight(x, m) -> float:
    """
    Equation describing the hooks straight.
    """
    return m*x


def _swift_extrapolation(x, c, phi, n) -> float:
    """
    Equation describing the flow curve according to Swift.
    """
    return c*(phi+x)**n


def _voce_extrapolation(x, sigma, R, B) -> float:
    """
    Equation describing the flow curve according to Voce.
    """
    return sigma + R*(1-np.exp(-B*x))


def _swift_voce_extrapolation(x, alpha, c, phi, n, sigma, R, B) -> float:
    """
    Equation describing the flow curve as a combination of Swift and Voce.
    """
    return alpha*(c*(phi+x)**n) + (1-alpha)*(sigma + R*(1-np.exp(-B*x)))


def get_data_from_file(file_path: Path) -> pd.DataFrame:
    """
    Read data from given .csv-file and store it in a dataframe.
    ...

    Parameter
    ---------
    file_path: Path
        path to the .csv-file

    Returns
    -------
    _: DataFrame
        dataframe containing the data from the .csv-file.
    """

    if file_path.is_file() is True:
        header, delimiter = _get_csv_info(file_path)

        if header is True:
            df = pd.read_csv(file_path, delimiter=delimiter,
                             header=0)
        else:
            df = pd.read_csv(file_path, delimiter=delimiter,
                             header=None)

        if df.shape[1] != 2:
            raise DataError(df.shape[1]) from None
        else:
            df = df.set_axis(["eng_strain", "eng_stress"],
                             axis="columns", copy=False)

            df["eng_strain"] = df["eng_strain"] - df["eng_strain"][0]
            df["eng_stress"] = df["eng_stress"] - df["eng_stress"][0]

            return df
    else:
        raise FileError(file_path) from None


def _get_csv_info(file_path: Path) -> tuple[bool, str]:
    """
    Collects information about the given .csv-file regarding existance of a
    header and the delimiter character.
    ...

    Parameter
    ---------
    file_path: Path
        path to the .csv-file

    Returns
    -------
    _: tuple[bool, str]
        bool to describe the existance of a header (True == yes)
        str to return the delimiter
    """
    with open(file_path, 'r') as f:
        # Sniffer analyzes the first few lines
        sniffer = Sniffer()
        sample = f.read(1024)  # Read a sample from the file
        return sniffer.has_header(sample), sniffer.sniff(sample).delimiter


def comp_true_stress_strain(df: pd.DataFrame, rp02_i: int, rm_i: int) -> pd.DataFrame:
    """
    Computes the true stress - true strain curve of the given data.
    ...

    Parameter
    ---------
    df: DataFrame
        dataframe containing the data
    rp02_i: int
        index of the datapoint for rp02
    rm_i: int
        index of the datapoint for rm

    Returns
    -------
    _: DataFrame
        dataframe containing the user_input data plus 
        data of the true stress - true strain curve.
    """

    df["strain"] = np.log(1+(df["eng_strain"][0:rm_i])
                          )             # strain [-]
    df["stress"] = df["eng_stress"][0:rm_i] * \
        np.exp(df["strain"][0:rm_i]
               )                                # stress [MPa]

    df["plst_strain"] = df["strain"].loc[rp02_i:] - df["strain"][rp02_i]
    df["plst_stress"] = df["stress"].loc[rp02_i:]

    return df


def comp_material_data(df: pd.DataFrame, e_start: int, e_end: int) -> list[float | int]:
    """
    Computing different material characteristics.

    Parameter
    ---------
    df: DataFrame
        dataframe containing the data
    e_start: int
        index of the first data point used for computation of youngs modulus
    e_end: int
        index of the last data point used for computation of youngs modulus

    Returns
    -------
    _: list[float|int]
        list containing the material charateristics
        0 = youngs modulus [float]
        1 = Rp_02 [float]
        2 = Rm [float]
        3 = index of Rp_02 [int]
        4 = index of Rm [int]
        5 = uniform strain [float]
        6 = failure strain [float]
    """

    # compute youngs modulus
    res = curve_fit(_hooks_straight,
                    df["eng_strain"][e_start:e_end], df["eng_stress"][e_start:e_end])
    E = res[0][0]

    # compute Rp_02
    # Compute difference between measurement data and hooks straight
    difference = df["eng_stress"] - (df["eng_strain"]-0.002)*E

    rp02_i = np.abs(difference).argmin()
    # Rp_0.2 of the material
    rp02 = df["eng_stress"][rp02_i]

    # Compute Failure strain A_5
    if df["eng_stress"].iloc[-1] > 50:
        a5_i = df["eng_strain"].index[-1]

    else:
        # Compute pandas series with stress drops
        stress_drop = pd.Series(df["eng_stress"].diff())
        a5_i = stress_drop.idxmin()-1

    # Compute failure strain
    af = (df["eng_strain"][a5_i]) - (df["eng_stress"][a5_i]/E)

    # Rm of the material
    rm_i = df["eng_stress"].idxmax()
    rm = df["eng_stress"][rm_i]

    # Unifrom strain
    ag = (df["eng_strain"][rm_i]) - (rm/E)

    return [E, rp02, rm, rp02_i, rm_i, ag, af]


def extrapolate(data: list, extrap_type: int, end: int = 1,
                resolution: int = 100) -> list[pd.Series | list[float]]:
    """
    Fit and extrapolate curve with selected fitting type.
    ...

    Parameter
    ---------
    data: list
        list containg necessary user_input data
        0 = dataframe with data to be fitted
        1 = index of start point for data fitting (index of Rp_02)
        2 = index of end point for data fitting (index of Rm)
    extrap_type: int
        integer indicating the selected fitting type
        0 = Swift
        1 = Voce
        2 = Swift-Voce
    end: int, default = 1 (=100%)
        integer indicating upto what strain the curve shall be extraploated 
    resolution: int, default = 100
        integer indicating the number of datapoints to be returned

    Returns
    -------
    _: Series
        list of series containing fitting results and parameter
        0 = strain values [Series]
        1 = stress values [Series]
        2 = parameter [list[float]]

    """

    df = data[0]
    start_index = data[1]
    end_index = data[2]

    if end == 1:
        extrap_strain = pd.Series(np.linspace(0, end, resolution+1))
    else:
        extrap_strain = pd.Series(
            np.linspace(0, df["plst_strain"][end-1], resolution))

    if extrap_type == 0:
        # Swift extrapolation
        ag = data[3]
        rm = data[4]

        n_0 = log(ag+1)
        c_0 = rm*(e/n_0)**n_0
        phi_0 = 0.1

        initial_guess = [c_0, phi_0, n_0]

        res = curve_fit(_swift_extrapolation, df["plst_strain"][start_index:end_index],
                        df["plst_stress"][start_index:end_index], initial_guess)

        parameter = res[0]

        extrap_stress = _swift_extrapolation(
            extrap_strain, parameter[0], parameter[1], parameter[2])

    elif extrap_type == 1:
        # Voce
        sigma_0 = df["plst_stress"][start_index]
        R_0 = df["plst_stress"].max()-sigma_0

        eps_50 = df["plst_strain"][abs(
            df["plst_stress"]-(sigma_0+0.5*R_0)).argmin()]
        B_0 = 1/eps_50

        initial_guess = [sigma_0, R_0, B_0]

        res = curve_fit(_voce_extrapolation, df["plst_strain"][start_index:end_index],
                        df["plst_stress"][start_index:end_index], initial_guess)

        parameter = res[0]

        extrap_stress = _voce_extrapolation(
            extrap_strain, parameter[0], parameter[1], parameter[2])

    elif extrap_type == 2:
        # Combined Swift Voce

        # Get swift and Voce curves with respective parameter
        _, swift_stress, swift_parameter = extrapolate(
            data, 0, end_index, end_index-start_index)
        _, voce_stress, voce_parameter = extrapolate(
            data, 1, end_index, end_index-start_index)

        # The numerator quantifies how well the difference between the Swift and Voce models
        # (Swift - Voce) aligns with the residuals of the Voce model (measured - Voce).
        # A larger numerator indicates that the Swift model improves upon the Voce model
        # in regions where the Voce model deviates from the measured data.
        numerator = np.sum((df["plst_stress"][start_index:end_index].values-voce_stress.values)
                           * (swift_stress-voce_stress))

        # The denominator represents the magnitude of the difference between the Swift
        # and Voce models (Swift - Voce) across the overlapping region. It normalizes
        # the calculation of the weighing factor (alpha) to ensure that the weighting
        # accounts for how distinct the two models are from each other.
        denominator = np.sum((swift_stress-voce_stress)**2)

        if denominator < 0.0001:
            alpha = 0.5
        elif abs(numerator)/denominator > 10:
            alpha = 0.5
        else:
            alpha = np.clip(abs(numerator)/denominator, 0, 1)

        parameter = [alpha]
        parameter.extend(swift_parameter)
        parameter.extend(voce_parameter)

        extrap_stress = _swift_voce_extrapolation(
            extrap_strain, parameter[0], parameter[1], parameter[2], parameter[3],
            parameter[4], parameter[5], parameter[6])

    result = [extrap_strain, extrap_stress, parameter]
    return result


def export_data(user_input: list[str], fitted_data: list[list], E: float, path_str: str,
                template_path_str: str) -> Path:
    """
    Prepate fitted and extrapolated data for export to .k-file.
    ...

    Parameter
    ---------
    user_input: list[str]
        list containing user input data from export dialog.
        0 = material title
        1 = material id
        2 = rho
        3 = posions ratio
        4 = failure strain
        5 = number of datapoints to be exported
        6 = path to export to
        7 = spacing type ("equi" or "uneven")
    fitted_data: list[list]
        list containg list with the data to be exported
        0 = strain data
        1 = stress data
    E: float
        the youngs modulus computed
    path_str: str
        string indicating the path to which the file shall be exported
    template_path_str: str
        string pointing to the template path

    Returns:
    _: Path
        path to which the file was saved.
    """

    if int(user_input[5]) > 100 or int(user_input[5]) < 2:
        raise ExportPointNoError from None
    else:
        export_data: dict = {}
        export_data["Title"] = user_input[0]
        export_data["mid"] = user_input[1].rjust(10)
        export_data["ro"] = user_input[2].rjust(10)
        export_data["E"] = str(round(E, 2)).rjust(10)
        export_data["pr"] = user_input[3].rjust(10)
        export_data["fail"] = user_input[4].rjust(10)

        if user_input[7] == "equi" or user_input[5] == 100:
            ids = np.linspace(0, 100, int(user_input[5])+1)

        else:
            point_no_1 = round(int(user_input[5])*0.6)
            point_no_2 = int(user_input[5]) - point_no_1

            ids_1 = np.linspace(0, 50, point_no_1)
            ids_1 = np.round(ids_1).astype(int)
            ids = set(ids_1)

            ids_2 = np.linspace(51, 100, point_no_2)
            ids_2 = np.round(ids_2).astype(int)

            ids.update(ids_2)

        for j, i in enumerate(ids):
            key_a = f"a{j}"
            key_o = f"o{j}"

            export_data[key_a] = str(round(fitted_data[0][i], 3)).rjust(20)
            export_data[key_o] = str(round(fitted_data[1][i], 3)).rjust(20)

        j += 1

        while j <= 101:
            key_a = f"a{j}"
            key_o = f"o{j}"

            export_data[key_a] = "$"
            export_data[key_o] = "$"

            j += 1

        path: Path = write_to_file(export_data, path_str, template_path_str)

        return path


def write_to_file(data: dict[str, str], path_str: str, template_path_str: str) -> None:
    """
    Write data to be exported to file.
    ...

    Parameter
    ---------
    data: dict[str:str]
        containg the data to be exported.
    path_str: str
        string indicating the path to which the file shall be exported
    template_path_str: str
        string pointing to the template path

    Returns
    -------
    None

    Raises
    ------
    FileError
    TemplateError

    """
    template_path = Path(template_path_str)
    path: Path = Path(path_str.replace("\"", ""))

    if template_path.is_file() and template_path.suffix == ".k":

        if path.is_file():

            with open(template_path, "r") as template, open(path, "w") as file:
                mat_card_content: str = LsDynaTemplate(
                    template.read()).substitute(data)

                file.writelines(mat_card_content)

        else:
            raise FileError(path) from None

    else:
        raise TemplateError(template_path) from None
