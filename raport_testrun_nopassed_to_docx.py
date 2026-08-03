import argparse

from app.kiwi_client import create_kiwi_client
from app.services import (
    get_test_runs,
    show_test_runs,
    ask_for_run_id,
    validate_run_id,
    get_run_name,
    get_test_executions_with_comments_from_run,
    get_non_passed_executions,
)
from app.exporter import export_run_report_to_docx


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Eksport do DOCX wyłącznie testów, "
            "które nie mają statusu PASSED."
        )
    )

    parser.add_argument(
        "--run-id",
        type=int,
        help=(
            "ID Test Run do eksportu. "
            "Jeśli brak, program zapyta interaktywnie."
        ),
    )

    parser.add_argument(
        "--list-runs",
        action="store_true",
        help="Wyświetl dostępne Test Run i zakończ program.",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=30,
        help="Ile ostatnich Test Run pokazać na liście.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print("Łączenie z Kiwi TCMS...")
    tcms = create_kiwi_client()

    print("Pobieranie Test Run...")
    runs = get_test_runs(tcms)
    runs = sorted(
        runs,
        key=lambda run: run.get("id", 0),
        reverse=True,
    )

    if not runs:
        print("Nie znaleziono żadnych Test Run.")
        return

    if args.list_runs:
        show_test_runs(runs[:args.limit])
        return

    if args.run_id is not None:
        if not validate_run_id(runs, args.run_id):
            print(
                f"Test Run o ID {args.run_id} nie istnieje."
            )
            print("\nDostępne Test Run:\n")
            show_test_runs(runs[:args.limit])
            return

        selected_run_id = args.run_id

    else:
        show_test_runs(runs[:args.limit])
        selected_run_id = ask_for_run_id(runs)

    run_name = get_run_name(
        runs,
        selected_run_id,
    )

    print(
        f"\nPobieranie wykonań i komentarzy "
        f"z Test Run ID = {selected_run_id}..."
    )

    all_executions = get_test_executions_with_comments_from_run(
        tcms=tcms,
        run_id=selected_run_id,
    )

    non_passed_executions = get_non_passed_executions(
        tcms=tcms,
        executions=all_executions,
    )

    print(
        f"Liczba wszystkich wykonań: "
        f"{len(all_executions)}"
    )
    print(
        f"Liczba testów innych niż PASSED: "
        f"{len(non_passed_executions)}"
    )

    if not non_passed_executions:
        print(
            "\nWszystkie testy mają status PASSED. "
            "Raport nie został wygenerowany."
        )
        return

    output_file = export_run_report_to_docx(
        tcms=tcms,
        run_name=run_name,
        run_id=selected_run_id,
        executions=non_passed_executions,
        report_title=(
            "Raport testów, które nie przeszły: "
            f"{run_name}"
        ),
        file_prefix="Raport_Testow_NOPASSED",
    )

    print(
        f"\nGotowe. Raport zapisany jako: "
        f"{output_file}"
    )


if __name__ == "__main__":
    main()