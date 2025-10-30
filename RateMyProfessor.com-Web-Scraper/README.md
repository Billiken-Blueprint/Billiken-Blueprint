# RateMyProfessor.com-Web-Scraper
A Python script that uses Selenium to scrape professor ratings from [RateMyProfessors.com](https://www.ratemyprofessors.com/) and saves them to a JSON file.

## Requirements
- Python 3.6+
- Selenium
- ChromeDriver

## Usage
Using the script is simple but requires the user to already have the `sid`, that is the unique school ID, of the school they want to scrape as assigned by RateMyProfessors.com. The `sid` can be found by searching for the school on RateMyProfessors.com and looking at the URL. For example, the `sid` for the University of Wisconsin-Madison is `1256` and can be found in the URL, 

```{bash}
https://www.ratemyprofessors.com/search/teachers?query=*&sid=1256
```

I want to point out that the `sid` should be a unique identifier for the university, however, I have found that some universities have multiple. For example, professors are listed for the University of Wisconsin-Madison for `sid` values of each `1256` and `18418`. I have not found any other universities with multiple IDs, but if you find one, please let me know. In the meantime have reached out to RateMyProfessors.com to see if they can clarify this issue.

You must also install ChromeDriver to your machine and specify the path of the ChromeDriver executable in the `driver_config.py` file. You can download the appropriate version for your system [here](https://chromedriver.chromium.org/downloads).

Once you have the `sid` and ChromeDriver installed, install the required dependencies and run the script with,

```{bash}
pip3 install -r requirements.txt
python3 rmp_scrape/fetch.py -s YourSID
```

### Command Line Arguments

There are a number of command line arguments that can be specified using the following flags:

#### Required Arguments
- `-s` or `--sid`: The `sid` of the school you want to scrape. 

#### Optional Arguments
- `-config` or `--config`: The config file path if you want to use a config file instead of specifying the arguments.  
- `-f` or `--file_path`: The file path to store the scraped data.
- `-prt` or `--page_reload_timeout`: The timeout for reloading the RMP page.
- `-smt` or `--show_more_timeout`: The timeout for clicking the show more button.

You have the option to run the script directly from the command line by specifying which arguments you want to use, but only the `-s` or `-sid` argument is required. If you do not specify the `-f` or `-file_path` argument, the script will save the scraped data to a file named `profs_from_YourSchoolName.json` in the project directory. 

You can also run the script from the command line passing only the `-config` argument, as long as the provided config file path is a `.py` file located within the `/rmp_scrape` directory that contains (at the minimum) a valid `sid`. For example, a user can create a file named `config.py` in the `/rmp_scrape` directory with the following arguments,

```{python}
sid = 1256  
testing = True
page_reload_timeout = 100 # 100 seconds
show_more_timeout = 10 # 10 seconds
file_path = 'all_professors.json'
```

And can then run the script from within the project directory with these configurations from the command line with,

```{bash}
python3 rmp_scrape/fetch.py -config config
```
One important thing to note is that by default any arguments that are used in the command line will override any arguments found in the config file. For example, if you are using the config file specified above, the command,

```{bash}
python3 rmp_scrape/fetch.py -config config -t False
```

Would not run the script in `testing` mode even though `testing=True` in the config file. Or for another example, running,

```{bash}
python3 rmp_scrape/fetch.py -config config -s 0001
```

will run the script for `sid = 0001` instead of `sid = 1256` as specified in the config file. This makes it easy to save default configurations with slight modifications when running from the command line.

The `-prt` or `-page_reload_timeout` and the `smt` or `show_more_timeout` arguments are options that I have added to help with the scraping process. The `page_reload_timeout` argument is used to specify how many seconds the script should spend trying to reload the page `www.ratemyprofessors.com/search/teachers?query=*&sid=YourSID`. For some reason while working on this script, I noticed that the page would sometimes not load properly. The `page_reload_timeout` argument allows the user to specify how many seconds the script should spend attempting to load the page. Whereas most of the time when you visit this page, you will see a reasonable amount of professors for a given school, like so:

![RMP_reasonable](https://user-images.githubusercontent.com/72423203/210110116-e145656f-eca9-4800-86e5-fce39f0c714d.png)

On other occasions, you will see a page that looks like this despite the fact that you are requesting the same page (even if for you are requesting this page for the first time).

![RMP_error_1](https://user-images.githubusercontent.com/72423203/210110127-ae5ae40b-70f2-4a28-b6b4-811693af2a65.png)

To combat this the `page_reload_timeout` command line argument will let you designate how many seconds you want to spend reloading the page until the correct page loads. This is not optimal, but I assume it is an issue with RateMyProfessors.com's internals and is only used so that the script is functional. For most if not all use cases, this should not be set or should be set arbitrarily high since after a few attempts to reload the page it seems to always return to a reasonable value.

It also seems RateMyProfessors.com runs into some issues when a user presses the 'Show More' button at the bottom of the professor's list for a given school (e.g. [www.ratemyprofessors.com/search/teachers?query=*&sid=1256](https://www.ratemyprofessors.com/search/teachers?query=*&sid=1256). After pressing the 'Show More' button the site will on occasion load the page with professors at a different school than the one corresponding to the given `sid`. For example, here is a screenshot of the page after accessing the professors for the University of Wisconsin-Madison and then pressing the 'Show More' button four times. As you can see, the page is now showing a professor from Grand Valley State University, and subsequent presses will show professors from other schools. 
 
![RMP_error_2](https://user-images.githubusercontent.com/72423203/210110197-f4235619-e65f-4d72-b03e-163277a7726d.png)

As a temporary fix, I have added the `show_more_timeout` argument to allow the user to specify how many seconds the script should continue pressing the 'Show More' button before the script scrapes the data from the page. The idea here is that after subsequent presses of the 'Show More' button, the page will start containing all professors from RateMyProfessors.com. Since this can be very large, the user can instead set a length of time that will result in a timeout so that the script isn't continuously pressing 'Show More' even when the professors appearing on the page may not be all from the school corresponding top the given `sid`. 

This fix is not optimal, as after the page is filled with a lot of professors, the script must perform an additional comparison on all entries to ensure that only professors that are from the school corresponding to the desired `sid` are written to the JSON file.


## Edit Made to Meet the Usage of Billiken-Blueprint Development
This fork modernizes and hardens the RateMyProfessors scraper so it works with RMP’s new UI and with department filters, and adds a simple JSON to SQLite pipeline.

ey changes (scraper: rmp_scrape/fetch.py)

New results URL format:
From the old
https://www.ratemyprofessors.com/search/teachers?query=*&sid=<SID>
➜ to the new (resilient)
https://www.ratemyprofessors.com/search/professors/<SID>?q=*&did=<DEPT_ID>

Department filter (-did) support (e.g., 11 for CS at SLU).

Resilient counting: num_professors() no longer depends on a brittle XPATH split()[0]. It parses multiple header patterns and falls back to counting visible professor cards.

Robust school-name detection: tries OpenGraph <meta property="og:title">, <title>, and <h1> as fallbacks instead of a hard-coded XPATH.

Lazy-load expansion: smooth scroll + “Show More” clicks with overlay dismissal (cookie banners) so we actually load all visible results for the page variant.

Individual Review Extraction: Each professor profile is now opened and parsed to extract every review (or however many you allow via flags).

Config file flexibility: accepts either a text KEY=VALUE file or a Python .py config, and CLI flags override config values.


New converter (convert.py)

Converts your scraped JSON (including nested reviews) into a normalized SQLite DB with two tables:

professors (one row per professor)

reviews (one row per review, with professor_id FK)

Schema-flexible: infers columns from whatever keys exist in your JSON (math, CS, etc.).

Safely stores lists/dicts (e.g., tags) as JSON strings so inserts don’t fail.

Works with any similarly structured dumps (top-level list of professors, each with a reviews array — or change --review-key).

New Requirements

Python 3.9+ recommended

Google Chrome + matching ChromeDriver (on macOS, easiest via: brew install --cask google-chrome && brew install chromedriver)

Python deps in your venv:

pip install selenium bs4


(Only Selenium is needed for the scraper; bs4 is optional. The converter uses only stdlib.)

🚀 How to run the scraper

From the project root:

Minimal (School only)
python3 rmp_scrape/fetch.py -s 850 -t true -f all_professors.json

Filter to a department (e.g., CS = did 11)
python3 rmp_scrape/fetch.py -s 850 -did 11 -t true -f cs_professors.json

Include individual reviews (cap at 120 per prof)
python3 rmp_scrape/fetch.py -s 850 -did 11 -t true -ir true -mr 120 -f cs_professors_with_reviews.json

Useful timeouts

-prt 50 → page reload timeout (sec) for the search page

-smt 10 → how long we try to “Show More”/scroll expand

Example:

python3 rmp_scrape/fetch.py -s 850 -did 11 -t true -prt 50 -smt 10 -ir true -mr 120 -f cs_professors_with_reviews.json

Using a config file

Create rmp_scrape/config.py or rmp_scrape/config (KEY=VALUE text). For example:

# rmp_scrape/config.py
sid = 850
did = 11
testing = True
page_reload_timeout = 50
show_more_timeout = 10
file_path = "cs_professors_with_reviews.json"
include_reviews = True
max_reviews = 120


Run:

python3 rmp_scrape/fetch.py -config config


Any CLI flags you pass will override config values.

🗄️ How to convert JSON → SQLite

After scraping (e.g., cs_professors_with_reviews.json):

python3 convert.py --in cs_professors_with_reviews.json --out cs.sqlite


For a different key name for reviews (future JSONs):

python3 convert.py --in some_dump.json --out dump.sqlite --review-key ratings

What you get

professors table: inferred columns such as name, school, profile_url (UNIQUE), overall_rating, num_ratings, department, etc.

reviews table: inferred columns such as course, quality, difficulty, comment, date, tags (stored as JSON string), plus professor_id FK.

Quick sanity checks
sqlite3 cs.sqlite
.tables
.schema professors
.schema reviews
SELECT COUNT(*) FROM professors;
SELECT COUNT(*) FROM reviews;

💡 Tips (macOS)

If the system sqlite3 is ancient, install a newer one:

brew install sqlite


Then the binary is at /opt/homebrew/bin/sqlite3 (Apple Silicon) or /usr/local/bin/sqlite3 (Intel).

If Chrome pops up and you prefer no UI, open fetch.py and uncomment:

# chrome_opts.add_argument("--headless=new")


If RMP intermittently shows partial results, keep -prt (page reload timeout) reasonably high (e.g., 50–100), and the scraper will retry smartly before falling back.

🧩 Output fields (example)

Each professor JSON object looks like:

{
  "school": "Saint Louis University",
  "school_sid": 850,
  "department_id": 11,
  "profile_url": "https://www.ratemyprofessors.com/professor/2999302",
  "name": "Michael Liljegren",
  "department": "Computer Science",
  "overall_rating": 4.4,
  "num_ratings": 7,
  "reviews": [
    {
      "date": "Sep 2024",
      "course": "CSE131",
      "quality": 5.0,
      "difficulty": 2.0,
      "comment": "Great prof...",
      "would_take_again": true,
      "grade": "A-",
      "attendance": "Mandatory",
      "tags": ["Clear grading criteria", "Get ready to read"]
    }
  ]
}

The converter maps this into SQLite as described above.



