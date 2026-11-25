import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog


def _resource_path(relative_path: str) -> str:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent.parent))
    return str(base / relative_path)


class DirectorySelector:
    def __init__(self) -> None:
        self._root: tk.Tk | None = None

    def __enter__(self) -> "DirectorySelector":
        self._root = tk.Tk()
        self._root.withdraw()
        self._root.attributes("-topmost", True)

        icon_path = Path(_resource_path("src/assets/icon_ccxml.ico"))
        if icon_path.exists():
            try:
                self._root.iconbitmap(str(icon_path))
                self._root.iconbitmap(default=str(icon_path))
                self._root.update_idletasks()
            except tk.TclError:
                pass

        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._root is not None:
            self._root.destroy()
            self._root = None

    def select_dir(self) -> str:
        return filedialog.askdirectory(
            parent=self._root,
            title="Selecione a pasta com os XMLs",
        )
