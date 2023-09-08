from shutil import unpack_archive
import sys
from pathlib import Path
import re
import patoolib


CATEGORIES = {
    "Image": [".jpeg", ".png", ".pcd", ".jpg", ".svg", ".tiff", ".raw", ".gif", ".bmp"],
    "Documents": [".docx", ".doc", ".txt", ".pdf", ".xls", ".xlsx", ".pptx", ".rtf"],
    "Audio": [".mp3", ".aiff", ".wav", ".aac", ".flac"],
    "Video": [".avi", ".mp4", ".mov", ".mkv", ".mpeg"],
    "Archive": [".zip", ".7-zip", ".7zip", ".rar", ".gz", ".tar"],
    "Book": [".fb2", ".mobi"]}


def normalize(name):
    CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
    TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
                   "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")
    TRANS = {}
    for c, t in zip(CYRILLIC_SYMBOLS, TRANSLATION):
        TRANS[ord(c)] = t
        TRANS[ord(c.upper())] = t.upper()
    name = name.translate(TRANS)
    name = re.sub(r"[^a-zA-Z0-9.]", "_", name)
    return name


def get_categories(file: Path) -> str:
    ext = file.suffix.lower()
    for cat, exts in CATEGORIES.items():
        if ext in exts:
            return cat
    return "Other"

def unpack_archives(path: Path) -> None:
    archive_folder = path.joinpath("Archive")
    for file_name in archive_folder.glob("*"):
        if file_name.is_file():
            extract_folder = file_name.stem
            extract_path = archive_folder.joinpath(extract_folder)
            extract_path.mkdir(exist_ok=True)
            patoolib.extract_archive(str(file_name), outdir=str(extract_path))

def delete_empty_folders(path: Path) -> None:
    for folder in list(path.glob("**/*"))[::-1]:
        if folder.is_dir() and not any(folder.iterdir()):
            is_category_folder = any(cat in CATEGORIES.keys()
                                     for cat in folder.name)
            if not is_category_folder:
                folder.rmdir()
                
def move_file(file: Path, category: str, root_dir: Path) -> None:
    target_dir = root_dir.joinpath(category)
    if not target_dir.exists():
        target_dir.mkdir()
    new_path = target_dir.joinpath(file.name)
    if not new_path.exists():
        file.replace(new_path)


def sort_folder(path: Path) -> None:
    for element in path.glob("**/*"):
        if element.is_file():
            category = get_categories(element)
            move_file(element, category, path)


# def delete_empty_folders(path: Path) -> None:
#     for folder in list(path.glob("**/*"))[::-1]:
#         if folder.is_dir() and not any(folder.iterdir()):
#             is_category_folder = any(cat in CATEGORIES.keys()
#                                      for cat in folder.name)
#             if not is_category_folder:
#                 folder.rmdir()


# def unpack_archives(path: Path) -> None:
#     archive_folder = path.joinpath("Archive")
#     for file_name in archive_folder.glob("*"):
#         if file_name.is_file():
#             extract_folder = file_name.stem
#             extract_path = archive_folder.joinpath(extract_folder)
#             extract_path.mkdir(exist_ok=True)
#             patoolib.extract_archive(str(file_name), outdir=str(extract_path))


def main():
    try:
        path = Path(sys.argv[1])
    except IndexError:
        return "No path to folder"

    if not path.exists():
        return f"Folder with path {path} does`n exists."
    sort_folder(path)
    unpack_archive(path)
    delete_empty_folders(path)

    return "The task has been completed"


if __name__ == "__main__":
    main()
