import argparse

from app.kiwi_client import create_kiwi_client
from app.services import (
    get_products,
    show_products,
    ask_for_product_id,
    get_product_name,
    get_test_cases_from_product,
    get_categories_for_product,
    show_categories,
    ask_for_category_id,
    get_category_name,
)
from app.exporter import export_product_to_docx


def parse_args():
    parser = argparse.ArgumentParser(
        description="Eksport wszystkich Test Case z produktu do DOCX."
    )

    parser.add_argument(
        "--product-id",
        type=int,
        help="ID produktu. Jeśli brak – tryb interaktywny.",
    )

    parser.add_argument(
        "--list-products",
        action="store_true",
        help="Wyświetl listę produktów i zakończ.",
    )

    parser.add_argument(
        "--category-id",
        type=int,
        help="ID kategorii do filtrowania.",
    )

    parser.add_argument(
        "--choose-category",
        action="store_true",
        help="Po wyborze produktu pokaż kategorie i pozwól wybrać jedną interaktywnie.",
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

    # wybór kategorii
    selected_category_id = None
    selected_category_name = None

    if args.choose_category or args.category_id is not None:
        categories = get_categories_for_product(tcms, selected_product_id)

        if not categories:
            print("Brak kategorii dla tego produktu.")
            return

        if args.category_id is not None:
            if not validate_category_id(categories, args.category_id):
                print(f"Nie istnieje kategoria o ID {args.category_id} dla produktu {product_name}")
                print("\nDostępne kategorie:\n")
                show_categories(categories)
                return

            selected_category_id = args.category_id
            selected_category_name = get_category_name(categories, selected_category_id)

        elif args.choose_category:
            show_categories(categories)
            selected_category_id = ask_for_category_id(categories)
            selected_category_name = get_category_name(categories, selected_category_id)

    print(f"\nPobieranie test case z produktu ID = {selected_product_id}...")
    if selected_category_id is not None:
        print(f"Filtr kategorii ID = {selected_category_id} ({selected_category_name})")

    cases = get_test_cases_from_product(
        tcms,
        selected_product_id,
        category_id=selected_category_id,
    )

    print(f"Znaleziono {len(cases)} test case")

    output_file = export_product_to_docx(
        tcms=tcms,
        product_name=product_name,
        product_id=selected_product_id,
        cases=cases,
        category_name=selected_category_name,
    )

    print(f"\nGotowe. Plik zapisany jako: {output_file}")

def validate_category_id(categories, category_id):
    valid_ids = {c["id"] for c in categories}
    return category_id in valid_ids

if __name__ == "__main__":
    main()