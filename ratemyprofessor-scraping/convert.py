#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse, json, sqlite3
from typing import Any, Dict, List

# ---------- type helpers ----------

def infer_type(v: Any) -> str:
    if isinstance(v, bool):  return "INTEGER"
    if isinstance(v, int):   return "INTEGER"
    if isinstance(v, float): return "REAL"
    if isinstance(v, (list, dict)) or v is None:
        return "TEXT"  # store lists/dicts as JSON strings; None stays NULL (TEXT ok)
    return "TEXT"

def merge_type(t1: str, t2: str) -> str:
    if t1 == t2: return t1
    if "TEXT" in (t1, t2): return "TEXT"
    if {"INTEGER","REAL"} == {t1, t2}: return "REAL"
    return "TEXT"

def collect_schema(rows: List[Dict[str, Any]]) -> Dict[str, str]:
    schema: Dict[str, str] = {}
    for r in rows:
        for k, v in r.items():
            t = infer_type(v)
            schema[k] = merge_type(schema[k], t) if k in schema else t
    return schema

def coerce_sql_value(v: Any):
    # Make values safe for sqlite bindings
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (list, dict)):
        return json.dumps(v, ensure_ascii=False)
    return v  # ints, floats, str, None are fine

# ---------- data shaping ----------

def to_rows(items: List[Dict[str, Any]], review_key: str) -> tuple[List[dict], List[dict]]:
    prof_rows: List[Dict[str, Any]] = []
    review_rows: List[Dict[str, Any]] = []
    for it in items:
        if not isinstance(it, dict):
            continue
        reviews = it.get(review_key, []) if review_key in it and isinstance(it[review_key], list) else []
        root = {k: v for k, v in it.items() if k != review_key}
        prof_rows.append(root)
        for rv in reviews:
            if isinstance(rv, dict):
                review_rows.append(rv)
            else:
                review_rows.append({"comment": str(rv)})
    return prof_rows, review_rows

# ---------- DDL helpers ----------

def create_prof_table(cur: sqlite3.Cursor, schema: Dict[str, str]):
    cols = []
    for k, t in schema.items():
        if k == "profile_url":
            cols.append(f'"{k}" {t} UNIQUE')
        else:
            cols.append(f'"{k}" {t}')
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS professors (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          {", ".join(cols)}
        )
    """)
    if "name" in schema:
        cur.execute('CREATE INDEX IF NOT EXISTS idx_prof_name ON professors(name)')
    if "department" in schema:
        cur.execute('CREATE INDEX IF NOT EXISTS idx_prof_dept ON professors(department)')

def create_review_table(cur: sqlite3.Cursor, schema: Dict[str, str]):
    cols = [f'"{k}" {t}' for k, t in schema.items()]
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS reviews (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          professor_id INTEGER NOT NULL,
          {", ".join(cols)},
          FOREIGN KEY(professor_id) REFERENCES professors(id)
        )
    """)
    if "course" in schema:
        cur.execute('CREATE INDEX IF NOT EXISTS idx_rev_course ON reviews(course)')
    if "date" in schema:
        cur.execute('CREATE INDEX IF NOT EXISTS idx_rev_date ON reviews(date)')

# ---------- insert helper ----------

def insert_many(cur: sqlite3.Cursor, table: str, rows: List[Dict[str, Any]]) -> List[int]:
    if not rows:
        return []
    cols: List[str] = sorted({c for r in rows for c in r.keys()})
    placeholders = ", ".join(["?"] * len(cols))
    col_sql = ", ".join(f'"{c}"' for c in cols)
    sql = f'INSERT OR IGNORE INTO {table} ({col_sql}) VALUES ({placeholders})'
    ids: List[int] = []
    for r in rows:
        vals = [coerce_sql_value(r.get(c)) for c in cols]
        cur.execute(sql, vals)
        ids.append(cur.lastrowid)
    return ids

# ---------- main ----------

def main():
    p = argparse.ArgumentParser(description="Convert professor JSON (with reviews) → SQLite")
    p.add_argument("--in", dest="inp", required=True, help="Input JSON file")
    p.add_argument("--out", dest="out", default="professors.sqlite", help="Output SQLite file")
    p.add_argument("--review-key", dest="review_key", default="reviews",
                   help="Name of the array field that contains reviews (default: reviews)")
    args = p.parse_args()

    with open(args.inp, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        # If top-level is an object, pick the first list value
        items = next((v for v in data.values() if isinstance(v, list)), [])
    elif isinstance(data, list):
        items = data
    else:
        raise SystemExit("Unsupported JSON shape: top-level must be a list or an object containing a list.")

    prof_rows, review_rows = to_rows(items, args.review_key)

    prof_schema   = collect_schema(prof_rows)   or {"profile_url": "TEXT", "name": "TEXT"}
    review_schema = collect_schema(review_rows) or {"comment": "TEXT", "quality": "REAL"}

    conn = sqlite3.connect(args.out)
    cur = conn.cursor()

    create_prof_table(cur, prof_schema)
    create_review_table(cur, review_schema)

    prof_ids: List[int] = []
    if prof_rows:
        prof_ids = insert_many(cur, "professors", prof_rows)
    else:
        conn.commit(); conn.close()
        print("No professor rows found. Done.")
        return

    # Rebuild positional mapping to link reviews to the right professor
    expanded_reviews: List[Dict[str, Any]] = []
    prof_idx = -1
    for it in items:
        if not isinstance(it, dict):
            continue
        prof_idx += 1
        rvs = it.get(args.review_key, [])
        if not isinstance(rvs, list):
            continue
        for rv in rvs:
            row = dict(rv) if isinstance(rv, dict) else {"comment": str(rv)}
            row["professor_id"] = prof_ids[prof_idx]
            expanded_reviews.append(row)

    if expanded_reviews:
        insert_many(cur, "reviews", expanded_reviews)

    conn.commit()
    conn.close()
    print(f"Imported {len(prof_rows)} professors and {len(expanded_reviews)} reviews into {args.out}")

if __name__ == "__main__":
    main()
