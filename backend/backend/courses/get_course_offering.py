import urllib.parse

import requests


def get_course_offering(semester: str, code: str, crn: str):
    url = "https://courses.slu.edu/api/?page=fose&route=details"
    payload = urllib.parse.urlencode(
        {"group": f"code:{code}", "key": f"crn:{crn}", "srcdb": semester, "matched": f"crn:{crn}",
         "userWithRolesStr": "!!!!!!"})
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
        'Content-Length': '181',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0.1 Safari/605.1.15',
        'Referer': 'https://courses.slu.edu/',
        'Sec-Fetch-Dest': 'empty',
        'X-Requested-With': 'XMLHttpRequest',
        'Priority': 'u=3, i'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
