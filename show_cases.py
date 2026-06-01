from app.kiwi_client import create_kiwi_client
from app.services import get_test_cases_from_product

tcms = create_kiwi_client()

cases = get_test_cases_from_product(
    tcms=tcms,
    product_id=3,
    category_id=59,
)

print(cases[0])