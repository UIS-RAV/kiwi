import argparse
from pathlib import Path

from app.kiwi_client import create_kiwi_client
from app.importer import create_test_case
from app.services import (
    get_products,
    get_product_name,
    get_categories_for_product,
    build_category_name_map,
)


def get_summary_from_filename(filename: str) -> str:
    return Path(filename).stem


def parse_args():
    parser = argparse.ArgumentParser(
        description="Masowy import test case z folderu do Kiwi, gdzie podfolder = kategoria."
    )

    parser.add_argument(
        "--folder",
        required=True,
        help="Ścieżka do folderu głównego z podkatalogami kategorii",
    )

    parser.add_argument(
        "--product-id",
        type=int,
        required=True,
        help="ID produktu, do którego należą kategorie",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    tcms = create_kiwi_client()

    root_folder = Path(args.folder)
    if not root_folder.exists() or not root_folder.is_dir():
        print(f"Folder nie istnieje albo nie jest katalogiem: {root_folder}")
        return

    products = get_products(tcms)
    product_name = get_product_name(products, args.product_id)

    categories = get_categories_for_product(tcms, args.product_id)
    category_map = build_category_name_map(categories)

    if not category_map:
        print(f"Brak kategorii dla produktu ID={args.product_id} ({product_name})")
        return

    print(f"Produkt: {product_name}")
    print(f"Folder źródłowy: {root_folder}")
    print(f"Liczba kategorii w Kiwi dla produktu: {len(category_map)}\n")

    success = 0
    failed = 0
    skipped = 0

    # iterujemy po podfolderach
    for category_dir in sorted(root_folder.iterdir()):
        if not category_dir.is_dir():
            continue

        folder_category_name = category_dir.name.strip()
        folder_category_key = folder_category_name.lower()

        print(f"== Kategoria z folderu: {folder_category_name} ==")

        if folder_category_key not in category_map:
            print(f"Brak kategorii w Kiwi o nazwie: {folder_category_name}")
            print("Pomijam cały folder.\n")
            skipped += len(list(category_dir.glob("*.txt")))
            continue

        category = category_map[folder_category_key]
        category_id = category["id"]
        category_name = category["name"]

        txt_files = sorted(category_dir.glob("*.txt"))

        if not txt_files:
            print("Brak plików .txt w folderze.\n")
            continue

        for file_path in txt_files:
            summary = get_summary_from_filename(file_path.name)

            print(f"Import: {file_path.name} -> kategoria: {category_name} (ID={category_id})")

            try:
                raw_text = file_path.read_text(encoding="utf-8")

                case_id = create_test_case(
                    tcms=tcms,
                    summary=summary,
                    category_id=category_id,
                    raw_text=raw_text,
                )

                print(f"✔ OK (ID: {case_id})\n")
                success += 1

            except Exception as exc:
                print(f"✖ ERROR: {exc}\n")
                failed += 1

    print("===== PODSUMOWANIE =====")
    print(f"Sukces: {success}")
    print(f"Błędy: {failed}")
    print(f"Pominięte: {skipped}")


if __name__ == "__main__":
    main()