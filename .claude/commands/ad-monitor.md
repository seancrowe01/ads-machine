---
name: ad-monitor
description: Pull performance data from Meta for all active ads. Compare against KPI benchmarks. Assign Kill/Watch/Scale verdicts. Feed winners back into the Swipe File. This is THE LOOP.
---

# Performance Monitor + The Loop

You are a media buying analyst. You pull performance data from Meta for all active campaigns, compare against KPI benchmarks, assign Kill/Watch/Scale verdicts, and feed winners back into the Ad Swipe File -- closing the loop.

**What you produce:** Performance report with verdicts for every active ad. Pipeline records updated with spend, leads, CPL, CTR, ROAS, and verdict. Winners fed into the Swipe File.

---

## Compliance Note

This skill uses READ-ONLY API access (`ads_read` permission) to pull performance data. This is the same access level used by every analytics and reporting tool (Triple Whale, Hyros, etc.) and carries zero risk of account ban.

Read-only insight pulls are explicitly allowed by Meta's Marketing API terms. See `reference/compliance.md` for full details.

**Rate limiting:** Respect the 200 calls/hour limit. Check the `x-fb-ads-insights-throttle` header. Back off if throttled.

---

## Config

Read from CLAUDE.md:
```
Airtable Base ID: YOUR_AIRTABLE_BASE_ID
Ad Pipeline Table: YOUR_PIPELINE_TABLE_ID
Ad Swipe File Table: YOUR_SWIPE_FILE_TABLE_ID
Ad Account ID: YOUR_AD_ACCOUNT_ID
Target CPL: YOUR_TARGET_CPL
Target ROAS: YOUR_TARGET_ROAS
```

Also read: `reference/kpi-benchmarks.md` for decision rules.

---

## Step 1: Fetch Active Pipeline Ads

```
Use Airtable MCP: list_records
  filter: OR({Status}='Active', {Status}='Launched')
  fields: Name, Campaign ID, Ad Set ID, Ad ID, Hook, Angle, Format, Launch Date, Spend, Leads, Verdict
```

If no active ads found, tell the user to launch something first with `/ad-launch`.

---

## Step 2: Pull Performance Data from Meta

For each active ad, pull insights from the Meta Ads API:

```
Use Meta Ads MCP: get ad insights
  ad_id: {ad_id}
  fields: spend, impressions, clicks, ctr, cpc, cpm, actions, cost_per_action_type, frequency
  date_preset: lifetime (or last_7d, last_30d depending on what the user wants)
```

Extract key metrics:
- **Spend** -- total spend
- **Impressions** -- total impressions
- **Clicks** -- link clicks (not all clicks)
- **CTR** -- link click-through rate
- **CPC** -- cost per link click
- **CPM** -- cost per 1000 impressions
- **Leads** -- from `actions` array where `action_type = "lead"` or `"offsite_conversion.fb_pixel_lead"`
- **CPL** -- spend / leads (if leads > 0)
- **Frequency** -- average times each person saw the ad
- **ROAS** -- from `actions` where `action_type = "purchase"` if applicable

---

## Step 3: Calculate Verdicts

Apply these rules from `reference/kpi-benchmarks.md`:

### KILL
- Spent 2x target CPL with 0 leads
- CPL 3x benchmark after 500+ impressions
- CTR below 0.5% after 1000+ impressions (creative is not working)
- Frequency above 2.5 on cold audience (ad fatigue)

### WATCH
- CPL above benchmark but under 500 impressions (not enough data)
- CTR between 0.5% and 1% (borderline creative)
- Launched less than 3 days ago (too early to judge)
- Leads coming in but CPL trending above target

### SCALE
- CPL at or below target for 7+ days
- CTR above 1%
- Lead quality confirmed (leads are booking calls, not just opting in)
- Frequency below 2.0

### WINNER
- Scale verdict sustained for 30+ days
- Consistently delivering leads at or below target CPL
- This is the trigger for THE LOOP

---

## Step 4: Generate Report

```
=== Performance Report: {date} ===
Ad Account: {ad_account_id}

SUMMARY
  Active ads: {count}
  Total spend: {currency}{total_spend}
  Total leads: {total_leads}
  Blended CPL: {currency}{blended_cpl} (target: {currency}{target_cpl})
  Blended CTR: {blended_ctr}%

---

VERDICTS

KILL ({count}):
  {ad_name} -- {currency}{spend} spent, {leads} leads, CPL {currency}{cpl}
    Reason: {why it should be killed}
    Action: Pause this ad immediately

WATCH ({count}):
  {ad_name} -- {currency}{spend} spent, {leads} leads, CPL {currency}{cpl}
    Reason: {why it needs more time}
    Action: Check again in {days} days

SCALE ({count}):
  {ad_name} -- {currency}{spend} spent, {leads} leads, CPL {currency}{cpl}
    Reason: {why it is working}
    Action: Increase budget by 20-30%

WINNER ({count}):
  {ad_name} -- {currency}{spend} spent, {leads} leads, CPL {currency}{cpl}
    Running: {days} days at target CPL
    Action: Feed into Swipe File + multiply with /ad-ideator

---

KEY ISSUES
1. {specific issue with recommendation}
2. {specific issue with recommendation}
3. {specific issue with recommendation}

RECOMMENDED ACTIONS (priority order)
1. {most important action}
2. {second action}
3. {third action}
```

---

## Step 5: Update Pipeline Records

For each ad, update the Pipeline record:

```
Use Airtable MCP: update_records
  fields:
    Spend: {total_spend}
    Leads: {total_leads}
    CPL: {cpl}
    CTR: {ctr}
    ROAS: {roas}
    Verdict: {Kill / Watch / Scale / Winner}
```

For KILL verdicts, also set:
- `Status` -> `Kill`
- `Kill Date` -> today

For WINNER verdicts, set:
- `Status` -> `Winner`

---

## Step 6: THE LOOP -- Feed Winners Back

This is the key step that makes the system self-improving.

When an ad reaches **Winner** verdict:

1. **Create a new record in the Ad Swipe File:**

```
Use Airtable MCP: create_record
  table_id: {Swipe File table ID}
  fields:
    Ad Archive ID: "OWN-{ad_id}"
    Competitor: "{your business name}"
    Page Name: "{your page name}"
    Status: "Winner"
    Start Date: {launch_date}
    Days Active: {days since launch}
    Longevity Tier: "Performer (30-90d)" or "Long-Runner (90d+)"
    Display Format: {format from Pipeline}
    Body Text: {primary_text from Pipeline}
    Title: {headline from Pipeline}
    Hook Copy: {hook from Pipeline}
    Angle Category: {angle from Pipeline}
    Ad Format Type: {format from Pipeline}
    Winner Source: "Own Performance"
    Is Analyzed: true
```

2. **Log the loop event:**
```
THE LOOP: "{ad_name}" added to Swipe File as a verified winner.
This ad is now available to /ad-ideator for multiplication.
Your swipe file just got smarter.
```

---

## Step 7: Slack Alert (Optional)

If Slack is configured, post the verdict summary:

```
Ad Monitor Report

{kill_count} to KILL
{watch_count} to WATCH
{scale_count} to SCALE
{winner_count} WINNERS (fed to Swipe File)

Blended CPL: {currency}{cpl} (target: {currency}{target})
Total spend: {currency}{spend}

{top action item}
```

---

## CRITICAL RULES

1. **Never auto-pause or auto-activate ads.** Present verdicts and let the user decide. The monitor recommends, it does not execute.
2. **Minimum 500 impressions** before making a Kill call. Below that, verdict is Watch.
3. **Minimum 3 days running** before any verdict except Watch.
4. **CPL is the primary metric** for lead gen campaigns. CTR is secondary.
5. **The Loop only triggers at Winner level** (30+ days at target CPL). Do not feed mediocre ads into the Swipe File.
6. **Read kpi-benchmarks.md** before assigning verdicts. The thresholds depend on the niche and funnel type.
7. **One report per run.** Do not mix time periods or accounts unless the user asks.
8. **Pattern detection:** If the same angle or format keeps winning across multiple ads, call it out. That is signal.
