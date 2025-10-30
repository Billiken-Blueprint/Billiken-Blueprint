import requests
import json
import urllib.parse

from pydantic import BaseModel


class Semesters:
    SUMMER = "202600"
    FALL = "202610"
    WINTER = "202618"
    SPRING = "202620"


class CourseResult(BaseModel):
    key: str
    code: str
    title: str
    crn: str
    no: str
    total: str
    schd: str
    stat: str
    hide: str
    isCancelled: str
    meets: str
    mpkey: str
    meetingTimes: str
    instr: str
    start_date: str
    end_date: str


class GetCoursesResult(BaseModel):
    srcdb: str
    count: int
    results: list[CourseResult]


def get_courses(search_term: str, semester: str):
    url = f'https://courses.slu.edu/api/?page=fose&route=search&keyword={search_term}'

    payload = {
        'other': {
            'srcdb': semester
        },
        'criteria': [{
            'field': 'keyword',
            'value': search_term
        }]
    }
    payload = urllib.parse.quote(json.dumps(payload))

    headers = {
        'Content-Type': 'application/json',
        'Pragma': 'no-cache',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Sec-Fetch-Site': 'same-origin',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Sec-Fetch-Mode': 'cors',
        'Accept-Encoding': 'gzip, deflate, br',
        'Origin': 'https://courses.slu.edu',
        'Content-Length': '138',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0.1 Safari/605.1.15',
        'Referer': 'https://courses.slu.edu/',
        'Sec-Fetch-Dest': 'empty',
        'X-Requested-With': 'XMLHttpRequest',
        'Priority': 'u=3, i'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    body = response.json()

    with open('response.json', 'w') as f:
        json.dump(body, f, indent=4)

    return GetCoursesResult(**body)
