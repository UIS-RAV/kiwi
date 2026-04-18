import argparse

from app.kiwi_client import create_kiwi_client
from app.services import (
    get_test_plans,
    show_test_plans,
    ask_for_plan_id,
    get_plan_name,
    validate_plan_id,
    get_test_cases_from_plan,
)
from app.exporter import export_plan_to_docx


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Eksport test planu z Kiwi TCMS do pliku DOCX."
    )
    parser.add_argument(
        "--plan-id",
        type=int,
        help="ID test planu do eksportu. Jeśli nie podasz, program zapyta interaktywnie.",
    )
    parser.add_argument(
        "--list-plans",
        action="store_true",
        help="Tylko wyświetl dostępne test plany i zakończ program.",
    )
    return parser.parse_args()


def get_plan_by_id(plans: list[dict], plan_id: int) -> dict | None:
    for plan in plans:
        if plan["id"] == plan_id:
            return plan
    return None

def main() -> None:
    args = parse_args()

    print("Łączenie z Kiwi TCMS...")
    tcms = create_kiwi_client()

    print("Pobieranie test planów...")
    plans = get_test_plans(tcms)

    if not plans:
        print("Nie znaleziono żadnych test planów.")
        return

    if args.list_plans:
        show_test_plans(plans)
        return

    if args.plan_id is not None:
        if not validate_plan_id(plans, args.plan_id):
            print(f"Plan o ID {args.plan_id} nie istnieje.")
            print("\nDostępne Test Plany:\n")
            show_test_plans(plans)
            return
        selected_plan_id = args.plan_id
    else:
        show_test_plans(plans)
        selected_plan_id = ask_for_plan_id(plans)

    plan_name = get_plan_name(plans, selected_plan_id)

    print(f"\nPobieranie test case z planu ID = {selected_plan_id}...")
    cases = get_test_cases_from_plan(tcms, selected_plan_id)

    output_file = export_plan_to_docx(
        tcms=tcms,
        plan_name=plan_name,
        plan_id=selected_plan_id,
        cases=cases,
    )

    print(f"\nGotowe. Plik zapisany jako: {output_file}")


if __name__ == "__main__":
    main()