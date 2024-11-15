import pandas as pd
from pathlib import Path
from csv import Sniffer
from numpy import (log, exp, where, sign, diff)
from scipy.optimize import curve_fit

from CF_Errors import FileError


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


def comp_material_data(df: pd.DataFrame) -> tuple:
    # compute youngs modulus
    res = curve_fit(_hooks_straight,
                    df["eng_strain"][0:300], df["eng_stress"][0:300])
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

    # Rm of the material
    Rm_I = df["stress"].idxmax()
    Rm = df["stress"][Rm_I]

    return E, Rp_02, Rm, Rp_02_I, Rm_I
