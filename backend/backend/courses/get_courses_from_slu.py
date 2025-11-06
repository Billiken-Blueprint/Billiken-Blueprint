import json

import requests
import urllib.parse


def get_courses_from_slu(semester: str, keyword: str):
    url = f"https://courses.slu.edu/api/?page=fose&route=search&keyword={keyword}"
    payload = urllib.parse.quote(
        json.dumps(
            {
                "other": {"srcdb": semester},
                "criteria": [{"field": "keyword", "value": keyword}],
            }
        )
    )
    headers = {
        "Content-Type": "application/json",
        "Pragma": "no-cache",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Sec-Fetch-Site": "same-origin",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Sec-Fetch-Mode": "cors",
        "Accept-Encoding": "gzip, deflate, br",
        "Origin": "https://courses.slu.edu",
        "Content-Length": "138",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0.1 Safari/605.1.15",
        "Referer": "https://courses.slu.edu/",
        "Sec-Fetch-Dest": "empty",
        "X-Requested-With": "XMLHttpRequest",
        "Priority": "u=3, i",
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    body = response.json()

    # Return a simple, serializable structure rather than trying to
    # instantiate the ORM `Course` model here. Each entry contains the
    # course code, title, and CRN (if present).
    results = []
    for x in body.get("results", []):
        results.append(
            {
                "code": x.get("code"),
                "title": x.get("title"),
                "crn": x.get("crn"),
            }
        )

    return results
