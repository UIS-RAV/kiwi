import ssl
from tcms_api import TCMS
import config

ssl._create_default_https_context = ssl._create_unverified_context

tcms = TCMS(
    config.KIWI_URL,
    username=config.KIWI_USERNAME,
    password=config.KIWI_PASSWORD
)

plans = tcms.exec.TestPlan.filter({})

for p in plans:
    print(f"ID: {p['id']}, Name: {p['name']}")