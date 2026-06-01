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


STATUS_MAP = {
    "proposed": 1,
    "confirmed": 2,
    "disabled": 3,
    "need_update": 4,
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Bezpieczna zmiana statusu TC w wybranej kategorii."
    )

    parser.add_argument("--product-id", type=int)
    parser.add_argument("--category-id", type=int)
    parser.add_argument(
        "--from-status",
        choices=STATUS_MAP.keys(),
        required=True,
        help="Status źródłowy, np. proposed albo confirmed",
    )
    parser.add_argument(
        "--to-status",
        choices=STATUS_MAP.keys(),
        required=True,
        help="Status docelowy, np. confirmed albo proposed",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Tylko pokaż co zostałoby zmienione, bez zapisu.",
    )

    return parser.parse_args()


def validate_id(items, item_id):
    return item_id in {item["id"] for item in items}


def get_case_status_id(case):
    status = case.get("case_status")

    if isinstance(status, dict):
        return status.get("id")

    return status


def main():
    args = parse_args()

    from_status_id = STATUS_MAP[args.from_status]
    to_status_id = STATUS_MAP[args.to_status]

    if from_status_id == to_status_id:
        print("Status źródłowy i docelowy są takie same. Przerywam.")
        return

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

    print("\n=== PODSUMOWANIE OPERACJI ===")
    print(f"Produkt: {product_name} (ID={product_id})")
    print(f"Kategoria: {category_name} (ID={category_id})")
    print(f"Zmiana: {args.from_status.upper()} -> {args.to_status.upper()}")

    cases = get_test_cases_from_product(
        tcms=tcms,
        product_id=product_id,
        category_id=category_id,
    )

    to_update = [
        case for case in cases
        if get_case_status_id(case) == from_status_id
    ]

    skipped = len(cases) - len(to_update)

    print(f"\nZnaleziono TC w kategorii: {len(cases)}")
    print(f"Do zmiany: {len(to_update)}")
    print(f"Pominięte: {skipped}")

    if not to_update:
        print("\nBrak testów do zmiany.")
        return

    print("\nPrzypadki do zmiany:")
    for case in to_update:
        print(f"ID: {case['id']} | {case['summary']}")

    if args.dry_run:
        print("\nDRY RUN — nic nie zostało zmienione.")
        return

    confirmation = input("\nAby potwierdzić zmianę, wpisz TAK: ").strip()

    if confirmation != "TAK":
        print("Anulowano.")
        return

    success = 0
    failed = 0

    for case in to_update:
        try:
            tcms.exec.TestCase.update(
                case["id"],
                {
                    "case_status": to_status_id,
                },
            )
            print(f"✔ Zmieniono TC ID={case['id']}")
            success += 1
        except Exception as exc:
            print(f"✖ Błąd dla TC ID={case['id']}: {exc}")
            failed += 1

    print("\n=== WYNIK ===")
    print(f"Zmieniono: {success}")
    print(f"Błędy: {failed}")
    print(f"Pominięte: {skipped}")


if __name__ == "__main__":
    main()