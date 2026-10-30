"""Read-only diagnostics for the Trentox Tutor app. Never prints your API key."""
import json
import os
import sqlite3
import sys
import urllib.error
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))


def read_env():
    out = {}
    path = os.path.join(BASE, ".env")
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8-sig") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


env = read_env()
print("Python:", sys.version.split()[0])
print(".env variable NAMES:", sorted(env.keys()))
for k, v in env.items():
    print(f"  {k}: value length = {len(v)}")

key = env.get("OMNIROUTE_API_KEY") or env.get("GEMINI_API_KEY") or ""
base = env.get("OMNIROUTE_BASE_URL", "http://localhost:20128/v1").rstrip("/")
print("Base URL:", base)


def redact(text):
    return text.replace(key, "***") if key else text


ids = []
print("\n=== GET /models ===")
try:
    req = urllib.request.Request(base + "/models", headers={"Authorization": "Bearer " + key})
    with urllib.request.urlopen(req, timeout=10) as r:
        body = json.loads(r.read().decode())
        ids = [m.get("id") for m in body.get("data", [])]
        print("STATUS 200, models:", len(ids))
        for i in ids[:100]:
            print("  ", i)
except urllib.error.HTTPError as e:
    print("HTTP", e.code, redact(e.read().decode(errors="replace")[:400]))
except Exception as e:
    print("CONNECT ERROR:", redact(repr(e)))

print("\n=== Chat completion test ===")
candidates = [m.strip() for m in env.get("OMNIROUTE_MODELS", "gemini-3-flash-preview,gemini-3.1-pro-preview").split(",") if m.strip()]
candidates += [i for i in ids if i and "gemini" in i.lower()][:4]
seen = set()
for model in candidates:
    if model in seen:
        continue
    seen.add(model)
    payload = json.dumps({"model": model, "messages": [{"role": "user", "content": "Say OK"}], "max_tokens": 8}).encode()
    req = urllib.request.Request(
        base + "/chat/completions",
        data=payload,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            data = json.loads(r.read().decode())
            print(f"[OK ] {model} ->", repr(data["choices"][0]["message"]["content"])[:80])
    except urllib.error.HTTPError as e:
        print(f"[ERR] {model} -> HTTP {e.code}:", redact(e.read().decode(errors="replace")[:250]))
    except Exception as e:
        print(f"[ERR] {model} ->", redact(repr(e))[:250])

print("\n=== past_papers.db ===")
db = os.path.join(BASE, "data", "databases", "past_papers.db")
if not os.path.exists(db):
    print("not found:", db)
else:
    c = sqlite3.connect(db)
    tables = [r[0] for r in c.execute("select name from sqlite_master where type='table'")]
    print("TABLES:", tables)
    for t in tables:
        cols = [r[1] for r in c.execute(f"pragma table_info({t})")]
        n = c.execute(f"select count(*) from {t}").fetchone()[0]
        print(f"  {t}: {n} rows, columns={cols}")
    for t in tables:
        cols = [r[1] for r in c.execute(f"pragma table_info({t})")]
        if "question_text" not in cols:
            continue
        print(f"\n--- subject counts in {t} ---")
        if "subject_code" in cols:
            for row in c.execute(f"select subject_code, count(*) from {t} group by subject_code"):
                print("  ", row)
        print(f"--- 6 random samples from {t} ---")
        sel = "question_number, topic_name, question_text, marking_guideline, marks"
        sel = ", ".join(x for x in [s.strip() for s in sel.split(",")] if x in cols)
        for row in c.execute(f"select {sel} from {t} where length(question_text) > 30 order by random() limit 6"):
            print("ROW:", [(repr(str(x))[:700]) for x in row])
            print()
