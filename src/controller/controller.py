from pathlib import Path
from service.correct_duplicates import CorrectDuplicates
from utils.dir_selector import DirectorySelector


class Controller:
    @staticmethod
    def run() -> None:
        with DirectorySelector() as selector:
            selected_dir = selector.select_dir()

        if not selected_dir:
            raise FileNotFoundError("Diretório não selecionado ou não encontrado.")

        xml_dir_path = Path(selected_dir)
        if not xml_dir_path.is_dir():
            raise FileNotFoundError(f"Diretório inválido: {xml_dir_path}")

        CorrectDuplicates(xml_dir_path).run()
