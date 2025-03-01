# MAT_24_CurveFitter

![version](https://img.shields.io/badge/version-0.1-blue)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

This applications intend is to help the user create a *MAT_24 Ls-Dyna material card from given material test data.
The user can choose from three different methods for fitting and extrapolating the test data.
The below screenshots show the differences between the input data and the fitted and extrapolated data as well as the applications user interface.

![extrapolations](docs\Example_Material_Curves.svg)
![interface](docs\User_Interface.jpg)

**Table of Contents**

- [Installation](#installation)
- [Execution / Usage](#execution--usage)
- [Technologies](#technologies)
- [Features](#features)
- [Author](#author)
- [Change log](#change-log)
- [License](#license)

## Installation

On Windows:

Find the requirements.txt file in the **MAT_24_CurveFitter** folder. Then open a command window and execute the follwing command:
```sh
pip install -r /path/to/requirements.txt
```
This installs all necessary packages to run *MAT_24 CurveFitter.

## Execution / Usage

To run *MAT_24 CurveFitter find CF_main.py in the **CurveFitter** folder in the project directory. You can also open a command window and navigate to said folder to execute the following command:

```sh
python CF_main.py
```

To make yourself familiar with how to use *MAT_24 CurveFitter you can try to import the csv-file in the **data** folder in the project directory by clicking the *Import* button.
Afterwards you can fit and extrapolate a curve to the imported data with the *Fit and Extrapolate Curve* button. The fitting method can be selected in *Settings*. To write the fitted data to a *MAT_24 material card use the *Export to.k-file* button. The number of data points to be exported can also be selected in *Settings*.

Please note that *MAT_24_CurveFitter is unit independend. It is therefore upon the user to make sure that the input data is provided in a consistent unit system of the users choice. Also the data provided needs to be stress-strain data where to first collumn in the .csv-file represent the strain values.

## Technologies

*MAT_24_CurveFitter uses the following technologies and tools:

- [Python](https://www.python.org/): ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

## Features

*MAT_24_CurveFitter currently has the following set of features:

- Import .csv-files with or without header.
- Select from three different methods for data fitting and extrapolation (Voce, Swift, Voce-Swift).
- Selection of the number of data points to be used for computation of the Youngs Modulus (the number effects the result).
- Useage of custom .k-file templates.

*MAT_24_CurveFitter does not currently support:

- Creation of tabulated material cards e.g. to discribe strain rate dependency.
- Routine to process material data with a distinct yield strength. If such material data is loaded it will be process as data without a distinct yield strength.

## Author

Yannick Keller – yannick-keller@posteo.de

## Change log

- 0.1
    - First working version

## License

*MAT_24_CurveFitter is distributed under the MIT license. See [`LICENSE`](LICENSE.md) for more details.