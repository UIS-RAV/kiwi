import argparse
import ssl

from tcms_api import TCMS
import config
from app.importer import create_test_case


ssl._create_default_https_context = ssl._create_unverified_context


def main():
    parser = argparse.ArgumentParser(
        description="Tworzenie TestCase w Kiwi z gotowej treści."
    )
    parser.add_argument("--file", required=True, help="Plik z treścią testu")
    parser.add_argument("--summary", required=True, help="Nazwa test case")
    parser.add_argument("--category-id", type=int, required=True, help="ID kategorii")

    args = parser.parse_args()

    with open(args.file, "r", encoding="utf-8") as f:
        raw_text = f.read()

    tcms = TCMS(
        config.KIWI_URL,
        username=config.KIWI_USERNAME,
        password=config.KIWI_PASSWORD,
    )

    case_id = create_test_case(
        tcms=tcms,
        summary=args.summary,
        category_id=args.category_id,
        raw_text=raw_text,
    )

    print(f"Utworzono TestCase ID: {case_id}")


if __name__ == "__main__":
    main()