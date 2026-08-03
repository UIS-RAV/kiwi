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

def get_products(tcms):
    """Pobiera wszystkie produkty / projekty z Kiwi."""
    return tcms.exec.Product.filter({})


def show_products(products):
    """Wyświetla listę produktów."""
    print("\nDostępne projekty / produkty:\n")
    for product in products:
        print(f"ID: {product['id']} | Nazwa: {product['name']}")


def ask_for_product_id(products):
    """Pyta użytkownika o ID produktu i sprawdza, czy istnieje."""
    valid_ids = {product["id"] for product in products}

    while True:
        user_input = input("\nPodaj ID projektu / produktu: ").strip()

        if not user_input.isdigit():
            print("To nie jest liczba. Spróbuj ponownie.")
            continue

        product_id = int(user_input)

        if product_id not in valid_ids:
            print("Nie ma takiego projektu / produktu na liście. Spróbuj ponownie.")
            continue

        return product_id


def get_product_name(products, product_id):
    """Zwraca nazwę produktu po ID."""
    for product in products:
        if product["id"] == product_id:
            return str(product["name"])
    return f"Product {product_id}"


def get_test_cases_from_product(tcms, product_id, category_id=None):
    """Pobiera wszystkie TC z produktu: z planów i bez planów.
    Jeśli podano category_id, zwraca tylko TC z tej kategorii.
    """
    unique_cases = {}

    # 1. TC z planów należących do produktu
    plans = tcms.exec.TestPlan.filter({"product": product_id})

    for plan in plans:
        plan_id = plan["id"]
        cases = tcms.exec.TestCase.filter({"plan": plan_id})

        for case in cases:
            case_category_id = case.get("category")
            if category_id is None or case_category_id == category_id:
                unique_cases[case["id"]] = case

    # 2. Kategorie produktu
    categories = tcms.exec.Category.filter({})
    category_ids_for_product = {
        category["id"]
        for category in categories
        if category.get("product") == product_id
    }

    # 3. TC poza planami
    all_cases = tcms.exec.TestCase.filter({})

    for case in all_cases:
        case_category_id = case.get("category")

        if case_category_id in category_ids_for_product:
            if category_id is None or case_category_id == category_id:
                unique_cases[case["id"]] = case

    return list(unique_cases.values())

def get_categories(tcms):
    """Pobiera wszystkie kategorie."""
    return tcms.exec.Category.filter({})


def get_categories_for_product(tcms, product_id):
    """Pobiera kategorie tylko dla wybranego produktu."""
    categories = tcms.exec.Category.filter({})
    return [c for c in categories if c.get("product") == product_id]


def show_categories(categories):
    """Wyświetla listę kategorii."""
    print("\nDostępne kategorie:\n")
    for category in categories:
        print(f"ID: {category['id']} | Nazwa: {category['name']}")


def ask_for_category_id(categories):
    """Pyta użytkownika o ID kategorii i sprawdza, czy istnieje."""
    valid_ids = {category["id"] for category in categories}

    while True:
        user_input = input("\nPodaj ID kategorii: ").strip()

        if not user_input.isdigit():
            print("To nie jest liczba. Spróbuj ponownie.")
            continue

        category_id = int(user_input)

        if category_id not in valid_ids:
            print("Nie ma takiej kategorii na liście. Spróbuj ponownie.")
            continue

        return category_id


def get_category_name(categories, category_id):
    """Zwraca nazwę kategorii po ID."""
    for category in categories:
        if category["id"] == category_id:
            return str(category["name"])
    return f"Category {category_id}"

def get_categories(tcms):
    """Pobiera wszystkie kategorie."""
    return tcms.exec.Category.filter({})


def get_categories_for_product(tcms, product_id):
    """Pobiera kategorie przypisane do wybranego produktu."""
    categories = tcms.exec.Category.filter({})
    return [category for category in categories if category.get("product") == product_id]


def build_category_name_map(categories):
    """
    Buduje mapę:
    nazwa_kategorii_lower -> pełny obiekt kategorii
    """
    result = {}
    for category in categories:
        result[str(category["name"]).strip().lower()] = category
    return result

def get_test_runs(tcms):
    """Pobiera wszystkie Test Run."""
    return tcms.exec.TestRun.filter({})


def show_test_runs(runs):
    """Wyświetla listę Test Run."""
    print("\nDostępne Test Run:\n")
    for run in runs:
        print(
            f"ID: {run.get('id')} | "
            f"Nazwa: {run.get('summary') or run.get('name')} | "
            f"Plan: {run.get('plan')} | "
            f"Start: {run.get('start_date')} | "
            f"Stop: {run.get('stop_date')}"
        )


def ask_for_run_id(runs):
    """Pyta użytkownika o ID Test Run."""
    valid_ids = {run["id"] for run in runs}

    while True:
        user_input = input("\nPodaj ID Test Run: ").strip()

        if not user_input.isdigit():
            print("To nie jest poprawne ID. Spróbuj ponownie.")
            continue

        run_id = int(user_input)

        if run_id not in valid_ids:
            print("Nie ma takiego Test Run na liście. Spróbuj ponownie.")
            continue

        return run_id


def validate_run_id(runs, run_id):
    return run_id in {run["id"] for run in runs}


def get_run_name(runs, run_id):
    for run in runs:
        if run["id"] == run_id:
            return str(run.get("summary") or run.get("name") or f"Test Run {run_id}")
    return f"Test Run {run_id}"


def get_test_executions_from_run(tcms, run_id):
    """Pobiera wykonania testów z Test Run."""
    return tcms.exec.TestExecution.filter({"run": run_id})

def get_test_executions_with_comments_from_run(tcms, run_id):
    """
    Pobiera wykonania testów z Test Run
    wraz z komentarzami przypisanymi do wykonania.
    """
    executions = tcms.exec.TestExecution.filter({
        "run": run_id
    })

    for execution in executions:
        execution_id = execution.get("id")
        execution["comments"] = []

        if execution_id is None:
            continue

        try:
            comments = tcms.exec.TestExecution.get_comments(
                execution_id
            )

            execution["comments"] = comments or []

        except Exception as error:
            print(
                f"Nie udało się pobrać komentarzy "
                f"dla Execution ID {execution_id}: {error}"
            )

    return executions

def get_non_passed_executions(
    tcms,
    executions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Zwraca wyłącznie wykonania, których status jest inny niż PASSED.

    Status wykonania w danych TestExecution jest identyfikatorem,
    dlatego nazwy statusów pobierane są z TestExecutionStatus.
    """
    statuses = tcms.exec.TestExecutionStatus.filter({})

    status_map = {
        status["id"]: str(status["name"]).strip()
        for status in statuses
    }

    non_passed_executions = []

    for execution in executions:
        status_id = execution.get("status")

        status_name = str(
            execution.get("status__name")
            or execution.get("status_name")
            or status_map.get(status_id)
            or status_id
            or ""
        ).strip()

        if status_name.upper() != "PASSED":
            non_passed_executions.append(execution)

    return non_passed_executions