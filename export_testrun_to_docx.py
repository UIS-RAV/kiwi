import argparse

from app.kiwi_client import create_kiwi_client
from app.services import (
    get_test_runs,
    show_test_runs,
    ask_for_run_id,
    validate_run_id,
    get_run_name,
    get_test_executions_from_run,
)
from app.exporter import export_run_to_docx


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Eksport Test Run z Kiwi TCMS do pliku DOCX."
    )

    parser.add_argument(
        "--run-id",
        type=int,
        help="ID Test Run do eksportu. Jeśli brak, program zapyta interaktywnie.",
    )

    parser.add_argument(
        "--list-runs",
        action="store_true",
        help="Tylko wyświetl dostępne Test Run i zakończ program.",
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
    runs = sorted(runs, key=lambda r: r.get("id", 0), reverse=True)

    if not runs:
        print("Nie znaleziono żadnych Test Run.")
        return

    if args.list_runs:
        show_test_runs(runs[:args.limit])
        return

    if args.run_id is not None:
        if not validate_run_id(runs, args.run_id):
            print(f"Test Run o ID {args.run_id} nie istnieje.")
            print("\nDostępne Test Run:\n")
            show_test_runs(runs[:args.limit])
            return

        selected_run_id = args.run_id
    else:
        show_test_runs(runs[:args.limit])
        selected_run_id = ask_for_run_id(runs)

    run_name = get_run_name(runs, selected_run_id)

    print(f"\nPobieranie wykonań z Test Run ID = {selected_run_id}...")
    executions = get_test_executions_from_run(tcms, selected_run_id)

    output_file = export_run_to_docx(
        tcms=tcms,
        run_name=run_name,
        run_id=selected_run_id,
        executions=executions,
    )

    print(f"\nGotowe. Plik zapisany jako: {output_file}")


if __name__ == "__main__":
    main()