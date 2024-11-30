import pandas as pd
from pathlib import Path
from csv import Sniffer
from numpy import (log, exp, where, sign, diff, linspace)
from numpy import round as nround
from math import log as mlog, e
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


def comp_real_stress_strain(df: pd.DataFrame) -> pd.DataFrame:
    df["strain"] = log(1+(df["eng_strain"]))           # strain [-]
    df["stress"] = df["eng_stress"]*exp(df["strain"])     # stress [MPa]
    return df


def comp_material_data(df: pd.DataFrame, e_start: int, e_end: int) -> tuple:
    # compute youngs modulus
    res = curve_fit(_hooks_straight,
                    df["eng_strain"][0:300], df["eng_stress"][e_start:e_end])
    E = res[0][0]

    # compute Rp_02
    # Compute difference between measurement data and hooks straight
    difference = df["stress"] - (df["strain"]-0.002)*E

    # find the index at which a sing change occurs.
    # This is the point of the intersection.
    # np.sign writes -1 for negative index and 1 for positive index
    # np.diff writes a non zero value where the sign in the array changes
    # np.where returns the index
    sign_changes = where(diff(sign(difference)))[0]

    # Index of intersection
    Rp_02_I = int(sign_changes[0])
    # Rp_0.2 of the material
    Rp_02 = df["stress"][Rp_02_I]

    # Compute plastic strain curve
    df["plastic_strain"] = df["strain"][Rp_02_I::] - df["strain"][Rp_02_I]
    df["plastic_stress"] = df["stress"][Rp_02_I::]

    # Compute Failure strain A_5
    # Compute pandas series with stress drops
    stress_drop = pd.Series(df["plastic_stress"].diff())
    A_5_I = stress_drop.idxmin()-1
    A_5 = df["plastic_strain"][A_5_I]

    # Rm of the material
    Rm_I = df["stress"].idxmax()
    Rm = df["stress"][Rm_I]
    Ag = (df["strain"][Rm_I]) - (Rm/E)

    return df, [E, Rp_02, Rm, Rp_02_I, Rm_I, Ag, A_5]


def extrapolate(data: list, extrap_type: str) -> list:
    df = data[0]
    start_index = data[1]
    end_index = data[2]

    if extrap_type == "Swift":
        Ag = data[3]
        Rm = data[4]

        n_0 = mlog(Ag+1)
        c_0 = Rm*(e/n_0)**n_0
        phi_0 = 0.1

        initial_guess = [c_0, phi_0, n_0]

        res = curve_fit(_swift_extrapolation,
                        df["strain"][start_index:end_index]-df["strain"][start_index], df["stress"][start_index:end_index], initial_guess)

        c = res[0][0]
        phi = res[0][1]
        n = res[0][2]

        extrap_strain = pd.Series(linspace(0, 1, 100))
        extrap_stress = _swift_extrapolation(extrap_strain, c, phi, n)

        result = [extrap_strain, extrap_stress]

    return result


def export_data(title: str, mid: str, rho: str, poisons_ratio: str, fail: str, point_no: int,
                spacing: str, fitted_data: list[list], E: str, path_str: str, template_path_str:str) -> Path:
    if int(point_no) > 100:
        raise ExportPointNoError from None
    else:
        export_data: dict = {}
        export_data["Title"] = title
        export_data["mid"] = mid.rjust(10)
        export_data["ro"] = rho.rjust(10)
        export_data["E"] = str(round(E, 2)).rjust(10)
        export_data["pr"] = poisons_ratio.rjust(10)
        export_data["fail"] = fail.rjust(10)

        if spacing == "equi" or point_no == 100:
            ids = linspace(0, 99, point_no)

        else:
            point_no_1 = round(point_no*0.6)
            point_no_2 = point_no - point_no_1

            ids_1 = linspace(0, 50, point_no_1)
            ids_1 = nround(ids_1).astype(int)
            ids = set(ids_1)

            ids_2 = linspace(51, 99, point_no_2)
            ids_2 = nround(ids_2).astype(int)

            ids.update(ids_2)

        for j, i in enumerate(ids):
            key_a = f"a{j+1}"
            key_o = f"o{j+1}"

            export_data[key_a] = str(round(fitted_data[0][i], 3)).rjust(20)
            export_data[key_o] = str(round(fitted_data[1][i], 3)).rjust(20)

        j += 1

        while j+1 <= 100:
            key_a = f"a{j+1}"
            key_o = f"o{j+1}"

            export_data[key_a] = "$"
            export_data[key_o] = "$"

            j += 1

        path: Path = write_to_file(export_data, path_str, template_path_str)

        return path


def write_to_file(data: dict, path_str: str, template_path_str:str) -> None:
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
