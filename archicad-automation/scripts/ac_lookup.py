#!/usr/bin/env python3
"""Look things up before writing Archicad automation: Tapir commands, Archicad API limits and the
official Graphisoft Archicad Help of the version and language in use.

    python ac_lookup.py cmd <name|regex> [--tapir 2.0.0]     schema, "since", verified notes
    python ac_lookup.py find <words> [--tapir 2.0.0]         commands whose name/description match
    python ac_lookup.py limits <words>                        rows of Tapir's "API limits" page
    python ac_lookup.py help <words> --ac 28 [--lang GER] [-n 5] [--full]
                                                             best Help pages (title, link, excerpt)
    python ac_lookup.py build-help --ac 28 [--lang GER]       (re)build the local Help index
    python ac_lookup.py sources [--tapir 2.0.0]              refresh commands.json / limits for a release

Data lives OUTSIDE the skill folder (Graphisoft Help text is copyrighted - never commit it):
    $AC_LOOKUP_DATA, default ~/.cache/archicad-lookup/
Standard library only.
"""
import argparse
import html
import json
import os
import re
import sqlite3
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

DATA = Path(os.environ.get("AC_LOOKUP_DATA", Path.home() / ".cache" / "archicad-lookup"))
SKILL = Path(__file__).resolve().parent.parent
VERIFIED = SKILL / "references" / "tapir-verified-command-schemas.md"
TAPIR_RAW = "https://raw.githubusercontent.com/ENZYME-APD/tapir-archicad-automation/{ref}/docs/{file}"
HELP = "https://help.graphisoft.com/AC/{ac}/{lang}"
UA = {"User-Agent": "archicad-lookup/1.0 (+https://github.com/weltmaister/archicad-agent-skills)"}


def fetch(url: str, timeout: int = 30) -> bytes:
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                return r.read()
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))
    return b""


# --- Tapir commands ---------------------------------------------------------------------------

def tapir_dir(tag: str) -> Path:
    return DATA / "tapir" / tag


def ensure_tapir(tag: str) -> Path:
    d = tapir_dir(tag)
    if not (d / "commands.json").exists():
        d.mkdir(parents=True, exist_ok=True)
        ref = "main" if tag == "main" else tag
        for f in ("commands.json", "limits/index.md"):
            (d / f.replace("/", "_")).write_bytes(fetch(TAPIR_RAW.format(ref=ref, file=f), 120))
    return d


def commands(tag: str) -> list[dict]:
    d = json.loads((ensure_tapir(tag) / "commands.json").read_text(encoding="utf-8"))
    return d["commands"] if isinstance(d, dict) else d


def verified_notes(name: str) -> list[str]:
    if not VERIFIED.exists():
        return []
    out, text = [], VERIFIED.read_text(encoding="utf-8")
    for para in re.split(r"\n\s*\n", text):
        if re.search(rf"\b{re.escape(name)}\b", para):
            out.append(para.strip())
    return out


def schema_summary(s: dict | None, indent: str = "  ", depth: int = 0) -> list[str]:
    if not s or depth > 3:
        return []
    lines, req = [], set(s.get("required", []))
    for k, v in (s.get("properties") or {}).items():
        t = v.get("type") or (v.get("$ref", "").split("/")[-1]) or ("oneOf" if "oneOf" in v else "?")
        if t == "array":
            it = v.get("items", {})
            t = f"array<{it.get('type') or it.get('$ref', '').split('/')[-1] or '?'}>"
        desc = (v.get("description") or "").split(". ")[0][:110]
        lines.append(f"{indent}{k}{'*' if k in req else ''}: {t}  {desc}")
        if v.get("type") == "array" and isinstance(v.get("items"), dict) and v["items"].get("properties"):
            lines += schema_summary(v["items"], indent + "    ", depth + 1)
    return lines


def cmd_cmd(a):
    rx = re.compile(a.query, re.I)
    hits = [c for c in commands(a.tapir) if rx.fullmatch(c["name"])] or [c for c in commands(a.tapir) if rx.search(c["name"])]
    if not hits:
        sys.exit(f"no command matches {a.query!r} in Tapir {a.tapir}")
    for c in hits[:5 if len(hits) > 1 else 1]:
        print(f"## {c['name']}  (group {c.get('group')}, since Tapir {c.get('version')})  {c.get('docsUrl', '')}")
        print(c.get("description", "").strip())
        print("input (* = required):"); print("\n".join(schema_summary(c.get("inputSchema"))) or "  (none)")
        print("output:"); print("\n".join(schema_summary(c.get("outputSchema"))) or "  (none)")
        if a.full:
            print(json.dumps({"input": c.get("inputSchema"), "output": c.get("outputSchema")}, indent=1)[:6000])
        notes = verified_notes(c["name"])
        if notes:
            print(f"verified notes ({VERIFIED.name}):")
            for n in notes[:6]:
                print("  > " + n.replace("\n", "\n    ")[:900])
        print()
    if len(hits) > 5:
        print(f"... {len(hits) - 5} more: " + ", ".join(c["name"] for c in hits[5:40]))


def cmd_find(a):
    words = [w.lower() for w in a.query.split()]
    scored = []
    for c in commands(a.tapir):
        hay = (c["name"] + " " + c.get("group", "") + " " + c.get("description", "")).lower()
        s = sum(hay.count(w) + 5 * c["name"].lower().count(w) for w in words)
        if all(w in hay for w in words):
            scored.append((s, c))
    for s, c in sorted(scored, key=lambda x: -x[0])[: a.n * 4]:
        print(f"{c['name']:<42} {c.get('version', ''):<7} {c.get('description', '').split('. ')[0][:110]}")


def cmd_limits(a):
    text = (ensure_tapir(a.tapir) / "limits_index.md").read_text(encoding="utf-8")
    words = [w.lower() for w in a.query.split()]
    rows = [r for r in text.splitlines() if r.startswith("|") and all(w in r.lower() for w in words)]
    print("\n".join(rows) if rows else "no row matches - the Archicad API page lists only known gaps; check the command catalog")


# --- Graphisoft Help --------------------------------------------------------------------------

def help_db(ac: str, lang: str) -> Path:
    return DATA / "help" / f"AC{ac}_{lang}.sqlite"


def page_text(raw: str) -> tuple[str, str]:
    title = html.unescape((re.search(r"<title>(.*?)</title>", raw, re.S) or [None, ""])[1]).strip()
    body = (re.search(r"<body.*?</body>", raw, re.S) or [raw])[0]
    body = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", " ", body, flags=re.S)
    body = re.sub(r"<(br|p|li|h\d|tr|div)[^>]*>", "\n", body)
    text = html.unescape(re.sub(r"<[^>]+>", " ", body))
    text = re.sub(r"Copyright ©.*$", "", text, flags=re.S)
    text = re.sub(r"[ \t\r\f]+", " ", text)
    return title, re.sub(r"\n\s*\n+", "\n", text).strip()


def toc_paths(base: str) -> dict[str, str]:
    """url -> breadcrumb from the RoboHelp table of contents (books toc<N>.new.js)."""
    crumbs: dict[str, str] = {}

    def load(key: str, trail: str, seen: set):
        if key in seen:
            return
        seen.add(key)
        try:
            js = fetch(f"{base}/whxdata/{key}.new.js").decode("utf-8", "replace")
        except Exception:
            return
        m = re.search(r"var toc\s*=\s*(\[.*?\]);", js, re.S)
        if not m:
            return
        for it in json.loads(m.group(1)):
            name = it.get("name", "")
            if it.get("url"):
                crumbs.setdefault(it["url"].split("#")[0], f"{trail} > {name}".strip(" >"))
            if it.get("type") == "book" and it.get("key"):
                load(it["key"], f"{trail} > {name}".strip(" >"), seen)

    load("toc", "", set())
    return crumbs


def cmd_build_help(a):
    base = HELP.format(ac=a.ac, lang=a.lang)
    locs = re.findall(r"<loc>([^<]+)</loc>", fetch(f"{base}/sitemap.xml", 60).decode("utf-8", "replace"))
    locs = [l.lstrip("/") for l in locs if l.endswith(".htm")]
    print(f"AC{a.ac} {a.lang}: {len(locs)} pages, reading the table of contents ...", flush=True)
    crumbs = toc_paths(base)
    db = help_db(a.ac, a.lang); db.parent.mkdir(parents=True, exist_ok=True)
    tmp = db.with_suffix(".tmp"); tmp.unlink(missing_ok=True)
    con = sqlite3.connect(tmp)
    con.execute("create virtual table pages using fts5(title, path, body, url unindexed, tokenize='unicode61 remove_diacritics 2')")

    def get(loc):
        try:
            return loc, fetch(f"{base}/{loc}").decode("utf-8", "replace")
        except Exception as e:
            return loc, None

    done = 0
    with ThreadPoolExecutor(max_workers=6) as ex:
        for loc, raw in ex.map(get, locs):
            done += 1
            if raw:
                title, text = page_text(raw)
                con.execute("insert into pages values (?,?,?,?)", (title, crumbs.get(loc, ""), text, f"{base}/{loc}"))
            if done % 200 == 0:
                print(f"  {done}/{len(locs)}", flush=True)
    con.execute("create table meta(k, v)")
    con.executemany("insert into meta values (?,?)", [("source", base), ("built", time.strftime("%Y-%m-%d")), ("pages", str(len(locs)))])
    con.commit(); con.close(); tmp.replace(db)
    print(f"index: {db}")


def cmd_help(a):
    db = help_db(a.ac, a.lang)
    if not db.exists():
        sys.exit(f"no Help index for AC{a.ac} {a.lang} - run: ac_lookup.py build-help --ac {a.ac} --lang {a.lang}")
    con = sqlite3.connect(db)
    terms = [t for t in re.findall(r"\w+", a.query) if len(t) > 1]
    q = " OR ".join(f'"{t}"*' for t in terms) if a.any else " ".join(f'"{t}"*' for t in terms)
    rows = con.execute("select title, path, url, snippet(pages, 2, '[', ']', ' … ', 24), body from pages "
                       "where pages match ? order by bm25(pages, 20.0, 4.0, 1.0) limit ?", (q, a.n)).fetchall()
    if not rows and not a.any:
        a.any = True
        return cmd_help(a)
    built = dict(con.execute("select k, v from meta").fetchall()).get("built", "?")
    print(f"Archicad {a.ac} Help ({a.lang}, index {built}) - {len(rows)} hits for: {a.query}\n")
    for title, path, url, snip, body in rows:
        print(f"## {title}\n   {path}\n   {url}\n   {snip}")
        if a.full:
            print("\n" + body[:6000] + "\n")
        print()


def cmd_sources(a):
    d = tapir_dir(a.tapir)
    for f in ("commands.json", "limits_index.md"):
        (d / f).unlink(missing_ok=True)
    ensure_tapir(a.tapir)
    print(f"Tapir {a.tapir}: {len(commands(a.tapir))} commands in {d}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("cmd", "find", "limits"):
        s = sub.add_parser(name); s.add_argument("query"); s.add_argument("--tapir", default="2.0.0")
        s.add_argument("-n", type=int, default=10); s.add_argument("--full", action="store_true")
    for name in ("help", "build-help"):
        s = sub.add_parser(name)
        if name == "help":
            s.add_argument("query"); s.add_argument("-n", type=int, default=5)
            s.add_argument("--full", action="store_true"); s.add_argument("--any", action="store_true")
        s.add_argument("--ac", required=True); s.add_argument("--lang", default="GER")
    s = sub.add_parser("sources"); s.add_argument("--tapir", default="2.0.0")
    a = p.parse_args()
    {"cmd": cmd_cmd, "find": cmd_find, "limits": cmd_limits, "help": cmd_help,
     "build-help": cmd_build_help, "sources": cmd_sources}[a.cmd](a)


if __name__ == "__main__":
    main()
