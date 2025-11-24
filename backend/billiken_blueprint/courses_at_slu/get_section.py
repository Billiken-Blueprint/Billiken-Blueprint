import time
import urllib.parse
import json
from exceptiongroup import catch
import httpx
import lxml.etree
import lxml.html

from billiken_blueprint.courses_at_slu.section import Section, MeetingTime

url = "https://courses.slu.edu/api/?page=fose&route=details"
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


async def get_section(course_code: str, crn: str, crns: list[str], semester: str):
    payload = dict(
        group=f"code:{course_code}",
        key=f"crn:{crn}",
        srcdb=semester,
        matched="crn:" + ",".join(crns),
        userWithRolesStr="!!!!!!",
    )
    payload = urllib.parse.quote(json.dumps(payload))

    # Try to load cache, create empty dict if file doesn't exist
    try:
        with open("response_cache.json", "r") as f:
            cached = json.load(f)
    except FileNotFoundError:
        cached = {}
    
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

    all_data = data["allInGroup"]
    all_data_this = [x for x in all_data if x["crn"] == crn][0]
    meeting_times = json.loads(all_data_this["meetingTimes"])

    try:
        instructors_tree = lxml.html.fromstring(data["instructordetail_html"])
    except lxml.etree.ParserError:
        instructors_tree = lxml.html.fromstring("<div></div>")

    return Section(
        meeting_times=[
            MeetingTime(
                day=mt["meet_day"],
                start_time=mt["start_time"],
                end_time=mt["end_time"],
            )
            for mt in meeting_times
        ],
        instructor_names=[
            instructor.strip() for instructor in instructors_tree.xpath("//div/text()")
        ],
        campus_code=data["campus_code"],
        description=data["description"],
        title=data["title"],
    )
