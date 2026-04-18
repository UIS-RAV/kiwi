import argparse

from app.kiwi_client import create_kiwi_client
from app.services import (
    get_products,
    show_products,
    ask_for_product_id,
    get_product_name,
    get_test_cases_from_product,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Pobieranie przypadków testowych z projektu (product) w Kiwi TCMS."
    )

    parser.add_argument(
        "--product-id",
        type=int,
        help="ID projektu (product). Jeśli brak – tryb interaktywny.",
    )

    parser.add_argument(
        "--list-products",
        action="store_true",
        help="Wyświetl listę projektów i zakończ.",
    )

    parser.add_argument(
        "--output",
        help="Ścieżka do pliku wyjściowego (txt). Jeśli brak – tylko print.",
    )

    return parser.parse_args()


def validate_product_id(products, product_id):
    valid_ids = {p["id"] for p in products}
    return product_id in valid_ids


def main():
    args = parse_args()

    print("Łączenie z Kiwi TCMS...")
    tcms = create_kiwi_client()

    print("Pobieranie projektów...")
    products = get_products(tcms)

    if not products:
        print("Brak projektów.")
        return

    # tylko lista
    if args.list_products:
        show_products(products)
        return

    # wybór produktu
    if args.product_id is not None:
        if not validate_product_id(products, args.product_id):
            print(f"Nie istnieje produkt o ID {args.product_id}")
            print("\nDostępne projekty:\n")
            show_products(products)
            return

        selected_product_id = args.product_id
    else:
        show_products(products)
        selected_product_id = ask_for_product_id(products)

    product_name = get_product_name(products, selected_product_id)

    print(f"\nPobieranie test case z produktu ID = {selected_product_id}...")
    cases = get_test_cases_from_product(tcms, selected_product_id)

    print(f"\nProdukt: {product_name}")
    print(f"Liczba przypadków: {len(cases)}\n")

    # zapis do pliku jeśli podano
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(f"Produkt: {product_name}\n")
            f.write(f"Liczba przypadków: {len(cases)}\n\n")

            for case in cases:
                line = f"ID: {case['id']} | Nazwa: {case['summary']}\n"
                f.write(line)
                print(line, end="")

        print(f"\nZapisano do pliku: {args.output}")

    else:
        for case in cases:
            print(f"ID: {case['id']} | Nazwa: {case['summary']}")


if __name__ == "__main__":
    main()