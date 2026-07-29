import argparse
import os
import re
import unicodedata

from app.kiwi_client import create_kiwi_client
from app.importer import create_test_case

PRIORITY_MAPPING = {
    "krytyczny": "krytyczny/natychmiastowy",
    "krytyczny/natychmiastowy": "krytyczny/natychmiastowy",
    "wysoki": "wysoki",
    "normalny": "normalny",
    "sredni": "normalny",
    "niski": "niski",
    "pilny": "pilny",
}

def get_files_from_folder(folder_path):
    files = []

    for file in os.listdir(folder_path):
        if file.endswith(".txt"):
            files.append(file)

    return sorted(files)


def get_summary_from_filename(filename):
    return os.path.splitext(filename)[0]

# Obsługa priorytetów

def normalize_text(value):
    value = value.strip().lower()

    value = unicodedata.normalize("NFKD", value)

    value = "".join(
        character
        for character in value
        if not unicodedata.combining(character)
    )

    return value


def get_priority_from_text(raw_text):
    match = re.search(
        r"^\s*Priorytet\s*:\s*(.*?)\s*$",
        raw_text,
        flags=re.IGNORECASE | re.MULTILINE,
    )

    if not match:
        raise ValueError(
            "Brak pola 'Priorytet:' w pliku TXT"
        )

    priority_name = match.group(1).strip()

    if not priority_name:
        raise ValueError(
            "Pole 'Priorytet:' nie zawiera wartości"
        )

    return priority_name


def get_object_id(item):
    object_id = item.get("id")

    if object_id is None:
        object_id = item.get("pk")

    if object_id is None:
        raise ValueError(
            f"Nie można odczytać ID obiektu: {item}"
        )

    return int(object_id)


def get_priority_name(priority):
    return str(
        priority.get("value")
        or priority.get("name")
        or priority.get("priority")
        or ""
    ).strip()


def get_kiwi_priorities(tcms):
    priorities = tcms.exec.Priority.filter({})

    if not priorities:
        raise ValueError(
            "Kiwi nie zwróciło żadnych priorytetów"
        )

    return priorities


def resolve_priority_id(
    priority_from_file,
    kiwi_priorities,
):
    normalized_priority = normalize_text(
        priority_from_file
    )

    expected_kiwi_priority = PRIORITY_MAPPING.get(
        normalized_priority
    )

    if expected_kiwi_priority is None:
        raise ValueError(
            f"Nieobsługiwany priorytet: "
            f"'{priority_from_file}'"
        )

    for kiwi_priority in kiwi_priorities:
        kiwi_priority_name = get_priority_name(
            kiwi_priority
        )

        if (
            normalize_text(kiwi_priority_name)
            == expected_kiwi_priority
        ):
            return (
                get_object_id(kiwi_priority),
                kiwi_priority_name,
            )

    available_priorities = ", ".join(
        get_priority_name(priority)
        for priority in kiwi_priorities
    )

    raise ValueError(
        f"Nie znaleziono priorytetu "
        f"'{expected_kiwi_priority}' w Kiwi. "
        f"Dostępne: {available_priorities}"
    )

# Koniec definicji do obsługi priorytetów

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
    # Pobranie dostępnych priorytetów z Kiwi.
    # Robimy to tylko raz przed rozpoczęciem importu.
    try:
        kiwi_priorities = get_kiwi_priorities(tcms)

    except Exception as error:
        print(
            f"Nie udało się pobrać priorytetów z Kiwi: {error}"
        )
        return

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

            # Odczyt wartości z linii:
            # Priorytet: Krytyczny
            priority_from_file = get_priority_from_text(
                raw_text
            )

            # Zamiana wartości z TXT na ID priorytetu w Kiwi.
            priority_id, kiwi_priority_name = resolve_priority_id(
                priority_from_file=priority_from_file,
                kiwi_priorities=kiwi_priorities,
            )

            print(
                f"  Priorytet: {priority_from_file} "
                f"-> {kiwi_priority_name} "
                f"(ID: {priority_id})"
            )

            case_id = create_test_case(
                tcms=tcms,
                summary=summary,
                category_id=args.category_id,
                raw_text=raw_text,
                priority_id=priority_id,
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