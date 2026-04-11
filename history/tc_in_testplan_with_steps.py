import ssl
from tcms_api import TCMS
import config

ssl._create_default_https_context = ssl._create_unverified_context

tcms = TCMS(
    config.KIWI_URL,
    username=config.KIWI_USERNAME,
    password=config.KIWI_PASSWORD
)

cases = tcms.exec.TestCase.filter({
    "plan": 6
})

for c in cases:
    print("=" * 80)
    print(f"ID: {c['id']}")
    print(f"Nazwa: {c['summary']}")
    print("Kroki testowe:")
    print(c.get("text", "Brak tekstu"))
    print()