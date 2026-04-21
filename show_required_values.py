from app.kiwi_client import create_kiwi_client

tcms = create_kiwi_client()

print("CASE STATUS:")
for item in tcms.exec.TestCaseStatus.filter({}):
    print(item)

print("\nPRIORITY:")
for item in tcms.exec.Priority.filter({}):
    print(item)