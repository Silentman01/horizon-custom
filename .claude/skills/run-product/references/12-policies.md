# Stream F — Policies (1:1 from the competitor)

Goal: our store gets the competitor's policy pages word for word, with only the identity swapped (brand, domain, emails) and every private detail removed, then published to the store's **Settings → Policies** as part of the run.

## Contents
1. Inputs and timing
2. Where policies come from
3. Fetch
4. Transform (rules)
5. Review
6. Push
7. Pitfalls
8. Done when

---

## 1. Inputs and timing
- Competitor site root (from `COMPETITOR_URL`), BRIEF decisions: `BRAND`, our domain (`OUR_DOMAIN`, e.g. `noxis.com` or the myshopify domain until a custom domain exists) and our support email (`SUPPORT_EMAIL`). Ask for domain/email at the branding gate if unknown — never invent them.
- Push needs `STORE` and `SHOPIFY_ADMIN_TOKEN` (Admin API token of a custom app with the `write_legal_policies` scope: Settings → Apps → Develop apps → create app → Admin API scopes → install → reveal token).
- Timing: fetch in Phase 1 (no brand needed); transform right after the gate; push in Phase 5 with the theme.

## 2. Where policies come from
Shopify serves policies at `https://<competitor>/policies/<handle>`: `refund-policy`, `privacy-policy`, `terms-of-service`, `shipping-policy`, `contact-information`, `legal-notice`, `subscription-policy`, `terms-of-sale`. The footer usually links the ones that exist (Plaims: refund, privacy, terms, shipping, contact; legal-notice/subscription 404). The policy text sits in `<div class="shopify-policy__body">`. Some stores also publish extra policy-like *pages* (e.g. `/pages/returns`) — check the footer links in `capture.json`; clone those as theme pages (`templates/page.*.json` or page content) only if they exist.

## 3. Fetch
```bash
python -I scripts/policies.py fetch --site https://plaims.com --out "<PRODUCT_DIR>/06_policies/source" \
  --html "<PRODUCT_DIR>/02_competitor/page/p.html" "<PRODUCT_DIR>/02_competitor/home/p.html"
```
Writes `<handle>.raw.html`, `<handle>.source.html` (body only) and `policies.json` (status, title, size). If everything 404s or the site blocks bots, save the pages from a browser and extract from those.

## 4. Transform (rules)
```bash
python -I scripts/policies.py transform --in "<PRODUCT_DIR>/06_policies/source" --out "<PRODUCT_DIR>/06_policies" \
  --brand-from Plaims --brand-to Noxis --domain-from plaims.com --domain-to <OUR_DOMAIN> --email-to <SUPPORT_EMAIL>
```
- **1:1 text.** Keep every sentence, number, time frame and fee exactly as the competitor wrote it (return window, shipping times, fees, thresholds). Don't "improve", shorten or harmonise with our page — the operator wants their policies exactly. (If our offer contradicts theirs — e.g. free-shipping threshold $30 on our page vs $35 in their shipping policy — flag it to the operator; don't edit silently.)
- **Identity swaps:** every brand mention in any casing (`Plaims`, `PLAIMS`, `plaims`; add `--alias-from` for legal/old names), the domain (with/without `www.`/`https://`, and the competitor's `*.myshopify.com`), every email address → ours.
- **Remove private information — never put any address in:** physical/postal/registered addresses (lines labelled "Physical address", street + number, ZIP/postcodes), phone numbers, company registration/VAT/EIN/SIRET numbers, other legal-entity names (replaced by our brand), people's names. A block that only carried private info is deleted; if the contact page ends up empty, only our support email is kept.
- The "Last updated" date stays as-is by default (`--date "<text>"` to replace it when the operator asks).

## 5. Review
Read `06_policies/REVIEW.md`: every replacement, every removal, and a leftovers check (any competitor brand/domain/email left → the script exits non-zero and push refuses). Removal is pattern-based: also skim each policy for names, addresses written in unusual formats (e.g. "c/o", PO boxes, non-US formats) and remove them by hand in `<handle>.html`. Plaims result: 5 policies; contact page had only "Physical address: 30 N Gould St Ste R, Sheridan WY 82801" → removed, email only; `vhm0ai-gh.myshopify.com` → our domain; 24 brand swaps in the terms.

## 6. Push
```bash
SHOPIFY_ADMIN_TOKEN=... python -I scripts/policies.py push --in "<PRODUCT_DIR>/06_policies" --store <store>.myshopify.com
```
Uses Admin GraphQL `shopPolicyUpdate(shopPolicy: {type, body})` per policy (types REFUND_POLICY, PRIVACY_POLICY, TERMS_OF_SERVICE, SHIPPING_POLICY, CONTACT_INFORMATION, LEGAL_NOTICE, SUBSCRIPTION_POLICY, TERMS_OF_SALE). `--dry-run` first. Without a token or store: deliver the `<handle>.html` files and put "paste into Settings → Policies" in the operator to-dos (Shopify CLI theme pushes cannot set policies).

## 7. Pitfalls
- Policies are store settings, not theme files — they don't travel with the branch; each store needs its own push.
- If the store uses Shopify's *automated* privacy policy, the API update may be rejected or overridden — switch it to a custom policy in Settings → Policies, then push again.
- Inline CSS/JS from the competitor's theme can leak into the body; the extractor drops `<script>/<style>` and class attributes — check the review for stray CSS text.
- Domain unknown at launch: use the myshopify domain and re-run transform + push once the custom domain is connected.

## 8. Done when
All competitor policies exist in `06_policies/<handle>.html`, REVIEW.md shows no leftovers and no private info, and they are pushed (or listed as an operator to-do with the files ready).
