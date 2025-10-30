# courses.slu.edu scraping

When we search for 'csci', the browser makes a request

```bash
curl 'https://courses.slu.edu/api/?page=fose&route=search&keyword=csci' \
-X 'POST' \
-H 'Content-Type: application/json' \
-H 'Pragma: no-cache' \
-H 'Accept: application/json, text/javascript, */*; q=0.01' \
-H 'Sec-Fetch-Site: same-origin' \
-H 'Accept-Language: en-US,en;q=0.9' \
-H 'Cache-Control: no-cache' \
-H 'Sec-Fetch-Mode: cors' \
-H 'Accept-Encoding: gzip, deflate, br' \
-H 'Origin: https://courses.slu.edu' \
-H 'Content-Length: 138' \
-H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0.1 Safari/605.1.15' \
-H 'Referer: https://courses.slu.edu/' \
-H 'Sec-Fetch-Dest: empty' \
-H 'Cookie: _sctr=1%7C1760677200000; _scid=saX9DKYl-movJjDa-Zr2BoS6uY2lUabt; _scid_r=saX9DKYl-movJjDa-Zr2BoS6uY2lUabt; _fbp=fb.1.1760718030332.864230374654775960; _ga=GA1.2.718985217.1760718030; _tt_enable_cookie=1; _ttp=01K7SFJ1JCYSHN7ZWYM01WMH11_.tt.1; nmstat=21598240-ad45-9b21-fd87-ce40fa1af76a; ttcsid=1760718030422::JC-Fggr2uihph7FPNF5r.1.1760718030734.0; ttcsid_CQT8A2BC77U2FBUJG0TG=1760718030421::xdUGsWLBMTRTRZSJ3zVd.1.1760718030735.0; __utmzz=utmcsr=google|utmcmd=organic|utmccn=(not set)|utmcct=(not set)|utmctr=(not provided)|utmgclid=(not set); _ga_5MQ9L3X3YS=GS2.1.s1760718029$o1$g0$t1760718029$j60$l0$h0; _ga_FTVG57K2SJ=GS2.1.s1760718029$o1$g0$t1760718029$j60$l0$h0; _gcl_au=1.1.1644772738.1760718030' \
-H 'X-Requested-With: XMLHttpRequest' \
-H 'Priority: u=3, i' \
--data-raw '%7B%22other%22%3A%7B%22srcdb%22%3A%22202610%22%7D%2C%22criteria%22%3A%5B%7B%22field%22%3A%22keyword%22%2C%22value%22%3A%22csci%22%7D%5D%7D'
```

Notably, data-raw is urlencoded 
```json
{
  "other": {
    "srcdb": "202610"
  },
  "criteria":[
    {
      "field": "keyword",
      "value": "csci"
    }
  ]
}
```

Then internally, courses.slu.edu seems to query the database
called ${params.page}-clss${data-raw.other.srcdb}. It seems like 
params.page is always 'fose', so it's always querying 'fose-clss${srcdb}'

Anyways, we can look at the html and see which srcdb values correspond 
to which semester/season.

|srcdb|semester|
|-----|--------|
|202620|Spring 2026|
|202618|Winter 2025-26|
|202600|Summer 2025|
|202610|Fall 2025|

And presumably this 2026 prefix corresponds to the school year,
and Summer 2026 would be 202700.