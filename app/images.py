import os
import re
from pathlib import Path
from urllib.parse import urljoin

import requests

import config


def ensure_download_dir() -> Path:
    path = Path(config.DOWNLOAD_DIR)
    path.mkdir(exist_ok=True)
    return path


def extract_image_paths(text: str | None) -> list[str]:
    if not text:
        return []

    pattern = r'!\[.*?\]\((/uploads/attachments/[^)]+)\)'
    return re.findall(pattern, str(text))


def download_image(relative_path: str) -> Path | None:
    download_dir = ensure_download_dir()

    try:
        full_url = urljoin(config.KIWI_BASE_WEB_URL, relative_path)
        filename = os.path.basename(relative_path)
        local_path = download_dir / filename

        response = requests.get(
            full_url,
            verify=config.SSL_VERIFY,
            timeout=30,
        )
        response.raise_for_status()

        with open(local_path, "wb") as file_handle:
            file_handle.write(response.content)

        return local_path
    except Exception as exc:
        print(f"Nie udało się pobrać obrazka: {relative_path}")
        print(f"Błąd: {exc}")
        return None