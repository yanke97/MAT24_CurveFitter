import pandas as pd
from csv import Sniffer

header = ["strain", "stress"]
df = pd.read_csv(r"e:\15_MAT24_Curve fitter\00_Daten\external-x-tensile-trans2_strain_force.csv",
                 delimiter=";", header=0, names=header)
# print(df.head(10))
# df["strain"] = df["strain"]*100
# df["Force"] = df["Force"]/1000

B_0: float = 6.35       # specimen width [mm]
t_0: float = 3.124      # specimen thickness [mm]
A_0: float = B_0*t_0
df["stress"] = df["stress"]/A_0

df.to_csv(
    r"e:\15_MAT24_Curve fitter\00_Daten\external-x-tensile-trans2_stress_strain.csv", sep=";", index=False)

# col_names = ["disp", "strain_eng", "Force"]
# path = r"E:\15_MAT24_Curve fitter\00_Daten\tensile_1_shortened.csv"
# df_sample = pd.read_csv(path, delimiter=";", nrows=1, header=None)
# print(df_sample)
# # checks if an column in the first row is of datatype object (which indacte strings)
# # if so a header is assumed.
# # if df_sample.shape[1] > 2:
# #    print("error")
#
# def has_header(file_path):
#     with open(file_path, 'r') as f:
#         # Sniffer analyzes the first few lines
#         sniffer = Sniffer()
#         sample = f.read(1024)  # Read a sample from the file
#         return sniffer.has_header(sample)
#
#
# print(has_header(path))

# if df_sample.dtypes.isin([object,]).any():
#    print("Header")
#    df = pd.read_csv(path, delimiter=";", header=0, names=col_names)
# else:
#    print("No Header")
#    df = pd.read_csv(path, delimiter=";", header=None, names=col_names)
#
# print(df.head(10))
