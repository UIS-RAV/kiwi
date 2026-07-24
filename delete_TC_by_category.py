import argparse
from typing import Any

from app.kiwi_client import create_kiwi_client


def get_id(item: dict[str, Any]) -> int:
    """
    Pobiera ID obiektu zwróconego przez Kiwi.
    """
    value = item.get("id") or item.get("pk")

    if value is None:
        raise ValueError(f"Nie znaleziono ID w obiekcie: {item}")

    return int(value)


def get_name(item: dict[str, Any]) -> str:
    """
    Pobiera nazwę obiektu.
    """
    return str(
        item.get("name")
        or item.get("summary")
        or "<brak nazwy>"
    )


def choose_from_list(
    items: list[dict[str, Any]],
    object_name: str,
) -> dict[str, Any]:
    """
    Wyświetla listę obiektów i pozwala wybrać jeden z nich.
    """
    if not items:
        raise ValueError(f"Nie znaleziono żadnych obiektów: {object_name}")

    print(f"\n===== WYBIERZ {object_name.upper()} =====")

    for index, item in enumerate(items, start=1):
        print(
            f"{index:3}. "
            f"ID {get_id(item)} - {get_name(item)}"
        )

    while True:
        selected = input(
            f"\nPodaj numer z listy lub ID {object_name}: "
        ).strip()

        if not selected.isdigit():
            print("Podaj liczbę.")
            continue

        selected_number = int(selected)

        # Najpierw sprawdzamy numer pozycji na liście.
        if 1 <= selected_number <= len(items):
            return items[selected_number - 1]

        # Następnie sprawdzamy, czy użytkownik podał bezpośrednio ID.
        for item in items:
            if get_id(item) == selected_number:
                return item

        print(
            f"Nie znaleziono {object_name} "
            f"dla wartości {selected_number}."
        )


def get_products(tcms) -> list[dict[str, Any]]:
    """
    Pobiera wszystkie projekty, czyli Product w Kiwi.
    """
    products = tcms.exec.Product.filter({})

    return sorted(
        products,
        key=lambda product: get_name(product).lower(),
    )


def get_product_by_id(
    tcms,
    product_id: int,
) -> dict[str, Any]:
    """
    Pobiera projekt po ID.
    """
    products = tcms.exec.Product.filter({
        "id": product_id,
    })

    if not products:
        products = tcms.exec.Product.filter({
            "pk": product_id,
        })

    if not products:
        raise ValueError(
            f"Projekt/Product o ID {product_id} nie istnieje."
        )

    return products[0]


def get_categories_for_product(
    tcms,
    product_id: int,
) -> list[dict[str, Any]]:
    """
    Pobiera kategorie należące do wskazanego projektu.
    """
    categories = tcms.exec.Category.filter({
        "product": product_id,
    })

    return sorted(
        categories,
        key=lambda category: get_name(category).lower(),
    )


def get_category_by_id(
    tcms,
    category_id: int,
) -> dict[str, Any]:
    """
    Pobiera kategorię po ID.
    """
    categories = tcms.exec.Category.filter({
        "id": category_id,
    })

    if not categories:
        categories = tcms.exec.Category.filter({
            "pk": category_id,
        })

    if not categories:
        raise ValueError(
            f"Kategoria o ID {category_id} nie istnieje."
        )

    return categories[0]


def get_category_product_id(
    category: dict[str, Any],
) -> int | None:
    """
    Pobiera ID projektu przypisanego do kategorii.
    Obsługuje kilka możliwych formatów odpowiedzi Kiwi.
    """
    product = category.get("product")

    if isinstance(product, dict):
        return get_id(product)

    if product is not None:
        return int(product)

    product_id = category.get("product_id")

    if product_id is not None:
        return int(product_id)

    return None


def get_test_cases(
    tcms,
    category_id: int,
) -> list[dict[str, Any]]:
    """
    Pobiera wszystkie TC należące do kategorii.
    """
    test_cases = tcms.exec.TestCase.filter({
        "category": category_id,
    })

    unique_cases = {}

    for test_case in test_cases:
        case_id = get_id(test_case)
        unique_cases[case_id] = test_case

    return [
        unique_cases[case_id]
        for case_id in sorted(unique_cases)
    ]


def print_test_cases(
    test_cases: list[dict[str, Any]],
) -> None:
    print("\n===== TEST CASE DO SKASOWANIA =====")

    for index, test_case in enumerate(test_cases, start=1):
        case_id = get_id(test_case)
        summary = get_name(test_case)

        print(
            f"{index:4}. TC-{case_id}: {summary}"
        )


def ask_for_confirmation(
    product: dict[str, Any],
    category: dict[str, Any],
    test_cases_count: int,
) -> bool:
    """
    Prosi o potwierdzenie kasowania.
    """
    product_id = get_id(product)
    category_id = get_id(category)

    confirmation_text = (
        f"DELETE {product_id} {category_id} {test_cases_count}"
    )

    print("\n==========================================")
    print("UWAGA: OPERACJA JEST NIEODWRACALNA")
    print("==========================================")
    print(f"Projekt:   {get_name(product)}")
    print(f"Kategoria: {get_name(category)}")
    print(f"Liczba TC: {test_cases_count}")
    print()
    print("Aby potwierdzić kasowanie, wpisz dokładnie:")
    print()
    print(confirmation_text)
    print()

    entered_text = input("Potwierdzenie: ").strip()

    return entered_text == confirmation_text


def delete_test_cases(
    tcms,
    test_cases: list[dict[str, Any]],
) -> None:
    """
    Usuwa testy pojedynczo.

    Dzięki temu dokładnie wiadomo, który TC został skasowany,
    a który ewentualnie zwrócił błąd.
    """
    success = 0
    failed = 0

    print("\n===== KASOWANIE =====")

    for index, test_case in enumerate(test_cases, start=1):
        case_id = get_id(test_case)
        summary = get_name(test_case)

        print(
            f"[{index}/{len(test_cases)}] "
            f"Kasowanie TC-{case_id}: {summary}"
        )

        try:
            tcms.exec.TestCase.remove({
                "pk": case_id,
            })

            print("  ✔ OK")
            success += 1

        except Exception as error:
            print(f"  ✖ ERROR: {error}")
            failed += 1

    print("\n===== PODSUMOWANIE KASOWANIA =====")
    print(f"Skasowano: {success}")
    print(f"Błędy:     {failed}")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Bezpieczne masowe kasowanie Test Case "
            "z Kiwi TCMS po projekcie i kategorii"
        )
    )

    parser.add_argument(
        "--project-id",
        "--product-id",
        dest="product_id",
        type=int,
        help=(
            "ID projektu. W Kiwi projekt występuje jako Product. "
            "Gdy parametr nie zostanie podany, skrypt pokaże listę."
        ),
    )

    parser.add_argument(
        "--category-id",
        type=int,
        help=(
            "ID kategorii. Gdy parametr nie zostanie podany, "
            "skrypt pokaże kategorie wybranego projektu."
        ),
    )

    args = parser.parse_args()

    print("Łączenie z Kiwi TCMS...")

    try:
        tcms = create_kiwi_client()
    except Exception as error:
        print(f"Nie udało się połączyć z Kiwi: {error}")
        return

    # -----------------------------------------
    # Wybór projektu
    # -----------------------------------------

    try:
        if args.product_id is not None:
            product = get_product_by_id(
                tcms=tcms,
                product_id=args.product_id,
            )
        else:
            products = get_products(tcms)

            product = choose_from_list(
                items=products,
                object_name="projekt",
            )

    except Exception as error:
        print(f"\nBłąd podczas wyboru projektu: {error}")
        return

    product_id = get_id(product)

    print("\n===== WYBRANY PROJEKT =====")
    print(f"ID:    {product_id}")
    print(f"Nazwa: {get_name(product)}")

    # -----------------------------------------
    # Wybór kategorii
    # -----------------------------------------

    try:
        if args.category_id is not None:
            category = get_category_by_id(
                tcms=tcms,
                category_id=args.category_id,
            )

            category_product_id = get_category_product_id(category)

            if (
                category_product_id is not None
                and category_product_id != product_id
            ):
                print("\nBŁĄD:")
                print(
                    f"Kategoria ID {args.category_id} "
                    f"nie należy do projektu ID {product_id}."
                )
                return

        else:
            categories = get_categories_for_product(
                tcms=tcms,
                product_id=product_id,
            )

            category = choose_from_list(
                items=categories,
                object_name="kategorię",
            )

    except Exception as error:
        print(f"\nBłąd podczas wyboru kategorii: {error}")
        return

    category_id = get_id(category)

    print("\n===== WYBRANA KATEGORIA =====")
    print(f"ID:    {category_id}")
    print(f"Nazwa: {get_name(category)}")

    # -----------------------------------------
    # Pobranie TC
    # -----------------------------------------

    try:
        test_cases = get_test_cases(
            tcms=tcms,
            category_id=category_id,
        )

    except Exception as error:
        print(f"\nBłąd podczas pobierania TC: {error}")
        return

    if not test_cases:
        print("\nWybrana kategoria nie zawiera żadnych Test Case.")
        return

    print_test_cases(test_cases)

    print("\n===== PODSUMOWANIE =====")
    print(
        f"Projekt:   {get_name(product)} "
        f"(ID: {product_id})"
    )
    print(
        f"Kategoria: {get_name(category)} "
        f"(ID: {category_id})"
    )
    print(f"Liczba TC do skasowania: {len(test_cases)}")

    # -----------------------------------------
    # Potwierdzenie
    # -----------------------------------------

    confirmed = ask_for_confirmation(
        product=product,
        category=category,
        test_cases_count=len(test_cases),
    )

    if not confirmed:
        print("\nNiepoprawne potwierdzenie.")
        print("Kasowanie zostało anulowane.")
        return

    # -----------------------------------------
    # Kontrola przed usunięciem
    # -----------------------------------------

    print("\nPonowne sprawdzanie zawartości kategorii...")

    try:
        current_test_cases = get_test_cases(
            tcms=tcms,
            category_id=category_id,
        )

    except Exception as error:
        print(f"Nie udało się ponownie pobrać TC: {error}")
        print("Kasowanie zostało anulowane.")
        return

    original_ids = {
        get_id(test_case)
        for test_case in test_cases
    }

    current_ids = {
        get_id(test_case)
        for test_case in current_test_cases
    }

    if original_ids != current_ids:
        print("\nZawartość kategorii zmieniła się.")
        print("Kasowanie zostało anulowane dla bezpieczeństwa.")

        added_ids = sorted(current_ids - original_ids)
        removed_ids = sorted(original_ids - current_ids)

        if added_ids:
            print(f"Nowe TC: {added_ids}")

        if removed_ids:
            print(f"Usunięte wcześniej TC: {removed_ids}")

        return

    # -----------------------------------------
    # Kasowanie
    # -----------------------------------------

    delete_test_cases(
        tcms=tcms,
        test_cases=test_cases,
    )

    # -----------------------------------------
    # Kontrola końcowa
    # -----------------------------------------

    try:
        remaining_test_cases = get_test_cases(
            tcms=tcms,
            category_id=category_id,
        )

    except Exception as error:
        print(f"\nNie udało się sprawdzić wyniku: {error}")
        return

    print("\n===== KONTROLA KOŃCOWA =====")

    if not remaining_test_cases:
        print("✔ Kategoria nie zawiera już żadnych Test Case.")
    else:
        print(
            f"W kategorii pozostało "
            f"{len(remaining_test_cases)} Test Case:"
        )

        print_test_cases(remaining_test_cases)


if __name__ == "__main__":
    main()