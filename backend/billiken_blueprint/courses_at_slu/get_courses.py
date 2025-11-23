import json
import time
import urllib.parse
from dataclasses import dataclass

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


async def get_courses(keyword: str | None, semester: str, attribute_tag: str | None):
    url = f"https://courses.slu.edu/api/?page=fose&route=search&keyword={keyword}"
    criteria = []
    if keyword:
        criteria.append({"field": "keyword", "value": keyword})
    if attribute_tag:
        criteria.append({"field": attribute_tag, "value": "Y"})
    payload = {
        "other": {"srcdb": semester},
        "criteria": criteria,
    }
    payload = urllib.parse.quote(json.dumps(payload))

    with open("response_cache.json", "r") as f:
        cached = json.load(f)
    if payload in cached:
        data = cached[payload]
    else:
        time.sleep(3)
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, content=payload)
            response.raise_for_status()
            data = response.json()
            with open("response_cache.json", "w") as f:
                cached[payload] = data
                json.dump(cached, f, indent=4)

    courses = [
        Course(code=course["code"], title=course["title"], crn=course["crn"])
        for course in data.get("results", [])
    ]

    return courses
