import argparse
import os

from app.kiwi_client import create_kiwi_client
from app.importer import create_test_case


def get_files_from_folder(folder_path):
    files = []

    for file in os.listdir(folder_path):
        if file.endswith(".txt"):
            files.append(file)

    return sorted(files)


def get_summary_from_filename(filename):
    return os.path.splitext(filename)[0]


def main():
    parser = argparse.ArgumentParser(
        description="Masowy import test case z folderu do Kiwi"
    )

    parser.add_argument(
        "--folder",
        required=True,
        help="Ścieżka do folderu z plikami .txt"
    )

    parser.add_argument(
        "--category-id",
        type=int,
        required=True,
        help="ID kategorii"
    )

    args = parser.parse_args()

    tcms = create_kiwi_client()

    files = get_files_from_folder(args.folder)

    if not files:
        print("Brak plików .txt w folderze")
        return

    print(f"Znaleziono {len(files)} plików\n")

    success = 0
    failed = 0

    for file in files:
        file_path = os.path.join(args.folder, file)
        summary = get_summary_from_filename(file)

        print(f"Import: {file}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_text = f.read()

            case_id = create_test_case(
                tcms=tcms,
                summary=summary,
                category_id=args.category_id,
                raw_text=raw_text,
            )

            print(f"✔ OK (ID: {case_id})\n")
            success += 1

        except Exception as e:
            print(f"✖ ERROR: {e}\n")
            failed += 1

    print("===== PODSUMOWANIE =====")
    print(f"Sukces: {success}")
    print(f"Błędy: {failed}")


if __name__ == "__main__":
    main()