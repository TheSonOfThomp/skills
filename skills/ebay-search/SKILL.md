---
name: ebay-search
description: Search eBay for current listings, refine queries and filters, compare matching items, and present concise results with price, condition, shipping, seller details, and listing links. Automatically use this skill whenever the user asks to find, browse, compare, value, or price-check items on eBay, including used, collectible, refurbished, auction, or Buy It Now listings—even if they do not name eBay explicitly but describe an item search that belongs there. Validate the official eBay Browse API connection before API-backed searches and clearly explain missing or invalid setup. Do not use for making purchases, bids, offers, messages, saved searches, or ongoing listing alerts.
inputs:
  - name: search_request
    type: text
    required: true
    description: The item sought, including any known model, condition, budget, location, or delivery constraints
outputs:
  - name: search_results
    type: text
    description: Current matching eBay listings, search strategy, and notable trade-offs
---

# eBay Search

Find relevant current eBay listings and help the user compare them. Treat the task as research: provide useful, verifiable options but do not buy, bid, make an offer, contact a seller, save a search, or create alerts.
## API connection preflight

Before an API-backed search, run:

```bash
python3 scripts/validate_connection.py
```

The validator checks these environment variables without displaying their values:

- `EBAY_APP_ID`: the production eBay App ID / client ID.
- `EBAY_CERT_ID`: the production eBay Cert ID / client secret.

Interpret its JSON response before searching:

- `status: "ready"`: use the official Browse API where an API client is available.
- `status: "not_configured"`: tell the user that `EBAY_APP_ID` and/or `EBAY_CERT_ID` are missing. Explain that they can create production keys in the eBay Developers Program and export both variables in the agent's execution environment. Continue with visible browser-based eBay research if available.
- `status: "authentication_failed"`: tell the user the values were rejected, without exposing them. Ask them to verify that the App ID and Cert ID are a matching production pair and were exported without surrounding whitespace.
- `status: "connection_failed"`: tell the user the API could not be reached and include the returned non-sensitive detail. Continue with visible browser-based eBay research if available.

Do not print, log, or return either credential or the temporary OAuth token.

## Search workflow

1. Extract the searchable item details: brand, model or part number, edition, size, compatibility, condition, quantity, price ceiling, location, delivery deadline, and whether auctions are acceptable.
2. Ask a focused clarifying question only when a missing constraint would materially change the results. Otherwise, make sensible assumptions and state them briefly.
3. Build a precise search query. Prefer stable identifiers such as model numbers, part numbers, generations, sizes, or editions over broad keywords.
4. Run the API connection preflight before using an API client. Search eBay using the official Browse API when it is ready; otherwise use an available browser.
   - On a host Mac where Safari control is available, use the `safari-control` skill to drive the eBay website.
   - Use eBay's visible filters for condition, buying format, price, shipping, item location, and completed or sold listings when relevant.
5. Inspect each promising listing directly. Record the title, item price, shipping cost if shown, condition, buying format, seller information or feedback if visible, and canonical listing URL.
6. Compare the listings against the user's constraints. Flag uncertainty, missing details, suspiciously low prices, unclear compatibility, and differences between item price and total delivered cost.
7. Report the best matches concisely. Include the exact query and filters used so the user can reproduce or refine the search.

## Search guidance

- Use quotation marks around exact model names, part numbers, and distinctive phrases where the eBay search interface supports them.
- Exclude common false positives with negative terms when results are noisy. For example, exclude `case`, `parts`, `repair`, or `box only` only when those listings are unwanted.
- Distinguish `Buy It Now` from auctions; do not compare an auction's current bid as though it were its final price.
- Include shipping in price comparisons whenever it is available. Note tax separately because it depends on the buyer's location and may not be shown until checkout.
- For availability or market-price research, check sold or completed listings separately and clearly label them as historical results rather than items that can be bought now.
- For collectibles, electronics, and other condition-sensitive goods, prioritize photos, the full condition description, included accessories, return policy, and seller feedback over title keywords alone.
- Never infer authenticity, functionality, compatibility, or condition from a title alone.

## Result format

Use this structure unless the user asks for a different format:

```text
Search: <query>
Filters: <condition, buying format, price, location, shipping, and other relevant filters>

Best current listings:
1. <title>
   <item price> + <shipping or "shipping not shown"> — <condition> — <buying format>
   Seller: <seller name and feedback, if visible>
   Why it matches: <brief rationale>
   <URL>

2. ...

Notes:
- <important trade-off, uncertainty, or recommended refinement>
```

If no listing meets the request, say so clearly, summarize the closest matches, and suggest the most useful query or filter change.

## Safety and accuracy

- Use only information visible in the listing or search results at the time of the search.
- Do not claim a listing is available after its page indicates it has ended or sold.
- Do not bypass eBay access controls, log in as the user, or handle payment or account information.
- Do not proceed beyond research without the user's explicit instruction and a supported workflow.