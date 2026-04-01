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

## Step 1b: Resolve Page IDs (if needed)

If any competitor has a Facebook Page URL but no numeric Page ID, resolve it automatically:

**Actor:** `apify/facebook-pages-scraper` (official Apify -- 38k users, 99.5% success)

```json
{
  "startUrls": [{"url": "https://www.facebook.com/{page_slug}/"}]
}
```

The response includes `pageAdLibrary.id` -- that is the Ad Library Page ID. Update the Competitors table with the resolved ID.

If the resolver fails, tell the user to find it manually: facebook.com/ads/library > search the page name > copy `view_all_page_id=` from the URL.

---

## Step 2: Scrape Each Competitor via Apify

For each competitor, scrape ALL ads (active + inactive/historical) from the Meta Ad Library.

### Primary Actor: `apify/facebook-ads-scraper`

Official Apify actor. 16k+ users, 99.4% success rate. Most reliable long-term.

**Input per competitor:**
```json
{
  "startUrls": [{"url": "https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&is_targeted_country=false&media_type=all&search_type=page&sort_data[direction]=desc&sort_data[mode]=total_impressions&view_all_page_id={PAGE_ID}"}],
  "resultsLimit": 100
}
```

Key URL parameters:
- `active_status=all` -- pulls active AND historical/inactive ads
- `sort_data[mode]=total_impressions` -- highest impression ads first
- `country=ALL` -- all countries (change to `GB`, `US`, etc. to filter)

Use the Apify MCP `call-actor` tool. Set `async: false` so it waits for results.

### Fallback Actor 1: `curious_coder~facebook-ads-library-scraper`

Use if the primary actor is unavailable or returns errors.

```json
{
  "urls": [{"url": "https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&media_type=all&search_type=page&view_all_page_id={PAGE_ID}"}],
  "scrapePageAds.activeStatus": "all",
  "scrapePageAds.sortBy": "impressions_desc",
  "count": 100
}
```

### Fallback Actor 2: `whoareyouanas/meta-ad-scraper`

Simplest input -- takes Page ID directly.

```json
{
  "pageId": "{PAGE_ID}",
  "activeStatus": "all",
  "country": "ALL",
  "sortMode": "total_impressions",
  "sortDirection": "desc"
}
```

### Scraping rules

- Run competitors in sequence (not parallel) to avoid Apify rate limits
- Each scrape takes 30-120 seconds depending on ad count
- Print progress after each: `[{N}/{total}] {Name}: {count} ads scraped`
- If the primary actor fails on a competitor, retry once. If it fails again, try Fallback 1. Log which actor succeeded.

---

## Step 3: Dedup Against Existing Records

Before inserting, fetch existing Ad Archive IDs from the Swipe File:

```
Use Airtable MCP: list_records
  base_id: {from CLAUDE.md}
  table_id: {Swipe File table ID}
  fields: Ad Archive ID, Status, Start Date, Ad Active Status
```

Build a set of existing Ad Archive IDs.

**Dedup logic:**
- Ad in new scrape but NOT in Airtable = INSERT as new record
- Ad in new scrape AND already in Airtable = update `Ad Active Status` if changed (active -> inactive or vice versa), otherwise skip
- Ad in Airtable (Status = Active) but NOT in any new scrape AND was previously active = mark `Status` -> `Killed`, set `End Date` to today

**IMPORTANT:** When scraping with `active_status=all`, the source data includes both active and inactive ads. The `Ad Active Status` field tracks the Meta status. The `Status` field tracks YOUR status (Active, Killed, Winner, Starred). These are different things:
- `Ad Active Status` = what Meta says (Active or Inactive)
- `Status` = your classification (Active in swipe file, Killed from swipe file, Winner, Starred)

---

## Step 4: Transform and Insert New Ads

For each new ad, transform the Apify response into an Airtable record.

**Key field mappings (Primary actor: `apify/facebook-ads-scraper`):**

The official actor output uses a flat structure. Map fields as follows:

| Swipe File Field | Source | Notes |
|-----------------|--------|-------|
| Ad Archive ID | `adArchiveID` (string) | Primary dedup key |
| Competitor | Competitor name (text) | From your Competitors table |
| Page Name | `pageName` | |
| Ad Library URL | `https://www.facebook.com/ads/library/?id={adArchiveID}` | Construct from ID |
| Status | `Active` | Your classification -- always start as Active |
| Ad Active Status | `isActive` or derive from `startDate`/`endDate` | Meta's status: `Active` or `Inactive` |
| Start Date | `startDate` | May be ISO string or unix timestamp -- handle both |
| End Date | `endDate` | Only present for inactive ads |
| Display Format | Map from media: has video = `Video`, has image = `Image`, multiple images = `Carousel`, none = `DCO` | |
| Body Text | `bodyText` or `snapshot.body.text` | Field name varies by actor -- check both |
| Title | `title` or `snapshot.title` | |
| CTA Type | `ctaType` or `snapshot.cta_type` | |
| CTA Text | `ctaText` or `snapshot.cta_text` | |
| Link URL | `linkUrl` or `snapshot.link_url` | |
| Video URL | Look for `videoHDUrl`, `videoSDUrl`, `snapshot.videos[0].video_hd_url` | HD preferred, SD fallback |
| Image URL | Look for `imageUrl`, `originalImageUrl`, `snapshot.images[0].original_image_url` | |
| Word Count | Count words in Body Text | |
| Hook Copy | First line of Body Text (up to first period or newline) | |
| Scrape Date | Today's date | |
| Scrape Batch ID | Apify dataset ID | |
| Is Analyzed | false | |

**IMPORTANT: Output fields vary between actors.** The primary actor, Fallback 1, and Fallback 2 all use slightly different field names. When processing results:
1. Log the first result to see the exact field names
2. Try the primary field name first, then known alternatives
3. If a field is missing, leave it blank rather than erroring

**Fallback field name mappings:**

| Field | Primary (`apify/facebook-ads-scraper`) | Fallback 1 (`curious_coder`) | Fallback 2 (`whoareyouanas`) |
|-------|---------------------------------------|------------------------------|------------------------------|
| Archive ID | `adArchiveID` | `ad_archive_id` | `adArchiveID` |
| Body text | `bodyText` | `snapshot.body.text` | `description` |
| Page name | `pageName` | `snapshot.page_name` | `brandName` |
| Start date | `startDate` | `start_date` (unix) | `startDate` |
| Video URL | `videoHDUrl` | `snapshot.videos[0].video_hd_url` | `videoUrl` |
| Image URL | `imageUrl` | `snapshot.images[0].original_image_url` | `imageUrl` |

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

1. **Primary actor is `apify/facebook-ads-scraper`** (official Apify, 16k+ users, 99.4% success). Fallback 1: `curious_coder~facebook-ads-library-scraper`. Fallback 2: `whoareyouanas/meta-ad-scraper`.
2. **Always scrape with `active_status=all`** to get both active and historical/inactive ads. Inactive ads that ran 60+ days are proven winners.
3. **Start dates may be ISO strings or unix timestamps** depending on the actor. Handle both: try parsing as ISO first, then as unix timestamp.
4. **DCO ads have no media URLs.** Display format = DCO means Meta assembles the creative dynamically. Still insert the record -- the copy is useful.
5. **Dedup on Ad Archive ID.** Same ad can appear in multiple scrapes.
6. **Airtable batch limit is 10 records per request.** Always batch creates and updates.
7. **Facebook Page ID vs Profile ID:** The Competitors table stores the Ad Library page ID, NOT the profile ID. Use `apify/facebook-pages-scraper` to resolve page URLs to Ad Library IDs (the `pageAdLibrary.id` field).
8. **Run competitors in sequence.** Parallel scraping hits Apify rate limits.
9. **Never delete records.** Mark killed ads as Killed with an End Date. History matters.
10. **Ad Active Status vs Status:** `Ad Active Status` is what Meta reports (Active/Inactive). `Status` is your swipe file classification (Active, Killed, Winner, Starred). An ad can be `Ad Active Status = Inactive` but `Status = Winner` -- that means it ran successfully and was turned off after scaling.
11. **If the primary actor fails**, retry once. If it fails again, switch to Fallback 1. If that fails, try Fallback 2. Log which actor worked for each competitor.
12. **Fallback if all Apify actors are down:** You can manually browse the Meta Ad Library at facebook.com/ads/library and add records to the Swipe File via Airtable directly. The rest of the pipeline (analyzer, ideator, scripter) still works.
