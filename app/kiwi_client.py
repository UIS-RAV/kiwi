import ssl
import urllib3

from tcms_api import TCMS

import config


def configure_ssl() -> None:
    if not config.SSL_VERIFY:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        ssl._create_default_https_context = ssl._create_unverified_context


def create_kiwi_client() -> TCMS:
    configure_ssl()
    return TCMS(
        config.KIWI_URL,
        username=config.KIWI_USERNAME,
        password=config.KIWI_PASSWORD,
    )