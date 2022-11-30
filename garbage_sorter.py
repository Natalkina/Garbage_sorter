"""Garbage sorter is the application which do
sorting:
•	images ('JPEG', 'PNG', 'JPG', 'SVG');
•	videos ('AVI', 'MP4', 'MOV', 'MKV');
•	documents ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX');
•	music ('MP3', 'OGG', 'WAV', 'AMR');
•   archives ('ZIP', 'GZ', 'TAR');
•	unknown.
Additional functions:
•   normalize kirirlic to latin, other symbols to "_"
•   unpack all archives
"""

from pathlib import Path
import sys
import os
import shutil

sort_status = {
    "images": [],
    "videos": [],
    "documents": [],
    "music": [],
    "archives": [],
    "unknown": [],
    "known_extensions": set(),
    "unknown_extensions": set()
}


def main():
    if len(sys.argv) <= 1:
        source_dir = ""
    else:
        source_dir = sys.argv[1]

    # Create directories
    directories = ["images", "videos", "documents", "music", "archives", "unknown"]
    for directory in directories:
        # Path
        path = os.path.join(source_dir, directory)
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as error:
            print("Directory '%s' can not be created" % directory)

    path = Path(source_dir)
    items = path.glob("*")
    for item in items:
        if item.is_dir():
            if item.name not in directories:
                walk_dir(item, source_dir)
        else:
            handle_file(item, source_dir)
    print(sort_status)


def walk_dir(path, source_dir):
    if not path.exists():
        print(f"{path.absolute()} is not exist, please input truly name of path")
        return

    if not path.is_dir():
        print(f"{path} is file not folder")
        return

    items = path.glob("*")
    for item in items:
        if item.is_dir():
            walk_dir(item, source_dir)
        else:
            handle_file(item, source_dir)

    try:
        os.rmdir(path)
    except OSError as e:
        print("Error: %s : %s" % (path, e.strerror))


def handle_file(file, source_dir):
    if file.suffix[1:].upper() in ['ZIP', 'GZ', 'TAR']:
        shutil.unpack_archive(file, os.path.join(source_dir, "archives"))
        os.remove(file)
    else:
        rename_file(file, source_dir)


"""Rename_files"""


def rename_file(file, source_dir):
    # Adding the new name with extension
    new_base_name = normalize_filename(file.stem)

    extension_to_dir_map = {
        "images": ['JPEG', 'PNG', 'JPG', 'SVG'],
        "videos": ['AVI', 'MP4', 'MOV', 'MKV'],
        "documents": ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'],
        "music": ['MP3', 'OGG', 'WAV', 'AMR'],
    }
    # Move file to dir
    target_dir = "unknown"
    for dire in extension_to_dir_map:
        if file.suffix[1:].upper() in extension_to_dir_map[dire]:
            target_dir = dire
            break
    new_name = os.path.join(source_dir, target_dir, new_base_name + file.suffix)
    if os.path.exists(new_name):
        postfix = 1
        while True:
            new_name = os.path.join(source_dir, target_dir, new_base_name + str(postfix) + file.suffix)
            if not os.path.exists(new_name):
                break
            else:
                postfix += 1

    os.rename(file, new_name)

    sort_status[target_dir].append(new_name)
    if target_dir == "unknown":
        sort_status["unknown_extensions"].add(file.suffix[1:])
    else:
        sort_status["known_extensions"].add(file.suffix[1:])


"""Normalize function"""


def normalize_filename(text):
    result = ""
    for ch in text:
        if ch in CYRILLIC_SYMBOLS:
            result += translate(ch)
        elif ch.isalpha():
            result += ch
        elif ch.isnumeric():
            result += ch
        else:
            result += "_"
    return result


CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯЄІЇГ"
TRANSLATION = (
    "a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
    "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g",
    "A", "B", "V", "G", "D", "E", "E", "J", "Z", "I", "J", "K", "L", "M", "N", "O", "P", "R", "S", "T", "U",
    "F", "H", "Ts", "Ch", "Sh", "Sch", "", "Y", "", "E", "Yu", "Ya", "Je", "I", "Ji", "G",
)
TRANS = {}


def translate(name):
    for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
        TRANS[ord(c)] = l
        TRANS[ord(c.upper())] = l.upper()
    return name.translate(TRANS)


if __name__ == '__main__':
    main()
