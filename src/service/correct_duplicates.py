from pathlib import Path
from utils.xml_processor import XmlProcessor


class CorrectDuplicates:
    def __init__(self, xml_dir_path: Path) -> None:
        self._xml_dir_path: Path = xml_dir_path
        self._xmls_path_list: list[Path] = sorted(
            file_path for file_path in xml_dir_path.glob("*.xml") if file_path.is_file()
        )
        self._output_dir_path: Path = xml_dir_path / "corrigidos"

    def _process_xml(self, xml_path: Path) -> None:
        worker = XmlProcessor(xml_path)
        output_path = self._output_dir_path / xml_path.name
        worker.process_xml(output_path)

    def run(self) -> None:
        if not self._xmls_path_list:
            return

        self._output_dir_path.mkdir(parents=True, exist_ok=True)
        for xml_path in self._xmls_path_list:
            self._process_xml(xml_path)