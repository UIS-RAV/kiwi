from app.kiwi_client import create_kiwi_client

tcms = create_kiwi_client()

statuses = tcms.exec.TestCaseStatus.filter({})

for status in statuses:
    print(status)