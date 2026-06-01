import argparse

from app.kiwi_client import create_kiwi_client
from app.services import (
    get_products,
    show_products,
    ask_for_product_id,
    get_product_name,
    get_categories_for_product,
    show_categories,
    ask_for_category_id,
    get_category_name,
    get_test_cases_from_product,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Dodaje tag do wszystkich TC z wybranej kategorii."
    )

    parser.add_argument("--product-id", type=int)
    parser.add_argument("--category-id", type=int)
    parser.add_argument("--tag", required=True, help="Nazwa taga, np. CRU")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Tylko pokaż, co zostałoby zmienione.",
    )

    return parser.parse_args()


def validate_id(items, item_id):
    return item_id in {item["id"] for item in items}


def case_has_tag(case, tag_name):
    tags = case.get("tag") or []

    for tag in tags:
        if isinstance(tag, dict) and str(tag.get("name", "")).lower() == tag_name.lower():
            return True

        if isinstance(tag, str) and tag.lower() == tag_name.lower():
            return True

    return False


def main():
    args = parse_args()

    print("Łączenie z Kiwi TCMS...")
    tcms = create_kiwi_client()

    products = get_products(tcms)

    if args.product_id:
        if not validate_id(products, args.product_id):
            print(f"Nie istnieje produkt ID={args.product_id}")
            show_products(products)
            return
        product_id = args.product_id
    else:
        show_products(products)
        product_id = ask_for_product_id(products)

    product_name = get_product_name(products, product_id)

    categories = get_categories_for_product(tcms, product_id)

    if args.category_id:
        if not validate_id(categories, args.category_id):
            print(f"Nie istnieje kategoria ID={args.category_id} dla produktu {product_name}")
            show_categories(categories)
            return
        category_id = args.category_id
    else:
        show_categories(categories)
        category_id = ask_for_category_id(categories)

    category_name = get_category_name(categories, category_id)

    cases = get_test_cases_from_product(
        tcms=tcms,
        product_id=product_id,
        category_id=category_id,
    )

    to_update = [case for case in cases if not case_has_tag(case, args.tag)]
    already_tagged = len(cases) - len(to_update)

    print("\n=== PODSUMOWANIE OPERACJI ===")
    print(f"Produkt: {product_name} (ID={product_id})")
    print(f"Kategoria: {category_name} (ID={category_id})")
    print(f"Tag do dodania: {args.tag}")
    print(f"Znaleziono TC w kategorii: {len(cases)}")
    print(f"Już posiada tag: {already_tagged}")
    print(f"Do oznaczenia: {len(to_update)}")

    if not to_update:
        print("\nBrak testów do oznaczenia.")
        return

    print("\nPrzypadki do oznaczenia:")
    for case in to_update:
        print(f"ID: {case['id']} | {case['summary']}")

    if args.dry_run:
        print("\nDRY RUN — nic nie zostało zmienione.")
        return

    confirmation = input("\nAby potwierdzić dodanie taga, wpisz TAK: ").strip()

    if confirmation != "TAK":
        print("Anulowano.")
        return

    success = 0
    failed = 0

    for case in to_update:
        try:
            tcms.exec.TestCase.add_tag(case["id"], args.tag)
            print(f"✔ Dodano tag do TC ID={case['id']}")
            success += 1
        except Exception as exc:
            print(f"✖ Błąd dla TC ID={case['id']}: {exc}")
            failed += 1

    print("\n=== WYNIK ===")
    print(f"Oznaczono: {success}")
    print(f"Błędy: {failed}")
    print(f"Już miało tag: {already_tagged}")


if __name__ == "__main__":
    main()