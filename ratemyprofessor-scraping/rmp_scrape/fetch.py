#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RateMyProfessors scraper (resilient, r6)
- Supports /search/professors/{sid}?q=*&did=...
- Robust count, scrolling, and school-name extraction
- Optional per-professor review scraping (include_reviews / max_reviews)
- Accepts README-style short flags; supports text or .py config
"""

__SCRAPER_VERSION__ = "r6"

import os
import re
import sys
import json
import time
import pathlib
import importlib.util
import argparse
from dataclasses import dataclass
from typing import Optional, Dict, List

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ------------------------ Config helpers ------------------------ #

def parse_scalar(value: str):
    v = str(value).strip()
    if v.lower() in ("true", "yes", "on", "1"): return True
    if v.lower() in ("false", "no", "off", "0"): return False
    try:
        if "." in v: return float(v)
        return int(v)
    except ValueError:
        return v


def _load_py_config(path: pathlib.Path) -> Dict[str, object]:
    try:
        spec = importlib.util.spec_from_file_location("scraper_user_config", path)
        if not spec or not spec.loader:
            print(f"[WARN] Could not load python config: {path}")
            return {}
        mod = importlib.util.module_from_spec(spec)
        sys.modules["scraper_user_config"] = mod
        spec.loader.exec_module(mod)  # type: ignore
        cfg = {}
        for k in dir(mod):
            if k.startswith("_"): continue
            cfg[k] = getattr(mod, k)
        return cfg
    except Exception as e:
        print(f"[WARN] Failed to load python config {path}: {e}")
        return {}


def _load_text_config(path: pathlib.Path) -> Dict[str, object]:
    cfg: Dict[str, object] = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#") or "=" not in s: continue
                k, v = s.split("=", 1)
                cfg[k.strip()] = parse_scalar(v)
    except Exception as e:
        print(f"[WARN] Failed to load text config {path}: {e}")
    return cfg


def load_config(path: Optional[str]) -> Dict[str, object]:
    if not path:
        return {}
    p = pathlib.Path(path)
    candidates = [
        p,
        p.with_suffix(".py"),
        pathlib.Path("rmp_scrape") / p.name,
        pathlib.Path("rmp_scrape") / (p.name + ".py"),
    ]
    found = None
    for c in candidates:
        if c.exists():
            found = c
            break
    if not found:
        print(f"[WARN] Config file not found: {path}")
        return {}
    if found.suffix == ".py":
        return _load_py_config(found)
    else:
        return _load_text_config(found)


@dataclass
class CliArgs:
    testing: bool = True
    sid: Optional[int] = None
    did: Optional[int] = None
    page_reload_timeout: Optional[int] = 100
    show_more_timeout: Optional[int] = 10
    file_path: str = "all_professors.json"
    config: Optional[str] = None
    include_reviews: bool = False
    max_reviews: int = 100


def build_args() -> CliArgs:
    parser = argparse.ArgumentParser()
    parser.add_argument("-config", "--config", dest="config", type=str, default=None)
    parser.add_argument("-s", "--sid", dest="sid", type=int, default=None)
    parser.add_argument("-did", dest="did", type=int, default=None)
    parser.add_argument("-t", "--testing", dest="testing",
                        type=lambda s: str(s).lower() in ("1","true","yes","on"),
                        default=None)
    parser.add_argument("-prt", "--page_reload_timeout", dest="page_reload_timeout", type=int, default=None)
    parser.add_argument("-smt", "--show_more_timeout", dest="show_more_timeout", type=int, default=None)
    parser.add_argument("-f", "--file_path", dest="file_path", type=str, default=None)
    parser.add_argument("-ir", "--include_reviews", dest="include_reviews",
                        type=lambda s: str(s).lower() in ("1","true","yes","on"),
                        default=None)
    parser.add_argument("-mr", "--max_reviews", dest="max_reviews", type=int, default=None)
    ns = parser.parse_args()

    args = CliArgs()
    cfg = load_config(ns.config)
    for k, v in cfg.items():
        if hasattr(args, k):
            setattr(args, k, v)

    if ns.sid is not None: args.sid = ns.sid
    if ns.did is not None: args.did = ns.did
    if ns.testing is not None: args.testing = ns.testing
    if ns.page_reload_timeout is not None: args.page_reload_timeout = ns.page_reload_timeout
    if ns.show_more_timeout is not None: args.show_more_timeout = ns.show_more_timeout
    if ns.file_path is not None: args.file_path = ns.file_path
    if ns.include_reviews is not None: args.include_reviews = ns.include_reviews
    if ns.max_reviews is not None: args.max_reviews = ns.max_reviews
    args.config = ns.config
    return args


# ------------------------ Scraper ------------------------ #

class RateMyProf:
    def __init__(self, args: CliArgs):
        self.args = args
        if not args.sid:
            raise ValueError("Missing 'sid' (school ID). Provide in config or CLI (-s / --sid).")

        self.school_id: int = int(args.sid)
        self.department_id: Optional[int] = int(args.did) if args.did is not None else None

        self.url = f"https://www.ratemyprofessors.com/search/professors/{self.school_id}?q=*"
        if self.department_id is not None:
            self.url += f"&did={self.department_id}"

        chrome_opts = ChromeOptions()
        # chrome_opts.add_argument("--headless=new")  # uncomment for headless
        chrome_opts.add_argument("--no-sandbox")
        chrome_opts.add_argument("--disable-dev-shm-usage")
        chrome_opts.add_argument("--window-size=1280,1600")
        chrome_opts.add_argument("--remote-allow-origins=*")

        self.driver = webdriver.Chrome(options=chrome_opts)
        self.wait = WebDriverWait(self.driver, 20)

    # ----------------- Navigation helpers ----------------- #

    def get(self, url: str):
        self.driver.get(url)

    def _dismiss_overlays(self):
        try:
            xpaths = [
                '//button[contains(translate(.,"ACEIPT","aceipt"), "accept")]',
                '//button[contains(translate(.,"AGREE","agree"), "agree")]',
                '//button[contains(., "Accept All")]',
                '//button[contains(., "Accept")]',
                '//button[contains(., "I Agree")]',
            ]
            for xp in xpaths:
                btns = self.driver.find_elements(By.XPATH, xp)
                if btns:
                    self.driver.execute_script("arguments[0].click();", btns[0])
                    time.sleep(0.3)
                    break
        except Exception:
            pass

    def _click_show_more_if_present(self, testing: bool = False) -> bool:
        try:
            btns = self.driver.find_elements(By.XPATH, '//button[contains(., "Show More")]')
            if btns:
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btns[0])
                time.sleep(0.15)
                self.driver.execute_script("arguments[0].click();", btns[0])
                if testing: print("[expand] clicked Show More")
                return True
        except Exception as e:
            if testing: print("[expand] Show More click failed:", str(e))
        return False

    def _smart_scroll(self, pause: float = 0.35, max_tries: int = 3, testing: bool = False):
        try:
            last_h = self.driver.execute_script("return document.body.scrollHeight")
        except Exception:
            return
        if testing: print(f"[scroll] initial height={last_h}")
        for i in range(max_tries):
            self.driver.execute_script("window.scrollBy(0, Math.floor(window.innerHeight*0.9));")
            time.sleep(pause)
            try:
                new_h = self.driver.execute_script("return document.body.scrollHeight")
            except Exception:
                break
            if testing: print(f"[scroll] try={i+1} height={new_h}")
            if new_h <= last_h:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(pause)
                try:
                    new_h = self.driver.execute_script("return document.body.scrollHeight")
                except Exception:
                    break
                if new_h <= last_h:
                    break
            last_h = new_h

    def _expand_results(self, timeout_sec: int = 10, testing: bool = False):
        self._dismiss_overlays()
        start = time.time()
        stable_rounds = 0
        while time.time() - start < timeout_sec:
            cards = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/professor/"]')
            count = len(cards) if cards is not None else 0
            if testing: print(f"[expand] visible cards: {count}")

            clicked = self._click_show_more_if_present(testing=testing)
            if clicked:
                try:
                    WebDriverWait(self.driver, 8).until(
                        lambda d: len(d.find_elements(By.CSS_SELECTOR, 'a[href*="/professor/"]')) > count
                    )
                except Exception:
                    pass

            self._smart_scroll(pause=0.35, max_tries=2, testing=testing)

            new_count = len(self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/professor/"]'))
            if new_count <= count:
                stable_rounds += 1
            else:
                stable_rounds = 0

            if stable_rounds >= 3:
                if testing: print("[expand] no more growth; stopping")
                break

            time.sleep(0.25)

    # ----------------- Reviews helpers ----------------- #

    def _reviews_click_show_more(self, testing: bool = False) -> bool:
        try:
            xpaths = [
                '//button[contains(., "Show More")]',
                '//button[contains(., "Load More")]',
                '//button[contains(., "More Ratings")]',
                '//button[@aria-label="Load More"]',
            ]
            for xp in xpaths:
                btns = self.driver.find_elements(By.XPATH, xp)
                if btns:
                    self.driver.execute_script("arguments[0].scrollIntoView({block:\'center\'});", btns[0])
                    time.sleep(0.15)
                    self.driver.execute_script("arguments[0].click();", btns[0])
                    if testing: print("[reviews] clicked Show/Load More")
                    return True
        except Exception as e:
            if testing: print("[reviews] Show/Load More failed:", e)
        return False

    def _expand_reviews(self, max_wait_sec: int = 12, testing: bool = False):
        start = time.time()
        stable_rounds = 0
        while time.time() - start < max_wait_sec:
            blocks = self.driver.find_elements(
                By.XPATH,
                '//*[contains(@data-testid,"review") or contains(@class,"Review__") or contains(@class,"Rating__StyledRating")]'
            )
            count = len(blocks)
            if testing: print(f"[reviews] visible review blocks: {count}")

            clicked = self._reviews_click_show_more(testing=testing)
            self.driver.execute_script("window.scrollBy(0, Math.floor(window.innerHeight*0.9));")
            time.sleep(0.35)

            new_count = len(self.driver.find_elements(
                By.XPATH,
                '//*[contains(@data-testid,"review") or contains(@class,"Review__") or contains(@class,"Rating__StyledRating")]'
            ))
            if new_count <= count:
                stable_rounds += 1
            else:
                stable_rounds = 0

            if stable_rounds >= 3:
                if testing: print("[reviews] no more growth; stopping")
                break

    def _parse_single_review_block(self, el) -> dict:
        try:
            txt = (el.text or "").strip()
        except Exception:
            txt = ""

        review = {
            "date": None,
            "course": None,
            "quality": None,
            "difficulty": None,
            "comment": None,
            "would_take_again": None,
            "grade": None,
            "attendance": None,
            "tags": [],
        }

        # Comment
        try:
            pars = el.find_elements(By.XPATH, './/p|.//*[contains(@class,"Comments") or contains(@class,"Comment")]')
            best = ""
            for p in pars:
                t = (p.text or "").strip()
                if len(t) > len(best):
                    best = t
            if best:
                review["comment"] = best
        except Exception:
            pass
        if not review["comment"]:
            lines = [s.strip() for s in txt.splitlines() if s.strip()]
            if lines:
                review["comment"] = lines[-1]

        # Quality / Difficulty
        m = re.search(r'Quality\s*[:\-]?\s*(\d+(?:\.\d+)?)', txt, flags=re.I)
        if m:
            try: review["quality"] = float(m.group(1))
            except: pass
        m = re.search(r'Difficulty\s*[:\-]?\s*(\d+(?:\.\d+)?)', txt, flags=re.I)
        if m:
            try: review["difficulty"] = float(m.group(1))
            except: pass

        # Would take again
        m = re.search(r'Would take again\s*[:\-]?\s*(Yes|No)', txt, flags=re.I)
        if m:
            review["would_take_again"] = (m.group(1).lower() == "yes")

        # Grade
        m = re.search(r'Grade\s*[:\-]?\s*([A-F][\+\-]?)', txt, flags=re.I)
        if m:
            review["grade"] = m.group(1).upper()

        # Attendance
        m = re.search(r'Attendance\s*[:\-]?\s*([A-Za-z ]+)', txt, flags=re.I)
        if m:
            att = m.group(1).strip()
            att = re.split(r'\s{2,}|Tags?:', att)[0].strip()
            review["attendance"] = att

        # Course (e.g., CSE 131 or COMP1040)
        m = re.search(r'\b([A-Z]{2,5}\s?\d{3,4}[A-Z]?)\b', txt)
        if m:
            token = m.group(1)
            review["course"] = token if " " in token else token  # keep as seen

        # Date
        for pat in [
            r'\b([A-Za-z]{3,9}\s+\d{4})\b',
            r'\b(\d{1,2}/\d{1,2}/\d{2,4})\b',
            r'\b([A-Za-z]{3,9}\s+\d{1,2},\s*\d{4})\b'
        ]:
            m = re.search(pat, txt)
            if m:
                review["date"] = m.group(1)
                break

        # Tags (best-effort from inline text)
        tag_candidates = []
        for sep in ["·", "|", ",", "•"]:
            tag_candidates += [t.strip() for t in txt.split(sep)]
        tags = []
        for t in tag_candidates:
            tl = t.lower()
            if 2 <= len(t) <= 40 and any(k in tl for k in [
                "grader","participation","attendance","read","clear","group",
                "extra","lecture","heavy","homework","quiz","project","deadline","curve"
            ]):
                tags.append(t)
        seen = set(); cleaned = []
        for t in tags:
            if t.lower() not in seen:
                seen.add(t.lower()); cleaned.append(t)
        if cleaned:
            review["tags"] = cleaned

        return review

    def _scrape_reviews(self, max_reviews: int = 100, testing: bool = False) -> List[dict]:
        reviews: List[dict] = []
        self._expand_reviews(max_wait_sec=12, testing=testing)
        blocks = self.driver.find_elements(
            By.XPATH,
            '//*[contains(@data-testid,"review") or contains(@class,"Review__") or contains(@class,"Rating__StyledRating")]'
        )
        for el in blocks:
            try:
                r = self._parse_single_review_block(el)
                if r["comment"] or r["quality"] or r["difficulty"]:
                    reviews.append(r)
                    if len(reviews) >= max_reviews:
                        break
            except Exception:
                continue
        if testing:
            print(f"[reviews] collected {len(reviews)} review rows")
        return reviews

    # ----------------- Parsing helpers ----------------- #

    @staticmethod
    def _extract_school_from_text(txt: str) -> Optional[str]:
        if not txt: return None
        s = txt.strip()
        if "Professors at " in s:
            part = s.split("Professors at ", 1)[1].split("|", 1)[0].strip()
            if part: return part
        if " Professors" in s:
            part = s.split(" Professors", 1)[0].strip()
            if part: return part
        return s or None

    def get_school_name(self) -> str:
        try:
            og = self.driver.find_element(By.CSS_SELECTOR, 'meta[property="og:title"]')
            ogt = og.get_attribute("content") or ""
            sch = self._extract_school_from_text(ogt)
            if sch: return sch
        except Exception:
            pass
        try:
            title = self.driver.title or ""
            sch = self._extract_school_from_text(title)
            if sch: return sch
        except Exception:
            pass
        try:
            h1 = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//h1")))
            if h1 and h1.text.strip():
                sch = self._extract_school_from_text(h1.text)
                return sch or h1.text.strip()
        except Exception:
            pass
        return f"SID {self.school_id}"

    def num_professors(self, testing: bool = False) -> int:
        if testing:
            print("-----------------num_professors()-------------------")
            start = time.time()

        header_text = ""
        try:
            header_el = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//h1[@data-testid="pagination-header-main-results"]')
                )
            )
            header_text = (header_el.text or "").strip()
        except Exception:
            try:
                header_el = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((By.XPATH, "//h1"))
                )
                header_text = (header_el.text or "").strip()
            except Exception:
                header_text = ""

        num_profs: Optional[int] = None
        for pattern in [
            r'of\s+(\d+)\b',
            r'^(\d+)\s+(?:Professors|Results?)\b',
            r'\b(\d+)\b$'
        ]:
            m = re.search(pattern, header_text or "", flags=re.IGNORECASE)
            if m:
                try:
                    num_profs = int(m.group(1))
                    break
                except ValueError:
                    pass

        if num_profs is None:
            try:
                cards = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/professor/"]')
                num_profs = len(cards) if cards is not None else 0
            except Exception:
                num_profs = 0

        if testing:
            end = time.time()
            print("Header text:", header_text or "(empty)")
            print("Number of professors:", num_profs)
            print("num_professors() finished in", end - start, "seconds.")
        return int(num_profs or 0)

    # ----------------- Main scrape ----------------- #

    def scrape_professors(self, args: CliArgs) -> List[Dict[str, object]]:
        testing = bool(args.testing)
        if testing:
            print("-----------------scrape_professors()----------------")
            print("Scraping professors from RateMyProfessors.com at")
            print("URL: ", self.url)
            print("University SID: ", args.sid)

        self.get(self.url)
        time.sleep(1.0)

        self._expand_results(timeout_sec=int(args.show_more_timeout or 10), testing=testing)

        timeout_start = time.time()
        while True:
            try:
                num_profs = self.num_professors(testing)
                break
            except Exception:
                if args.page_reload_timeout is not None and (time.time() - timeout_start) >= args.page_reload_timeout:
                    if testing:
                        print("Timeout waiting for num_professors(). Proceeding with 0.")
                    num_profs = 0
                    break
                time.sleep(1.0)

        self._expand_results(timeout_sec=int(args.show_more_timeout or 10), testing=testing)

        school_name = self.get_school_name()

        cards = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/professor/"]')
        links: List[str] = []
        seen: set[str] = set()
        for a in cards:
            try:
                href = a.get_attribute("href") or ""
                if "/professor/" not in href:
                    continue
                href = href.split("?", 1)[0].rstrip("/")
                if href not in seen:
                    seen.add(href)
                    links.append(href)
            except Exception:
                continue

        if testing:
            print("-------------scrape_professors() cont.--------------")
            print(f"Found {len(links)} professor links (unique).")

        professors: List[Dict[str, object]] = []
        for i, url in enumerate(links, 1):
            prof: Dict[str, object] = {
                "school": school_name,
                "school_sid": args.sid,
                "department_id": args.did,
                "profile_url": url,
                "name": None,
                "department": None,
                "overall_rating": None,
                "num_ratings": None,
            }
            try:
                self.driver.get(url)

                # Name
                try:
                    h1 = WebDriverWait(self.driver, 10).until(
                        EC.visibility_of_element_located((By.XPATH, "//h1"))
                    )
                    nm = (h1.text or "").strip()
                    prof["name"] = nm or None
                except Exception:
                    pass

                # Overall rating
                try:
                    cand = self.driver.find_elements(
                        By.XPATH,
                        '//*[contains(@class,"RatingValue__Numerator") or contains(@data-testid,"rating") or contains(text(),"Overall Quality")]'
                    )
                    found = None
                    for el in cand:
                        txt = (el.text or "").strip()
                        m = re.search(r"\b(\d+(?:\.\d+)?)\b", txt)
                        if m:
                            found = float(m.group(1))
                            break
                    prof["overall_rating"] = found
                except Exception:
                    pass

                # Number of ratings
                try:
                    body_txt = self.driver.find_element(By.TAG_NAME, "body").text
                    m = re.search(r"\b(\d+)\s+Ratings?\b", body_txt, flags=re.IGNORECASE)
                    if m:
                        prof["num_ratings"] = int(m.group(1))
                except Exception:
                    pass

                # Department (best-effort)
                try:
                    body_txt = self.driver.find_element(By.TAG_NAME, "body").text
                except Exception:
                    body_txt = ""
                try:
                    m = re.search(r"Department\s*:?\s*([A-Za-z0-9 &/\-]+)", body_txt)
                    if m:
                        prof["department"] = m.group(1).strip()
                except Exception:
                    pass

                # Reviews (optional)
                if getattr(args, "include_reviews", False):
                    try:
                        prof["reviews"] = self._scrape_reviews(
                            max_reviews=int(getattr(args, "max_reviews", 100) or 100),
                            testing=testing
                        )
                    except Exception as e:
                        if testing: print("[reviews] error:", e)
                        prof["reviews"] = []

            except Exception:
                pass

            professors.append(prof)
            if testing and (i % 5 == 0 or i == len(links)):
                print(f"Scraped {i}/{len(links)} profiles")

        out_path = args.file_path or "all_professors.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(professors, f, ensure_ascii=False, indent=2)

        if testing:
            print(f"\nWrote {len(professors)} records to: {out_path}")

        return professors


# ------------------------ Main ------------------------ #

if __name__ == "__main__":
    print(f"[fetch.py] version={__SCRAPER_VERSION__}")
    args = build_args()
    print("----------------------TESTING-----------------------")
    print("Arguments:")
    print("sid: ", args.sid)
    print("testing: ", args.testing)
    print("page_reload_timeout: ", args.page_reload_timeout)
    print("show_more_timeout: ", args.show_more_timeout)
    print("file_path: ", args.file_path)
    print("include_reviews: ", args.include_reviews)
    print("max_reviews: ", args.max_reviews)

    scraper = RateMyProf(args)
    try:
        scraper.scrape_professors(args)
    finally:
        try:
            scraper.driver.quit()
        except Exception:
            pass
