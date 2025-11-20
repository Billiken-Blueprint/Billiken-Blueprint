import urllib.parse
import httpx
import json

import urllib


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
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0.1 Safari/605.1.15",
    "Referer": "https://courses.slu.edu/",
    "Sec-Fetch-Dest": "empty",
    "Cookie": "_sctr=1%7C1760677200000; _scid=saX9DKYl-movJjDa-Zr2BoS6uY2lUabt; _scid_r=saX9DKYl-movJjDa-Zr2BoS6uY2lUabt; _fbp=fb.1.1760718030332.864230374654775960; _ga=GA1.2.718985217.1760718030; _tt_enable_cookie=1; _ttp=01K7SFJ1JCYSHN7ZWYM01WMH11_.tt.1; nmstat=21598240-ad45-9b21-fd87-ce40fa1af76a; ttcsid=1760718030422::JC-Fggr2uihph7FPNF5r.1.1760718030734.0; ttcsid_CQT8A2BC77U2FBUJG0TG=1760718030421::xdUGsWLBMTRTRZSJ3zVd.1.1760718030735.0; __utmzz=utmcsr=google|utmcmd=organic|utmccn=(not set)|utmcct=(not set)|utmctr=(not provided)|utmgclid=(not set); _ga_5MQ9L3X3YS=GS2.1.s1760718029$o1$g0$t1760718029$j60$l0$h0; _ga_FTVG57K2SJ=GS2.1.s1760718029$o1$g0$t1760718029$j60$l0$h0; _gcl_au=1.1.1644772738.1760718030",
    "X-Requested-With": "XMLHttpRequest",
    "Priority": "u=3, i",
}


async def get_sections(course_code: str, semeseter: str, crns: list[str]):
    payload = dict(
        group=f"code:{course_code}",
        key="",
        srcdb=semeseter,
        matched="crn:" + ",".join(crns),
        userWithRolesStr="!!!!!!",
    )
    payload = urllib.parse.quote(json.dumps(payload))

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, content=payload)
        response.raise_for_status()
        data = response.json()
        return data
