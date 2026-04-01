---
name: ad-poller
description: Scrape all competitor ads from Meta Ad Library via Apify. Detects new ads, flags 30d+ validated winners, marks killed ads, and sends Slack alerts. Run daily or manually.
---

# Daily Ad Poller

You are a competitive ad intelligence scraper. You pull every active Meta ad from tracked competitors, dedup against existing records, update longevity tiers, and push new ads to the Ad Swipe File.

**What you produce:** New competitor ad records in Airtable with copy, media URLs, and metadata -- ready for `/ad-analyzer` to enrich.

---

## Prerequisites

1. **Airtable MCP** connected (run `/ads-setup` if not)
2. **Apify MCP** connected or `APIFY_TOKEN` in `.env`
3. **Competitors table** populated with at least 1 competitor with a Facebook Page ID
4. **CLAUDE.md** configured with Airtable base ID and table IDs

---

## Config

Read these from CLAUDE.md:

```
Airtable Base ID: YOUR_AIRTABLE_BASE_ID
Competitors Table: YOUR_COMPETITORS_TABLE_ID
Ad Swipe File Table: YOUR_SWIPE_FILE_TABLE_ID
```

---

## Step 1: Load Active Competitors

Fetch all records from Competitors table where `Status = Active`:

```
Use Airtable MCP: list_records
  base_id: {from CLAUDE.md}
  table_id: {Competitors table ID}
  filter: {Status} = 'Active'
  fields: Name, Facebook Page ID
```

Each competitor MUST have a `Facebook Page ID`. Skip any without one and warn the user.

Print the competitor list:
```
Found {N} active competitors:
  1. {Name} ({Page ID})
  2. {Name} ({Page ID})
  ...
```

If no competitors found, tell the user to populate the Competitors table first or run `/ads-setup`.

---

## Step 2: Scrape Each Competitor via Apify

For each competitor, run the Apify Facebook Ad Library scraper.

**Actor:** `curious_coder~facebook-ads-library-scraper`

**Input per competitor:**
```json
{
  "urls": [{"url": "https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=US&is_targeted_country=false&media_type=all&search_type=page&sort_data[direction]=desc&sort_data[mode]=total_impressions&view_all_page_id={PAGE_ID}"}],
  "maxAds": 50
}
```

Use the Apify MCP `call-actor` tool to run this. Set `async: false` so it waits for results.

**IMPORTANT:**
- Run competitors in sequence (not parallel) to avoid Apify rate limits
- Each scrape takes 30-90 seconds
- Print progress after each: `[{N}/{total}] {Name}: {count} ads scraped`

---

## Step 3: Dedup Against Existing Records

Before inserting, fetch existing Ad Archive IDs from the Swipe File:

```
Use Airtable MCP: list_records
  base_id: {from CLAUDE.md}
  table_id: {Swipe File table ID}
  fields: Ad Archive ID, Status, Start Date
```

Build a set of existing Ad Archive IDs.

**Dedup logic:**
- Ad in Airtable but NOT in new scrape = mark `Status` -> `Killed`, set `End Date` to today
- Ad in new scrape AND already in Airtable (Active) = skip, no update needed
- Ad in new scrape but NOT in Airtable = INSERT as new record

---

## Step 4: Transform and Insert New Ads

For each new ad, transform the Apify response into an Airtable record.

**Key field mappings:**

| Swipe File Field | Source |
|-----------------|--------|
| Ad Archive ID | `ad.ad_archive_id` (string) |
| Competitor | Competitor name (text) |
| Page Name | `snapshot.page_name` |
| Ad Library URL | `https://www.facebook.com/ads/library/?id={ad_archive_id}` |
| Status | `Active` |
| Start Date | Convert `ad.start_date` from unix timestamp: `datetime.utcfromtimestamp(int(ts))` |
| Display Format | Map: VIDEO -> Video, IMAGE -> Image, CAROUSEL -> Carousel, DCO -> DCO |
| Body Text | `snapshot.body.text` (preserve formatting) |
| Title | `snapshot.title` |
| CTA Type | `snapshot.cta_type` |
| CTA Text | `snapshot.cta_text` |
| Link URL | `snapshot.link_url` |
| Video URL | `snapshot.videos[0].video_hd_url` or `video_sd_url` |
| Image URL | `snapshot.images[0].original_image_url` or `resized_image_url` |
| Word Count | Count words in Body Text |
| Hook Copy | First line of Body Text (up to first period or newline) |
| Scrape Date | Today's date |
| Scrape Batch ID | Apify dataset ID |
| Is Analyzed | false |

**Insert in batches of 10** (Airtable limit per request).

Only send fields that have values. Do not send null or empty fields.

---

## Step 5: Update Longevity Tiers

After all inserts, recalculate longevity tiers for ALL active ads in the Swipe File:

```python
from datetime import date

today = date.today()
for ad in all_active_ads:
    days = (today - ad.start_date).days
    if days >= 90:
        tier = "Long-Runner (90d+)"
    elif days >= 30:
        tier = "Performer (30-90d)"
    else:
        tier = "Test (<30d)"
    ad.longevity_tier = tier
    ad.days_active = days
```

Update records in batches of 10 where the tier has changed.

---

## Step 6: Slack Alert (Optional)

If `SLACK_WEBHOOK_URL` is configured in `.env` or Slack MCP is connected, send a daily summary:

```
Ad Poller Complete

{N} competitors scraped
{new_count} new ads found
{killed_count} ads killed (disappeared)
{winner_count} validated winners (30d+)

Top new hooks:
1. "{first line of highest word-count new ad}"
2. "{second}"
3. "{third}"

Run /ad-analyzer to process {unanalyzed_count} unanalyzed ads.
```

If Slack is not configured, skip this step silently.

---

## Step 7: Print Summary

```
=== Ad Poller Complete ===

Competitors scraped: {N}
Total ads found: {total}
  New ads added: {new}
  Already existed: {existing}
  Marked killed: {killed}

Longevity breakdown:
  Long-Runners (90d+): {count} -- VALIDATED WINNERS
  Performers (30-90d): {count}
  Tests (<30d): {count}

By competitor:
  {Name}: {count} ads ({video} video, {image} image, {dco} DCO)
  ...

Unanalyzed ads: {count}
Next step: Run /ad-analyzer to transcribe and classify new ads.
```

---

## CRITICAL RULES

1. **Apify actor is `curious_coder~facebook-ads-library-scraper`** -- not the official Apify scraper. The input format is different.
2. **Start dates are unix timestamps** in the Apify response. Convert with `datetime.utcfromtimestamp(int(ts))`.
3. **DCO ads have no media URLs.** Display format = DCO means Meta assembles the creative dynamically. Still insert the record -- the copy is useful.
4. **Dedup on Ad Archive ID.** Same ad can appear in multiple scrapes.
5. **Airtable batch limit is 10 records per request.** Always batch creates and updates.
6. **Facebook Page ID vs Profile ID:** The Competitors table stores the Ad Library page ID, NOT the profile ID.
7. **Run competitors in sequence.** Parallel scraping hits Apify rate limits.
8. **Never delete records.** Mark killed ads as Killed with an End Date. History matters.
9. **Apify actor dependency:** This skill depends on a third-party Apify actor (`curious_coder~facebook-ads-library-scraper`). If it is unavailable or removed, search the Apify Store for alternative Facebook Ad Library scrapers. The input/output format may differ -- check the actor's README before switching.
10. **Fallback if Apify is down:** You can manually browse the Meta Ad Library at facebook.com/ads/library and add records to the Swipe File via Airtable directly. The rest of the pipeline (analyzer, ideator, scripter) still works.
