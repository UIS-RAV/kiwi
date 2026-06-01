from app.kiwi_client import create_kiwi_client

tcms = create_kiwi_client()

for tag in tcms.exec.Tag.filter({}):
    print(tag)