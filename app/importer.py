def create_test_case(tcms, summary: str, category_id: int, raw_text: str):
    case = tcms.exec.TestCase.create({
        "summary": summary,
        "category": category_id,
        "text": raw_text,
        "case_status": 1,  # <- podmienisz na prawdziwe ID
        "priority": 1,  # <- podmienisz na prawdziwe ID
    })
    return case["id"]

