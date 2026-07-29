def create_test_case(
    tcms,
    summary: str,
    category_id: int,
    raw_text: str,
    priority_id: int,
):
    case = tcms.exec.TestCase.create({
        "summary": summary,
        "category": category_id,
        "text": raw_text,
        "case_status": 1,
        "priority": priority_id,
    })

    return case["id"]