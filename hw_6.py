from shutil import unpack_archive
import sys
from pathlib import Path
import re
import shutil


CATEGORIES = {
    "Image": [".jpeg", ".png", ".pcd", ".jpg", ".svg", ".tiff", ".raw", ".gif", ".bmp"],
    "Documents": [".docx", ".doc", ".txt", ".pdf", ".xls", ".xlsx", ".pptx", ".rtf"],
    "Audio": [".mp3", ".aiff", ".wav", ".aac", ".flac"],
    "Video": [".avi", ".mp4", ".mov", ".mkv", ".mpeg"],
    "Archive": [".zip", ".7-zip", ".7zip", ".rar", ".gz", ".tar"],
    "Book": [".fb2", ".mobi"]}

known_extensions = set(ext for ext_list in CATEGORIES.values() for ext in ext_list)
encountered_extensions = set()
unknown_extensions = set()


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
    unknown_extensions.add(ext)
    return "Other"


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
            encountered_extensions.add(element.suffix.lower())


def delete_empty_folders(path: Path) -> None:
    for folder in list(path.glob("**/*"))[::-1]:
        if folder.is_dir() and not any(folder.iterdir()):
            is_category_folder = any(cat in CATEGORIES.keys()
                                     for cat in folder.name)
            if not is_category_folder:
                folder.rmdir()


def unpack_archives(path: Path) -> None:
    archive_folder = path.joinpath("Archive")
    for file_name in archive_folder.glob("*"):
        if file_name.is_file():
            extract_folder = file_name.stem
            extract_path = archive_folder.joinpath(extract_folder)
            extract_path.mkdir(exist_ok=True)
            shutil.unpack_archive(str(file_name), extract_path)


def main():
    try:
        path = Path(sys.argv[1])
    except IndexError:
        print("No path to folder")
        return

    if not path.exists():
        print(f"Folder with path {path} does not exist.")
        return

    sort_folder(path)
    unpack_archives(path)
    delete_empty_folders(path)

    print("The task has been completed")


    print("\nFiles in Each Category:")
    for category in CATEGORIES.keys():
        category_path = path.joinpath(category)
        if category_path.exists():
            category_files = list(category_path.glob("*"))
            if category_files:
                print(f"{category}:")
                for file in category_files:
                    print(f" - {file}")


    print("\nUsed extentions:")
    for ext in encountered_extensions:
        print(ext)


    print("\nUnknown Extensions:")
    for ext in unknown_extensions:
        print(ext)


if __name__ == "__main__":
    main()
