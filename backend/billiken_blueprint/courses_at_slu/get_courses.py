import json
import urllib.parse

import httpx

from billiken_blueprint.courses_at_slu.course import Course

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
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0.1 Safari/605.1.15",
    "Referer": "https://courses.slu.edu/",
    "Sec-Fetch-Dest": "empty",
    "X-Requested-With": "XMLHttpRequest",
    "Priority": "u=3, i",
}


async def get_courses(keyword: str, semester: str):
    url = f"https://courses.slu.edu/api/?page=fose&route=search&keyword={keyword}"
    payload = {
        "other": {"srcdb": semester},
        "criteria": [{"field": "keyword", "value": keyword}],
    }
    payload = urllib.parse.quote(json.dumps(payload))

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, content=payload)
        response.raise_for_status()
        data = response.json()
        courses = [
            Course(code=course["code"], title=course["title"], crn=course["crn"])
            for course in data.get("results", [])
        ]

    return courses
