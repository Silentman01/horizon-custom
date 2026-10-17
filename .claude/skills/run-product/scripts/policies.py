#!/usr/bin/env python3
"""policies.py - clone a competitor's Shopify policies 1:1 for our brand, then push them.

Subcommands (Python 3.10+, stdlib only; run with -I):

  fetch      download every policy page the competitor publishes
    python -I policies.py fetch --site https://plaims.com --out DIR [--html extra.html ...]
      Discovers /policies/<handle> links in the given HTML files (home/product captures) and always
      tries the standard handles. Writes <handle>.raw.html (page), <handle>.source.html (policy body
      only) and policies.json (handle, title, url, status).

  transform  rewrite them for our brand (1:1 text, only identity swapped, private info removed)
    python -I policies.py transform --in DIR --out DIR --brand-from Plaims --brand-to Noxis
           --domain-from plaims.com --domain-to noxis.com --email-to support@noxis.com
           [--alias-from "Plaims Co"] [--keep-date | --date "October 14, 2026"]
      * every email -> --email-to; competitor domain (incl. www., https://, myshopify) -> --domain-to
      * brand name in every casing (Plaims / PLAIMS / plaims / Plaims') -> ours, keeping the casing
      * REMOVES: postal/physical addresses, phone numbers, company/VAT/EIN/registration numbers,
        legal entity names other than the brand, and paragraphs/lines that only carried them
      * writes <handle>.html (clean body HTML ready for Shopify), REVIEW.md (every change, every
        removal, leftovers check) and transform.json
      Text is otherwise kept word for word. ALWAYS read REVIEW.md: removal is pattern-based.

  push       publish them to the store's Settings > Policies (Admin GraphQL shopPolicyUpdate)
    python -I policies.py push --in DIR --store mystore.myshopify.com [--dry-run] [--api 2025-07]
      Needs SHOPIFY_ADMIN_TOKEN (Admin API access token of a custom app with the
      write_legal_policies scope; Settings > Apps > Develop apps). Theme pushes cannot set policies.
"""
import argparse, html, json, os, re, subprocess, sys, urllib.error, urllib.request
from datetime import date
from html.parser import HTMLParser

sys.stdout.reconfigure(encoding="utf-8")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128 Safari/537.36"
STANDARD = ["refund-policy", "privacy-policy", "terms-of-service", "shipping-policy",
            "contact-information", "legal-notice", "subscription-policy", "terms-of-sale"]
TYPES = {"refund-policy": "REFUND_POLICY", "privacy-policy": "PRIVACY_POLICY",
         "terms-of-service": "TERMS_OF_SERVICE", "shipping-policy": "SHIPPING_POLICY",
         "contact-information": "CONTACT_INFORMATION", "legal-notice": "LEGAL_NOTICE",
         "subscription-policy": "SUBSCRIPTION_POLICY", "terms-of-sale": "TERMS_OF_SALE"}


def get(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        try:  # certificate-store problems on some Windows machines
            out = subprocess.run(["curl", "-sL", "-A", UA, "-w", "\n%{http_code}", url],
                                 capture_output=True, text=True, encoding="utf-8", timeout=timeout)
            body, _, code = out.stdout.rpartition("\n")
            return int(code or 0), body
        except Exception:
            return 0, ""


class BodyExtractor(HTMLParser):
    """Return the inner HTML of <div class="shopify-policy__body"> (depth-aware)."""
    VOID = {"br", "img", "hr", "input", "meta", "link", "wbr", "source", "col", "area", "base", "embed"}

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.depth, self.out, self.done, self.title, self._in_title = 0, [], False, "", False

    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get("class") or ""
        if "shopify-policy__title" in cls:
            self._in_title = True
        if self.done:
            return
        if self.depth == 0 and tag == "div" and "shopify-policy__body" in cls:
            self.depth = 1
            return
        if self.depth:
            if tag in ("script", "style"):
                self.depth += 1000  # skip embedded junk wholesale
            elif tag not in self.VOID:
                self.depth += 1
            if self.depth < 1000:
                self.out.append(self.get_starttag_text())

    def handle_startendtag(self, tag, attrs):
        if self.depth and self.depth < 1000:
            self.out.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        if self._in_title and tag in ("h1", "h2", "div"):
            self._in_title = False
        if not self.depth or self.done:
            return
        if tag in ("script", "style") and self.depth >= 1000:
            self.depth -= 1000
            return
        if self.depth >= 1000 or tag in self.VOID:
            return
        self.depth -= 1
        if self.depth == 0:
            self.done = True
        else:
            self.out.append(f"</{tag}>")

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self.depth and self.depth < 1000:
            self.out.append(data)

    def handle_entityref(self, name):
        if self.depth and self.depth < 1000:
            self.out.append(f"&{name};")

    def handle_charref(self, name):
        if self.depth and self.depth < 1000:
            self.out.append(f"&#{name};")


def extract(page):
    p = BodyExtractor()
    p.feed(page)
    body = "".join(p.out).strip()
    body = re.sub(r"<(\w+)(\s[^>]*)?\sclass=\"[^\"]*\"", r"<\1\2", body)  # drop theme classes
    return html.unescape(p.title).strip(), body


# ---------------------------------------------------------------------------- fetch
def cmd_fetch(a):
    os.makedirs(a.out, exist_ok=True)
    site = a.site.rstrip("/")
    if not site.startswith("http"):
        site = "https://" + site
    handles = list(STANDARD)
    for f in a.html or []:
        try:
            txt = open(f, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for h in re.findall(r"/policies/([a-z0-9-]+)", txt):
            if h not in handles:
                handles.append(h)
    status, home = get(site + "/")
    for h in re.findall(r"/policies/([a-z0-9-]+)", home):
        if h not in handles:
            handles.append(h)
    rows = []
    for h in handles:
        url = f"{site}/policies/{h}"
        code, page = get(url)
        row = {"handle": h, "url": url, "status": code, "title": "", "chars": 0}
        if code == 200 and "shopify-policy__body" in page:
            title, body = extract(page)
            open(os.path.join(a.out, f"{h}.raw.html"), "w", encoding="utf-8").write(page)
            open(os.path.join(a.out, f"{h}.source.html"), "w", encoding="utf-8").write(body)
            text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)).strip()
            row.update(title=title, chars=len(text))
        rows.append(row)
        print(f"{h:22} {code:>3}  {row['title'] or '-':28} {row['chars']} chars")
    json.dump(rows, open(os.path.join(a.out, "policies.json"), "w", encoding="utf-8"), indent=1)
    found = [r for r in rows if r["chars"]]
    print(f"== {len(found)} policies saved to {a.out}")
    if not found:
        sys.exit("no policy found (site blocks bots? save the pages from a browser and pass them as --html)")


# ---------------------------------------------------------------------------- transform
STREET = (r"\b\d{1,6}[A-Za-z]?\s+(?:[NSEW]\.?\s+)?(?:[A-Z0-9][\w'.-]*\s+){0,4}"
          r"(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard|Dr|Drive|Ln|Lane|Way|Ct|Court|Pl|Place|Pkwy|Parkway|"
          r"Hwy|Highway|Sq|Square|Ter|Terrace|Cir|Circle|Rue|Avenue|Strasse|Straße|Calle|Via|Weg)\b\.?"
          r"(?:[,\s]+(?:Ste|Suite|Unit|Apt|Fl|Floor|#)\s*[\w-]+)?")
ZIP = r"\b[A-Z]{2}\s+\d{5}(?:-\d{4})?\b|\b\d{5}(?:-\d{4})?(?=,?\s+(?:United States|USA|US)\b)|\b[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}\b"
PHONE = r"(?<![\w/])(?:\+?\d{1,3}[\s.-]?)?(?:\(\d{2,4}\)[\s.-]?)?\d{2,4}[\s.-]\d{2,4}[\s.-]\d{2,4}(?:[\s.-]\d{2,4})?(?![\w/])"
REG = (r"\b(?:EIN|VAT(?:\s*(?:No|Number|ID))?|SIRET|SIREN|RCS|TVA|Company\s*(?:No|Number|Reg(?:istration)?\.?\s*(?:No|Number)?)|"
       r"Registration\s*(?:No|Number)|Reg\.\s*No|ABN|ACN|UTR|Tax\s*ID)\s*[:#]?\s*[A-Z]{0,4}[\d][\d\s-]{4,}\b")
ENTITY = r"\b(?:[A-Z][\w&'.-]*\s+){1,4}(?:LLC|L\.L\.C\.|Inc\.?|Ltd\.?|Limited|LLP|GmbH|S\.?A\.?S\.?|SARL|S\.?L\.?|B\.V\.|Pty\s+Ltd|Corp\.?|Co\.,?\s+Ltd\.?)"
ADDR_LABEL = r"(?:physical|business|registered|mailing|postal|return|company|office|street)\s+address\s*:?"


def case_like(word, template):
    if template.isupper():
        return word.upper()
    if template.islower():
        return word.lower()
    if template[:1].isupper():
        return word[:1].upper() + word[1:]
    return word


def cmd_transform(a):
    meta = json.load(open(os.path.join(a.inp, "policies.json"), encoding="utf-8"))
    os.makedirs(a.out, exist_ok=True)
    df = re.escape(a.domain_from.lower().replace("https://", "").replace("www.", "").strip("/"))
    brands = [a.brand_from] + (a.alias_from or [])
    report, summary = ["# Policies transform — review\n",
                       f"Brand {a.brand_from} → {a.brand_to} · domain {a.domain_from} → {a.domain_to} · email → {a.email_to}\n",
                       "Read every REMOVED line: removal is pattern-based. Text is otherwise 1:1.\n"], []
    for row in meta:
        if not row.get("chars"):
            continue
        h = row["handle"]
        body = open(os.path.join(a.inp, f"{h}.source.html"), encoding="utf-8").read()
        changes, removed = [], []

        def sub(pattern, repl, label, text, flags=0):
            def r(m):
                new = repl(m) if callable(repl) else repl
                changes.append(f"{label}: `{m.group(0)}` → `{new}`")
                return new
            return re.sub(pattern, r, text, flags=flags)

        body = sub(r"mailto:[\w.+-]+@[\w-]+(?:\.[\w-]+)+", f"mailto:{a.email_to}", "email link", body)
        body = sub(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b", a.email_to, "email", body)
        body = sub(rf"(?:https?://)?(?:www\.)?{df}(?=[/\"'\s<).,]|$)", a.domain_to, "domain", body, re.I)
        body = sub(r"\b[\w-]+\.myshopify\.com\b", a.domain_to, "myshopify domain", body, re.I)
        for b in brands:
            body = sub(rf"\b{re.escape(b)}\b", lambda m: case_like(a.brand_to, m.group(0)), "brand", body, re.I)

        # private information: remove whole lines/blocks that carry it, then stray fragments
        blocks = re.split(r"(<(?:p|li|div|h\d|tr)[^>]*>.*?</(?:p|li|div|h\d|tr)>|<br\s*/?>)", body, flags=re.S | re.I)
        kept = []
        for blk in blocks:
            plain = html.unescape(re.sub(r"<[^>]+>", " ", blk))
            hit = None
            for name, pat, fl in (("address", ADDR_LABEL, re.I), ("street address", STREET, 0), ("zip/postcode", ZIP, 0),
                                  ("registration number", REG, re.I)):
                if re.search(pat, plain, fl):
                    hit = name
                    break
            if hit:
                # keep the block if the private bit is only a fragment of a long sentence; cut the fragment
                frag_pats = [STREET, ZIP, REG] if hit != "address" else [ADDR_LABEL + r".*"]
                if len(plain.split()) > 40 and hit != "address":
                    new = blk
                    for fp in frag_pats:
                        new = re.sub(fp, "", new, flags=re.I if fp is REG else 0)
                    removed.append(f"{hit} (fragment cut): `{plain.strip()[:160]}`")
                    kept.append(new)
                else:
                    removed.append(f"{hit} (block removed): `{plain.strip()[:160]}`")
                continue
            kept.append(blk)
        body = "".join(kept)

        def cut(pattern, label, flags=0):
            nonlocal body
            for m in re.finditer(pattern, html.unescape(re.sub(r"<[^>]+>", " ", body)), flags):
                removed.append(f"{label}: `{m.group(0).strip()}`")
            body = re.sub(pattern, "", body, flags=flags)

        cut(PHONE, "phone number")
        ents = [m.group(0) for m in re.finditer(ENTITY, html.unescape(re.sub(r"<[^>]+>", " ", body)))]
        for e in set(ents):
            if a.brand_to.lower() in e.lower():
                continue
            body = body.replace(e, a.brand_to)
            changes.append(f"legal entity: `{e}` → `{a.brand_to}`")

        if a.date:
            body = sub(r"(Last\s+updated\s*:?\s*)([A-Z][a-z]+\s+\d{1,2},\s+\d{4}|\d{1,2}\s+[A-Z][a-z]+\s+\d{4}|\d{4}-\d{2}-\d{2})",
                       lambda m: m.group(1) + a.date, "date", body, re.I)

        body = re.sub(r"<(p|li|div|h\d)[^>]*>\s*(?:&nbsp;|\s|<br\s*/?>)*</\1>", "", body)
        body = re.sub(r"(?:<br\s*/?>\s*){3,}", "<br><br>", body).strip()
        plain = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", body))).strip()
        if h == "contact-information" and len(plain) < 10 and a.email_to:
            body = f"<p>Email: <a href=\"mailto:{a.email_to}\">{a.email_to}</a></p>"
            changes.append("contact page was empty after removing private info → only our email kept")
            plain = f"Email: {a.email_to}"

        leftovers = []
        for b in brands:
            if re.search(rf"\b{re.escape(b)}\b", plain, re.I):
                leftovers.append(f"brand `{b}`")
        if re.search(df, plain, re.I):
            leftovers.append(f"domain `{a.domain_from}`")
        for m in re.finditer(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b", plain):
            if m.group(0).lower() != a.email_to.lower():
                leftovers.append(f"email `{m.group(0)}`")

        open(os.path.join(a.out, f"{h}.html"), "w", encoding="utf-8").write(body + "\n")
        title = row.get("title") or h.replace("-", " ").title()
        report.append(f"\n## {title} (`{h}`) — {len(plain.split())} words\n")
        report.append("**Replaced:**\n" + ("\n".join(f"- {c}" for c in changes) or "- none") + "\n")
        report.append("**REMOVED (private info):**\n" + ("\n".join(f"- {r}" for r in removed) or "- none") + "\n")
        report.append("**Leftovers check:** " + (", ".join(leftovers) if leftovers else "clean") + "\n")
        summary.append({"handle": h, "title": title, "type": TYPES.get(h), "file": f"{h}.html",
                        "replaced": len(changes), "removed": len(removed), "leftovers": leftovers})
        print(f"{h:22} replaced {len(changes):3}  removed {len(removed):2}  leftovers: {', '.join(leftovers) or 'none'}")
    open(os.path.join(a.out, "REVIEW.md"), "w", encoding="utf-8").write("\n".join(report))
    json.dump(summary, open(os.path.join(a.out, "transform.json"), "w", encoding="utf-8"), indent=1)
    print(f"== wrote {len(summary)} policies + REVIEW.md to {a.out}")
    if any(s["leftovers"] for s in summary):
        sys.exit("leftover competitor identity found - fix before pushing (see REVIEW.md)")


# ---------------------------------------------------------------------------- push
MUTATION = """mutation shopPolicyUpdate($shopPolicy: ShopPolicyInput!) {
  shopPolicyUpdate(shopPolicy: $shopPolicy) { shopPolicy { id type url } userErrors { field message } }
}"""


def cmd_push(a):
    summary = json.load(open(os.path.join(a.inp, "transform.json"), encoding="utf-8"))
    token = os.environ.get("SHOPIFY_ADMIN_TOKEN")
    if not token and not a.dry_run:
        sys.exit("SHOPIFY_ADMIN_TOKEN is not set (custom app Admin API token with write_legal_policies). "
                 "Without it: paste each <handle>.html into Settings > Policies.")
    endpoint = f"https://{a.store}/admin/api/{a.api}/graphql.json"
    failed = 0
    for s in summary:
        if not s.get("type"):
            print(f"{s['handle']:22} skipped (no Shopify policy type; create it as a page instead)")
            continue
        if s.get("leftovers"):
            print(f"{s['handle']:22} REFUSED: leftovers {s['leftovers']}")
            failed += 1
            continue
        body = open(os.path.join(a.inp, s["file"]), encoding="utf-8").read()
        if a.dry_run:
            print(f"{s['handle']:22} dry-run -> {s['type']} ({len(body)} chars)")
            continue
        payload = json.dumps({"query": MUTATION, "variables": {"shopPolicy": {"type": s["type"], "body": body}}}).encode()
        req = urllib.request.Request(endpoint, data=payload, method="POST", headers={
            "Content-Type": "application/json", "X-Shopify-Access-Token": token})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                res = json.loads(r.read())
        except urllib.error.HTTPError as e:
            print(f"{s['handle']:22} HTTP {e.code}: {e.read()[:300]!r}")
            failed += 1
            continue
        errs = (res.get("errors") or []) + (((res.get("data") or {}).get("shopPolicyUpdate") or {}).get("userErrors") or [])
        if errs:
            print(f"{s['handle']:22} ERROR {errs}")
            failed += 1
        else:
            pol = res["data"]["shopPolicyUpdate"]["shopPolicy"]
            print(f"{s['handle']:22} pushed -> {pol.get('url')}")
    if failed:
        sys.exit(f"{failed} policy push(es) failed")


def main():
    ap = argparse.ArgumentParser(description="Clone competitor Shopify policies for our brand and push them.")
    sp = ap.add_subparsers(dest="cmd", required=True)
    f = sp.add_parser("fetch")
    f.add_argument("--site", required=True)
    f.add_argument("--out", required=True)
    f.add_argument("--html", nargs="*", help="captured pages to scan for /policies/ links")
    t = sp.add_parser("transform")
    t.add_argument("--in", dest="inp", required=True)
    t.add_argument("--out", required=True)
    t.add_argument("--brand-from", required=True)
    t.add_argument("--alias-from", action="append", help="other competitor names (legal name, old name)")
    t.add_argument("--brand-to", required=True)
    t.add_argument("--domain-from", required=True)
    t.add_argument("--domain-to", required=True)
    t.add_argument("--email-to", required=True)
    g = t.add_mutually_exclusive_group()
    g.add_argument("--keep-date", action="store_true", help="keep the competitor's 'Last updated' date (default)")
    g.add_argument("--date", help="replace 'Last updated' dates with this text")
    p = sp.add_parser("push")
    p.add_argument("--in", dest="inp", required=True)
    p.add_argument("--store", required=True)
    p.add_argument("--api", default="2025-07")
    p.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    {"fetch": cmd_fetch, "transform": cmd_transform, "push": cmd_push}[a.cmd](a)


if __name__ == "__main__":
    main()
