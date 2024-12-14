from pathlib import Path

class FileError(Exception):
    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path
        self.message = f"The provided file: {file_path} does not exist."

        super().__init__(self.message)

class ExportPointNoError(Exception):
    def __init__(self) -> None:
        self.message = "The number of points to export must range between 2 and 100."

        super().__init__(self.message)

class TemplateError(Exception):
    """
    Custom Error. Raised when no template file exists.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.message = f"{self.path} is not a valid template file."

        super().__init__(self.message)

class DataError(Exception):
    """
    Custom Error. Raised when input data does not conform with expectations.
    """

    def __init__(self, row_no:int) -> None:
        self.row_no = row_no
        self.message = f"Expected 2 columns in file, but found {row_no}."

        super().__init__(self.message)