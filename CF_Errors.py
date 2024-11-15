from pathlib import Path

class FileError(Exception):
    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path
        self.message = f"The provided file: {file_path} does not exist."

        super().__init__(self.message)