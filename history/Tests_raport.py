import ssl
from tcms_api import TCMS
import config


# Tymczasowo wyłączamy weryfikację SSL,
# bo u Ciebie certyfikat wewnętrzny powodował błąd.
ssl._create_default_https_context = ssl._create_unverified_context


def connect_to_kiwi():
    """Tworzy połączenie z Kiwi TCMS."""
    return TCMS(
        config.KIWI_URL,
        username=config.KIWI_USERNAME,
        password=config.KIWI_PASSWORD
    )


def get_test_plans(tcms):
    """Pobiera wszystkie test plany."""
    return tcms.exec.TestPlan.filter({})


def show_test_plans(plans):
    """Wyświetla listę test planów."""
    print("\nDostępne Test Plany:\n")
    for plan in plans:
        print(f"ID: {plan['id']} | Nazwa: {plan['name']}")


def ask_for_plan_id(plans):
    """Pyta użytkownika o ID planu i sprawdza, czy istnieje."""
    available_ids = {plan["id"] for plan in plans}

    while True:
        user_input = input("\nPodaj ID test planu: ").strip()

        if not user_input.isdigit():
            print("To nie jest poprawny numer. Spróbuj ponownie.")
            continue

        plan_id = int(user_input)

        if plan_id not in available_ids:
            print("Nie ma takiego test planu na liście. Spróbuj ponownie.")
            continue

        return plan_id


def get_test_cases_from_plan(tcms, plan_id):
    """Pobiera wszystkie test case z wybranego test planu."""
    return tcms.exec.TestCase.filter({
        "plan": plan_id
    })


def show_test_cases_with_steps(cases):
    """Wyświetla test case wraz z treścią / krokami."""
    if not cases:
        print("\nBrak test case w tym planie.")
        return

    print(f"\nZnaleziono {len(cases)} test case.\n")

    for case in cases:
        print("=" * 100)
        print(f"ID TC: {case.get('id')}")
        print(f"Nazwa: {case.get('summary', 'Brak nazwy')}")
        print("-" * 100)
        print("Kroki / treść testu:\n")
        print(case.get("text", "Brak treści"))
        print()


def main():
    print("Łączenie z Kiwi TCMS...")
    tcms = connect_to_kiwi()

    print("Pobieranie test planów...")
    plans = get_test_plans(tcms)

    if not plans:
        print("Nie znaleziono żadnych test planów.")
        return

    show_test_plans(plans)

    selected_plan_id = ask_for_plan_id(plans)

    print(f"\nPobieranie test case z planu ID = {selected_plan_id}...")
    cases = get_test_cases_from_plan(tcms, selected_plan_id)

    show_test_cases_with_steps(cases)


if __name__ == "__main__":
    main()