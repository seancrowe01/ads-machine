---
name: ad-launch
description: Prepare and launch Meta ad campaigns. Default mode generates Ads Manager-ready specs you copy-paste in. Advanced mode creates campaigns via the API (requires compliance checklist). Updates Pipeline records.
---

# Ad Launcher

You help launch Meta ad campaigns from Pipeline records. You offer two modes:

1. **SAFE MODE (default)** -- Generate complete, copy-paste-ready campaign specs. The user creates the campaign manually in Ads Manager or through an approved partner tool. Zero API risk.

2. **DIRECT API MODE (advanced)** -- Create campaigns programmatically via the Meta Graph API. Requires the user to confirm they have completed the compliance checklist first. Carries account risk if done incorrectly.

**IMPORTANT:** Before offering Direct API Mode, you MUST read `reference/compliance.md` and present the risks. Accounts have been permanently banned for using unapproved API connections. This is not theoretical -- it has happened to advertisers with 16+ years and $1.5M+ in lifetime spend.

---

## Step 0: Choose Launch Mode

Ask the user:

```
How do you want to launch this campaign?

1. SAFE MODE (recommended)
   I will generate complete campaign specs -- objective, targeting,
   budget, copy, creative specs -- formatted so you can build it
   in Ads Manager in under 5 minutes. Zero API risk.

2. DIRECT API MODE (advanced -- read compliance warning first)
   I will create the campaign via the Meta Graph API directly.
   This requires a compliant setup. If your app has not passed
   Meta App Review, this can get your ad account permanently banned.

Which mode? (1 / 2)
```

If the user picks 2, proceed to the **Compliance Gate** before any API call.

---

## SAFE MODE (Default)

### Step 1: Select Pipeline Ad

Show Pipeline records ready for launch:

```
Use Airtable MCP: list_records
  filter: OR({Status}='Briefed', {Status}='Scripted')
  fields: Name, Hook, Primary Text, Headline, CTA Type, Format, Landing Page
```

Let the user pick one.

### Step 2: Confirm Campaign Details

Ask the user to confirm or provide:
1. **Campaign name** -- suggest: `{BusinessCode}_{Angle}_{Date}`
2. **Objective** -- Leads, Sales, Traffic, Awareness, Engagement
3. **Daily budget** -- in their currency
4. **Targeting** -- location, age range, gender, interests
5. **Optimization goal** -- Lead gen, conversions, link clicks, etc.
6. **Placements** -- Advantage Plus (recommended) or manual
7. **Creative asset description** -- what video/image they will upload
8. **Landing page URL**

### Step 3: Generate Ads Manager Blueprint

Output a complete, step-by-step blueprint they can follow in Ads Manager:

```
=== CAMPAIGN BLUEPRINT ===
Ready to build in Meta Ads Manager

CAMPAIGN
  Name: {campaign_name}
  Objective: {objective}
  Special Ad Category: None (unless housing, credit, employment, or politics)
  Status: Start PAUSED

AD SET
  Name: {campaign_name} - Ad Set
  Budget: {currency}{daily_budget}/day
  Schedule: Start date {today or specified}
  Optimization: {optimization_goal}
  Bid strategy: Lowest cost

  TARGETING
  Location: {locations}
  Age: {min}-{max}
  Gender: {gender}
  Detailed targeting: {Advantage Plus recommended, or specific interests}
  Placements: {Advantage Plus or manual list}

AD CREATIVE
  Format: {video / single image / carousel}
  Primary text:
  ---
  {primary_text from Pipeline}
  ---
  Headline: {headline}
  Description: {description}
  CTA button: {cta_type}
  Landing page: {landing_page_url}

  Creative specs:
  - Aspect ratio: {9:16 for stories/reels, 4:5 for feed}
  - Minimum resolution: 1080x1080
  - Video length: {duration from script}
  - File format: MP4 (video) or JPG/PNG (image)

LAUNCH CHECKLIST
[ ] Campaign created and set to PAUSED
[ ] Ad set targeting verified
[ ] Creative uploaded and approved
[ ] Landing page loads correctly on mobile
[ ] Pixel/CAPI firing on landing page
[ ] Preview ad on mobile before activating
[ ] Activate campaign
```

### Step 4: Update Pipeline Record

```
Use Airtable MCP: update_records
  fields:
    Landing Page: {url}
    Status: "Launched"
    Launch Date: {today}
```

Print:
```
Blueprint ready. Build this in Ads Manager and update the Pipeline
with the Campaign ID once it is live.

After 3-5 days, run /ad-monitor to check performance.
```

---

## DIRECT API MODE (Advanced)

### Compliance Gate

Before ANY API call, present this warning and checklist:

```
--- COMPLIANCE WARNING ---

Advertisers have been PERMANENTLY BANNED for connecting AI tools
to Meta via unapproved developer apps. This includes accounts with
16+ years of history and $1.5M+ in lifetime spend.

Read the full details: reference/compliance.md

Before proceeding, confirm ALL of the following:

[ ] 1. Your Meta developer app has passed Meta App Review
       with ads_management permission
[ ] 2. Your app is NOT created on the same Facebook account
       you use to run ads
[ ] 3. Your Business Manager has completed Meta Business Verification
[ ] 4. You understand that using an unapproved app can result
       in permanent account ban with no appeal
[ ] 5. You accept full responsibility for any account actions

Type "I confirm all 5 items" to proceed, or type "safe" to switch
to Safe Mode instead.
```

**If the user does not confirm all 5 items, do NOT proceed with API calls. Switch to Safe Mode.**

If they do not have a reviewed app, recommend:
- **Pipeboard** (pipeboard.co) -- Meta Business Partner, handles compliance
- **Madgicx** (madgicx.com) -- Meta Business Partner, AI-native
- **Revealbot** (revealbot.com) -- Approved automation tool

### Rate Limiting (Required for Direct API)

All API calls MUST follow these rules:
- Maximum 200 calls per hour per token
- Minimum 3-second delay between write operations
- Maximum 10 write operations per minute
- Check `x-fb-ads-insights-throttle` header before insight pulls
- Exponential backoff on 429 or throttle responses
- Never batch-create more than 5 ads in a single session

### Step 1: Select Pipeline Ad

Same as Safe Mode Step 1.

### Step 2: Confirm Campaign Details

Same as Safe Mode Step 2.

### Step 3: Create Campaign

```
POST /{ad_account_id}/campaigns

{
  "name": "{campaign_name}",
  "objective": "{objective}",
  "status": "PAUSED",
  "special_ad_categories": "NONE"
}
```

**API notes:**
- `special_ad_categories` must be string `"NONE"`, not `[]`
- Always create PAUSED
- Wait 3 seconds before next API call

Save the returned `campaign_id`.

### Step 4: Create Ad Set

```
POST /{ad_account_id}/adsets

{
  "name": "{campaign_name} - Ad Set",
  "campaign_id": "{campaign_id}",
  "daily_budget": {budget_in_cents},
  "billing_event": "IMPRESSIONS",
  "optimization_goal": "{optimization_goal}",
  "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
  "is_adset_budget_sharing_enabled": "0",
  "targeting": {targeting_object},
  "promoted_object": {promoted_object},
  "status": "PAUSED"
}
```

**API notes:**
- `is_adset_budget_sharing_enabled` must be `"0"` (string), not `false`
- Budget is in cents/pence (e.g. $20/day = 2000)
- `promoted_object` depends on objective:
  - Leads: `{"pixel_id": "{pixel_id}", "custom_event_type": "LEAD"}`
  - Traffic: `{"page_id": "{page_id}"}`
  - Conversions: `{"pixel_id": "{pixel_id}", "custom_event_type": "{event}"}`
- Wait 3 seconds before next API call

### Step 5: Upload Creative Asset

**For video:**
```
POST /{ad_account_id}/advideos
Content-Type: multipart/form-data
file: {video_file}
```

**For image:**
```
POST /{ad_account_id}/adimages
Content-Type: multipart/form-data
file: {image_file}
```

After video upload: fetch thumbnail URL immediately. **Thumbnail URLs expire.**

Wait 3 seconds before next API call.

### Step 6: Create Ad Creative

**Video:**
```
POST /{ad_account_id}/adcreatives
{
  "name": "{campaign_name} - Creative",
  "object_story_spec": {
    "page_id": "{page_id}",
    "video_data": {
      "video_id": "{video_id}",
      "title": "{headline}",
      "message": "{primary_text}",
      "image_url": "{thumbnail_url}",
      "call_to_action": {
        "type": "{cta_type}",
        "value": {"link": "{landing_page_url}"}
      }
    }
  }
}
```

**Image:**
```
POST /{ad_account_id}/adcreatives
{
  "name": "{campaign_name} - Creative",
  "object_story_spec": {
    "page_id": "{page_id}",
    "link_data": {
      "image_hash": "{image_hash}",
      "link": "{landing_page_url}",
      "message": "{primary_text}",
      "name": "{headline}",
      "description": "{description}",
      "call_to_action": {"type": "{cta_type}"}
    }
  }
}
```

**Meta app must be in Live mode** (not Development) to create ad creatives.

Wait 3 seconds before next API call.

### Step 7: Create Ad

```
POST /{ad_account_id}/ads
{
  "name": "{campaign_name} - Ad",
  "adset_id": "{adset_id}",
  "creative": {"creative_id": "{creative_id}"},
  "status": "PAUSED"
}
```

### Step 8: Show Summary and Confirm Activation

```
Campaign created (PAUSED):

{campaign_name}
+-- Campaign: {campaign_id}
|   Objective: {objective}
|
+-- Ad Set: {adset_id}
|   Budget: {currency}{daily_budget}/day
|   Targeting: {targeting_summary}
|
+-- Creative: {creative_id}
|   Format: {video/image}
|   CTA: {cta_type}
|
+-- Ad: {ad_id}
    Status: PAUSED
    Landing: {landing_page_url}

Ready to activate? This will start spending budget immediately.
(yes / no -- keep paused)
```

**If yes:** Activate:
```
POST /{campaign_id}
{"status": "ACTIVE"}
```

**If no:** Keep paused.

### Step 9: Update Pipeline Record

```
Use Airtable MCP: update_records
  fields:
    Campaign ID: {campaign_id}
    Ad Set ID: {adset_id}
    Ad ID: {ad_id}
    Creative ID: {creative_id}
    Landing Page: {landing_page_url}
    Launch Date: {today}
    Status: "Active" (if activated) or "Launched" (if paused)
```

---

## Multiple Ads Under One Campaign

1. Create ONE campaign + ONE ad set
2. Create multiple ad creatives (one per asset)
3. Create multiple ads under the same ad set
4. Meta optimizes delivery across creatives automatically
5. Post-Andromeda best practice: 1 campaign, 1 ad set, many ads
6. In Direct API Mode: space out ad creation calls (3 seconds between each)

---

## CRITICAL RULES

1. **Safe Mode is the default.** Never jump to Direct API without the compliance gate.
2. **The compliance checklist is mandatory.** No exceptions. No shortcuts.
3. **Everything launches PAUSED.** Never auto-activate.
4. **Rate limit all API calls.** 3-second minimum between writes. 10 writes per minute max.
5. **If the user does not have a reviewed app, do not proceed with Direct API.** Recommend approved partners instead.
6. **Save all IDs back to the Pipeline** so `/ad-monitor` can track performance.
7. **This skill does not provide legal advice.** The compliance guide is informational. The user is responsible for their own account.
