from typing import Any

from tcms_api import TCMS


def get_test_plans(tcms: TCMS) -> list[dict[str, Any]]:
    return tcms.exec.TestPlan.filter({})


def show_test_plans(plans: list[dict[str, Any]]) -> None:
    print("\nDostępne Test Plany:\n")
    for plan in plans:
        print(f"ID: {plan['id']} | Nazwa: {plan['name']}")


def ask_for_plan_id(plans: list[dict[str, Any]]) -> int:
    valid_ids = {plan["id"] for plan in plans}

    while True:
        user_input = input("\nPodaj ID test planu: ").strip()

        if not user_input.isdigit():
            print("To nie jest liczba. Spróbuj ponownie.")
            continue

        plan_id = int(user_input)

        if plan_id not in valid_ids:
            print("Nie ma takiego planu na liście. Spróbuj ponownie.")
            continue

        return plan_id


def get_plan_name(plans: list[dict[str, Any]], plan_id: int) -> str:
    for plan in plans:
        if plan["id"] == plan_id:
            return str(plan["name"])
    return f"Test Plan {plan_id}"


def get_test_cases_from_plan(tcms: TCMS, plan_id: int) -> list[dict[str, Any]]:
    return tcms.exec.TestCase.filter({"plan": plan_id})

def validate_plan_id(plans, plan_id):
    valid_ids = {plan["id"] for plan in plans}
    return plan_id in valid_ids