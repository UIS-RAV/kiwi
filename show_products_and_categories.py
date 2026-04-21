import argparse

from app.kiwi_client import create_kiwi_client
from app.services import (
    get_products,
    show_products,
    ask_for_product_id,
    get_product_name,
    get_categories_for_product,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Wyświetla produkty, a po wyborze pokazuje kategorie dla produktu."
    )

    parser.add_argument(
        "--product-id",
        type=int,
        help="ID produktu. Jeśli brak, skrypt zapyta interaktywnie.",
    )

    parser.add_argument(
        "--list-products",
        action="store_true",
        help="Tylko wyświetl listę produktów i zakończ.",
    )

    return parser.parse_args()


def validate_product_id(products, product_id):
    valid_ids = {product["id"] for product in products}
    return product_id in valid_ids


def main():
    args = parse_args()

    print("Łączenie z Kiwi TCMS...")
    tcms = create_kiwi_client()

    print("Pobieranie produktów...")
    products = get_products(tcms)

    if not products:
        print("Nie znaleziono żadnych produktów.")
        return

    if args.list_products:
        show_products(products)
        return

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

    print(f"\nPobieranie kategorii dla produktu: {product_name} (ID={selected_product_id})")
    categories = get_categories_for_product(tcms, selected_product_id)

    if not categories:
        print("Brak kategorii dla tego produktu.")
        return

    print(f"\nKategorie dla produktu: {product_name}\n")
    for category in sorted(categories, key=lambda c: str(c.get('name', '')).lower()):
        print(f"ID: {category['id']} | Nazwa: {category['name']}")


if __name__ == "__main__":
    main()