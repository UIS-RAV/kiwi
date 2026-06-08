import argparse
from app.kiwi_client import create_kiwi_client


def parse_args():
    parser = argparse.ArgumentParser(
        description="Lista Test Run i usuwanie daty zakończenia przypadkowo zakończonego Test Run."
    )

    parser.add_argument("--run-id", type=int, help="ID Test Run do wznowienia.")
    parser.add_argument("--limit", type=int, default=30, help="Ile Test Run wyświetlić.")
    parser.add_argument("--dry-run", action="store_true", help="Tylko pokaż, bez zmiany.")

    return parser.parse_args()


def show_runs(runs):
    print("\nDostępne Test Run:\n")
    for run in runs:
        print(
            f"ID: {run.get('id')} | "
            f"Nazwa: {run.get('summary') or run.get('name')} | "
            f"Plan: {run.get('plan')} | "
            f"Start: {run.get('start_date')} | "
            f"Stop: {run.get('stop_date')}"
        )


def ask_for_run_id():
    while True:
        value = input("\nPodaj ID Test Run do wznowienia: ").strip()
        if value.isdigit():
            return int(value)
        print("To nie jest poprawne ID.")


def main():
    args = parse_args()

    print("Łączenie z Kiwi TCMS...")
    tcms = create_kiwi_client()

    print("Pobieranie Test Run...")
    runs = tcms.exec.TestRun.filter({})

    runs = sorted(runs, key=lambda r: r.get("id", 0), reverse=True)
    show_runs(runs[:args.limit])

    run_id = args.run_id or ask_for_run_id()

    selected = None
    for run in runs:
        if run.get("id") == run_id:
            selected = run
            break

    if not selected:
        print(f"Nie znaleziono Test Run ID={run_id}")
        return

    print("\n=== WYBRANY TEST RUN ===")
    print(f"ID: {selected.get('id')}")
    print(f"Nazwa: {selected.get('summary') or selected.get('name')}")
    print(f"Start: {selected.get('start_date')}")
    print(f"Stop: {selected.get('stop_date')}")

    if not selected.get("stop_date"):
        print("\nTen Test Run nie ma ustawionej daty zakończenia.")
        return

    if args.dry_run:
        print("\nDRY RUN — data zakończenia zostałaby wyczyszczona.")
        return

    confirmation = input("\nAby usunąć datę zakończenia, wpisz TAK: ").strip()

    if confirmation != "TAK":
        print("Anulowano.")
        return

    tcms.exec.TestRun.update(
        run_id,
        {
            "stop_date": None,
        },
    )

    print(f"\nGotowe. Usunięto datę zakończenia dla Test Run ID={run_id}")


if __name__ == "__main__":
    main()