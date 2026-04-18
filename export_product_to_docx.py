import argparse

from app.kiwi_client import create_kiwi_client
from app.services import (
    get_products,
    show_products,
    ask_for_product_id,
    get_product_name,
    get_test_cases_from_product,
)
from app.exporter import export_product_to_docx


def parse_args():
    parser = argparse.ArgumentParser(
        description="Eksport wszystkich Test Case z produktu do DOCX."
    )

    parser.add_argument(
        "--product-id",
        type=int,
        help="ID produktu (project). Jeśli brak – tryb interaktywny.",
    )

    parser.add_argument(
        "--list-products",
        action="store_true",
        help="Wyświetl listę produktów i zakończ.",
    )

    return parser.parse_args()


def validate_product_id(products, product_id):
    valid_ids = {p["id"] for p in products}
    return product_id in valid_ids


def main():
    args = parse_args()

    print("Łączenie z Kiwi TCMS...")
    tcms = create_kiwi_client()

    print("Pobieranie produktów...")
    products = get_products(tcms)

    if not products:
        print("Brak produktów.")
        return

    # tylko lista
    if args.list_products:
        show_products(products)
        return

    # wybór produktu
    if args.product_id is not None:
        if not validate_product_id(products, args.product_id):
            print(f"Nie istnieje produkt o ID {args.product_id}")
            print("\nDostępne produkty:\n")
            show_products(products)
            return

        selected_product_id = args.product_id
    else:
        show_products(products)
        selected_product_id = ask_for_product_id(products)

    product_name = get_product_name(products, selected_product_id)

    print(f"\nPobieranie test case z produktu ID = {selected_product_id}...")
    cases = get_test_cases_from_product(tcms, selected_product_id)

    print(f"Znaleziono {len(cases)} test case")

    # 🔥 używamy tego samego eksportera co dla planów
    output_file = export_product_to_docx(
        product_name=product_name,
        product_id=selected_product_id,
        cases=cases,
    )

    print(f"\nGotowe. Plik zapisany jako: {output_file}")


if __name__ == "__main__":
    main()