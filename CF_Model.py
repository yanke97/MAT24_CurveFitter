import pandas as pd
from pathlib import Path
from csv import Sniffer
import numpy as np
from math import log, e
from scipy.optimize import curve_fit
from string import Template

from CF_Errors import FileError, ExportPointNoError, TemplateError


class LsDynaTemplate(Template):
    """
    Template class inheriting form strings Template.
    Delimiter is changed to prevent interference with 
    Ls-Dynas comment character.
    """
    delimiter = "$%"


def _hooks_straight(x, m) -> float:
    return m*x


def _swift_extrapolation(x, c, phi, n) -> float:
    return c*(phi+x)**n


def _voce_extrapolation(x, sigma, R, B) -> float:
    return sigma + R*(1-np.exp(-B*x))


def _swift_voce_extrapolation(x, alpha, c, phi, n, sigma, R, B) -> float:
    return alpha*(c*(phi+x)**n) + (1-alpha)*(sigma + R*(1-np.exp(-B*x)))


def get_data_from_file(file_path: Path) -> pd.DataFrame:
    if file_path.is_file() is True:
        header, delimiter = _get_csv_info(file_path)
        col_names = ["eng_strain", "eng_stress"]

        if header is True:
            df = pd.read_csv(file_path, delimiter=delimiter,
                             header=0, names=col_names)
        else:
            df = pd.read_csv(file_path, delimiter=delimiter,
                             header=None, names=col_names)

        df["eng_strain"] = df["eng_strain"] - df["eng_strain"][0]
        df["eng_stress"] = df["eng_stress"] - df["eng_stress"][0]

        return df
    else:
        raise FileError(file_path) from None


def _get_csv_info(file_path: Path) -> tuple[bool, str]:
    with open(file_path, 'r') as f:
        # Sniffer analyzes the first few lines
        sniffer = Sniffer()
        sample = f.read(1024)  # Read a sample from the file
        return sniffer.has_header(sample), sniffer.sniff(sample).delimiter


def comp_true_stress_strain(df: pd.DataFrame, Rp_02_I: int, Rm_I: int) -> pd.DataFrame:
    df["strain"] = np.log(1+(df["eng_strain"][0:Rm_I]))           # strain [-]
    df["stress"] = df["eng_stress"][0:Rm_I] * \
        np.exp(df["strain"][0:Rm_I])     # stress [MPa]

    df["plst_strain"] = df["strain"].loc[Rp_02_I:] - df["strain"][Rp_02_I]
    df["plst_stress"] = df["stress"].loc[Rp_02_I:]

    return df


def comp_material_data(df: pd.DataFrame, e_start: int, e_end: int) -> list[float]:
    # compute youngs modulus
    res = curve_fit(_hooks_straight,
                    df["eng_strain"][e_start:e_end], df["eng_stress"][e_start:e_end])
    E = res[0][0]

    # compute Rp_02
    # Compute difference between measurement data and hooks straight
    difference = df["eng_stress"] - (df["eng_strain"]-0.002)*E

    Rp_02_I = np.abs(difference).argmin()
    # Rp_0.2 of the material
    Rp_02 = df["eng_stress"][Rp_02_I]

    # Compute Failure strain A_5
    if df["eng_stress"].iloc[-1] > 50:
        A_5_I = df["eng_strain"].index[-1]

    else:
        # Compute pandas series with stress drops
        stress_drop = pd.Series(df["eng_stress"].diff())
        A_5_I = stress_drop.idxmin()-1

    Af = (df["eng_strain"][A_5_I]) - (df["eng_stress"][A_5_I]/E)

    # Rm of the material
    Rm_I = df["eng_stress"].idxmax()
    Rm = df["eng_stress"][Rm_I]
    Ag = (df["eng_strain"][Rm_I]) - (Rm/E)

    return [E, Rp_02, Rm, Rp_02_I, Rm_I, Ag, Af]


def extrapolate(data: list, extrap_type: int, end: int = 1, resolution: int = 100) -> list:
    df = data[0]
    start_index = data[1]
    end_index = data[2]

    if end == 1:
        extrap_strain = pd.Series(np.linspace(0, end, resolution))
    else:
        extrap_strain = pd.Series(
            np.linspace(0, df["plst_strain"][end-1], resolution))

    if extrap_type == 0:
        # Swift extrapolation
        Ag = data[3]
        Rm = data[4]

        n_0 = log(Ag+1)
        c_0 = Rm*(e/n_0)**n_0
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


def export_data(title: str, mid: str, rho: str, poisons_ratio: str, fail: str, point_no: int,
                spacing: str, fitted_data: list[list], E: str, path_str: str, template_path_str: str) -> Path:
    if int(point_no) > 100:
        raise ExportPointNoError from None
    else:
        np.export_data: dict = {}
        np.export_data["Title"] = title
        np.export_data["mid"] = mid.rjust(10)
        np.export_data["ro"] = rho.rjust(10)
        np.export_data["E"] = str(round(E, 2)).rjust(10)
        np.export_data["pr"] = poisons_ratio.rjust(10)
        np.export_data["fail"] = fail.rjust(10)

        if spacing == "equi" or point_no == 100:
            ids = np.linspace(0, 99, point_no)

        else:
            point_no_1 = round(point_no*0.6)
            point_no_2 = point_no - point_no_1

            ids_1 = np.linspace(0, 50, point_no_1)
            ids_1 = np.round(ids_1).astype(int)
            ids = set(ids_1)

            ids_2 = np.linspace(51, 99, point_no_2)
            ids_2 = np.round(ids_2).astype(int)

            ids.update(ids_2)

        for j, i in enumerate(ids):
            key_a = f"a{j+1}"
            key_o = f"o{j+1}"

            np.export_data[key_a] = str(round(fitted_data[0][i], 3)).rjust(20)
            np.export_data[key_o] = str(round(fitted_data[1][i], 3)).rjust(20)

        j += 1

        while j+1 <= 100:
            key_a = f"a{j+1}"
            key_o = f"o{j+1}"

            np.export_data[key_a] = "$"
            np.export_data[key_o] = "$"

            j += 1

        path: Path = write_to_file(np.export_data, path_str, template_path_str)

        return path


def write_to_file(data: dict, path_str: str, template_path_str: str) -> None:
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
