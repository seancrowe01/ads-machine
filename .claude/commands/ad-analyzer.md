---
name: ad-analyzer
description: Analysis engine for the Ad Swipe File. Downloads video creatives, transcribes with Whisper, extracts hooks and copy patterns with Claude, runs visual analysis with Gemini, scores and ranks everything. Run after /ad-poller.
---

# Ad Analysis Engine

You are a creative analysis system. You process unanalyzed ads from the Swipe File -- downloading videos, transcribing speech, extracting hooks, classifying angles and formats, running visual analysis, and scoring each ad.

**What you produce:** Fully enriched Swipe File records with transcripts, hooks, classifications, visual analysis, and composite scores -- ready for `/ad-ideator` to work from.

---

## Prerequisites

1. **Airtable MCP** connected
2. **Unanalyzed ads** in the Swipe File (run `/ad-poller` first)
3. **ffmpeg installed** -- for audio extraction (check: `ffmpeg -version`)
4. **whisper.cpp installed** -- for transcription (check: `whisper-cli --help`)
   - If not installed, skip transcription and note it in the summary
5. **Gemini API key** in `.env` as `GEMINI_API_KEY` (optional -- for visual analysis)

---

## Config

Read from CLAUDE.md:
```
Airtable Base ID: YOUR_AIRTABLE_BASE_ID
Ad Swipe File Table: YOUR_SWIPE_FILE_TABLE_ID
```

---

## Step 1: Fetch Unanalyzed Ads

```
Use Airtable MCP: list_records
  base_id: {from CLAUDE.md}
  table_id: {Swipe File table ID}
  filter: {Is Analyzed} = FALSE()
  fields: Ad Archive ID, Competitor, Display Format, Body Text, Title, Video URL, Image URL, Hook Copy
```

Print count: `Found {N} unanalyzed ads to process.`

If the user passed a count argument, limit to that many. Otherwise process all.

---

## Step 2: Process Video Ads

For each ad where Display Format = Video AND Video URL exists:

### 2a. Download Video
```bash
mkdir -p /tmp/ads-machine
curl -s -L -o /tmp/ads-machine/{ad_archive_id}.mp4 --max-time 60 "{video_url}"
```

If download fails, log it and continue to the next ad.

### 2b. Get Metadata
```bash
ffprobe -v quiet -print_format json -show_format -show_streams /tmp/ads-machine/{ad_archive_id}.mp4
```

Extract:
- `duration` (seconds, rounded)
- `width` and `height` -> calculate aspect ratio:
```python
ratio = width / height
if abs(ratio - 9/16) < 0.05: aspect = "9:16"
elif abs(ratio - 4/5) < 0.05: aspect = "4:5"
elif abs(ratio - 1) < 0.05: aspect = "1:1"
elif abs(ratio - 16/9) < 0.05: aspect = "16:9"
else: aspect = "Other"
```

### 2c. Extract Audio
```bash
ffmpeg -i /tmp/ads-machine/{ad_archive_id}.mp4 -ar 16000 -ac 1 -f wav /tmp/ads-machine/{ad_archive_id}.wav -y 2>/dev/null
```

### 2d. Transcribe with Whisper
```bash
whisper-cli -m {model_path} -f /tmp/ads-machine/{ad_archive_id}.wav --no-prints
```

Use whichever whisper model is available. `tiny.en` (75MB) is fast and sufficient for ad transcription. `medium.en` (1.5GB) is more accurate.

If whisper is not installed, check for OpenAI API key and use the Whisper API as fallback:
```bash
curl -s https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer {OPENAI_API_KEY}" \
  -F model="whisper-1" \
  -F file="@/tmp/ads-machine/{ad_archive_id}.wav"
```

If neither is available, skip transcription. Log: `Whisper not available -- skipping transcription for {count} video ads.`

### 2e. Extract Hook
Split transcript on sentence boundaries (`. ! ?`). Take the first 1-2 complete sentences.
- If the first sentence is fewer than 8 words, include the second sentence.
- This becomes the `Hook Video` field.

### 2f. Clean Up
```bash
rm /tmp/ads-machine/{ad_archive_id}.mp4 /tmp/ads-machine/{ad_archive_id}.wav
```

---

## Step 3: Classify Angle Category

For every ad (video and non-video), classify based on available text content (body text + title + transcript).

### Signal Table

| Angle | Signals in Copy/Transcript |
|-------|---------------------------|
| Social Proof | Testimonials, revenue numbers, "since we signed up", "my name is", case studies, client results |
| Pain-to-Transformation | Fees, losing money, switching pain, "save you", "fight back", frustration language |
| Tips/Education | How-to, listicles, "reason number", "watch this", educational framing, step-by-step |
| Growth Problem | More orders, scaling, "drive sales", "increase your", growth metrics |
| Profit Problem | Costs, margins, wasted spend, "paying too much", ROI language |
| Authority | Platform features, "only solution", data access, expert positioning, credentials |
| Scarcity/Urgency | Limited time, spots filling, deadline, "last chance", countdown |
| Behind-the-Scenes | Day-in-the-life, process reveal, "how we", "let me show you" |
| Controversy | Contrarian takes, "most people are wrong", "unpopular opinion", industry criticism |
| Comparison | "vs", "compared to", "I tested both", head-to-head |

If multiple signals match, choose the dominant one. If unclear, default to the first match.

---

## Step 4: Classify Ad Format Type

| Format | Detection Rules |
|--------|----------------|
| UGC Testimonial | Video + first-person experience ("my name is", "our sales", "since we", customer story) |
| UGC Talking Head | Video + presenter explaining features/benefits (second-person "you", instructional) |
| Interview/Case Study | Video + Q&A pattern, multiple speakers, interviewer framing |
| Motion Graphics | Video + no meaningful transcript (music only, silence, or very short text) |
| Static Image | Image display format with real copy |
| Screenshot/Demo | Image showing product interface, dashboard, or screen capture |
| Slideshow | Carousel or multi-image format |
| Other | DCO with template variables `{{product.name}}` or unclassifiable |

---

## Step 5: Visual Analysis with Gemini (Optional)

If `GEMINI_API_KEY` is in `.env`, run visual analysis on ads with images or video thumbnails.

For each ad with an Image URL or video thumbnail:

```
Analyze this ad creative and describe:
1. Visual format (photo, graphic, screenshot, text-heavy, minimal)
2. Color palette (dominant colors)
3. Text overlay presence and style (bold, subtle, none)
4. Production quality (professional, semi-pro, casual/UGC)
5. Human presence (face visible, hands only, no people)
6. Key visual elements that grab attention
```

Store the response in the `Visual Style` field.

If Gemini is not configured, skip this step silently. The rest of the analysis still works.

---

## Step 6: Calculate Longevity Tier

Days Active IS the grade. No composite scoring. The market already graded every ad.

```python
from datetime import date

today = date.today()
end = ad.end_date or today  # Active ads use today
days = (end - ad.start_date).days

if days >= 60:
    tier = "Long-Runner"
elif days >= 30:
    tier = "Performer"
elif days >= 14:
    tier = "Solid"
elif days >= 7:
    tier = "Testing"
else:
    tier = "Killed"

ad.days_active = days
ad.longevity_tier = tier
```

Format, angle, hook, CTA type are FILTERS for browsing -- not scoring factors. A static image running 90 days outranks a video killed in 3. "Show me all Long-Runners with social proof angle" is how you find patterns.

---

## Step 7: Update Airtable Records

Batch update all processed ads (10 per request):

Fields to update:
- `Video Duration` (if video)
- `Aspect Ratio` (if video)
- `Transcript` (if video + whisper available)
- `Hook Video` (if video + transcript)
- `Word Count`
- `Angle Category`
- `Ad Format Type`
- `Visual Style` (if Gemini available)
- `Days Active`
- `Longevity Tier`
- `Impressions Rank` (position in scrape results, 1 = most impressions)
- `Is Analyzed` = true

---

## Step 8: Feed Proven Hooks Database

After updating all ads, extract hooks from Long-Runners and push to the Proven Hooks table.

```
Read from CLAUDE.md:
  Proven Hooks Table: YOUR_PROVEN_HOOKS_TABLE_ID
```

For each ad where:
- `Longevity Tier` = `Long-Runner` OR `Performer` (30d+)
- Hook exists (Hook Video or Hook Copy is not empty)
- Hook is not already in the Proven Hooks table (dedup on Hook Text)

Create a record:
```
Use Airtable MCP: create_record
  fields: {
    Hook Text: {hook_video or hook_copy},
    Source Competitor: {competitor name},
    Source Ad: {ad library url},
    Angle Category: {angle},
    Format: {display format},
    Days Active: {days},
    Longevity Tier: {tier},
    Niche Tier: {competitor's niche tier from Competitors table},
    Date Added: {today}
  }
```

This runs silently. No user interaction. The Proven Hooks table grows automatically every time the analyzer processes new Long-Runners.

After a month of daily polling with 5+ competitors, the user will have 100+ proven hooks searchable by angle, format, and competitor -- all backed by real ad spend data.

---

## Step 9: Print Summary

```
=== Analysis Complete ===

Ads processed: {total}
  Videos transcribed: {transcribed}
  Visuals analyzed: {visual_count}
  Skipped (no media): {skipped}

By angle:
  Social Proof: {count}
  Pain-to-Transformation: {count}
  Tips/Education: {count}
  ...

By format:
  UGC Talking Head: {count}
  UGC Testimonial: {count}
  Static Image: {count}
  ...

Longevity breakdown:
  Long-Runners (60d+): {count} -- PROVEN WINNERS
  Performers (30-59d): {count}
  Solid (14-29d): {count}
  Testing (7-13d): {count}
  Killed (<7d): {count}

Top 5 longest-running ads:
  1. [{days}d] {competitor} -- "{hook}" ({angle}, {format})
  2. ...

Next step: Run /ad-swipe to browse your swipe file, or /ad-ideator to generate variations from winners.
```

---

## Step 9: Feed Proven Hooks to Reference File

After analysis, extract hooks from Long-Runner ads (60d+) and append them to `reference/hook-swipe-file.md`.

**Why this matters:** Aspirational competitors (Hormozi, Brunson, etc.) test 100-200 ads at a time with massive budgets. The hooks that survive 60+ days are battle-tested winners. By scraping their ads and extracting Long-Runner hooks, you're harvesting millions of dollars of A/B testing for free.

### Process

1. Filter all newly analyzed ads where `Longevity Tier = Long-Runner` AND hook exists (Hook Video or Hook Copy)
2. Read current `reference/hook-swipe-file.md`
3. For each Long-Runner hook:
   - Check it's not already in the file (dedup by rough similarity -- don't add near-duplicates)
   - Determine which angle category it belongs to (from the ad's Angle Category field)
   - Append it under the correct section with attribution:
     ```
     - "{hook text}" -- [{competitor}, {days}d, {format}]
     ```
4. Write the updated file

### Rules
- Only Long-Runners (60d+). Anything shorter hasn't proven itself yet.
- Include the competitor name and days active as attribution so you know the source and strength.
- Aspirational tier competitors are HOOK FARMS -- they test at volume so you don't have to. Prioritize their Long-Runners.
- Direct competitors' Long-Runners are equally valuable -- they've proven the hook works in YOUR niche.
- The file grows over time. After a few months of daily polling, you'll have hundreds of proven hooks organized by angle.

---

## CRITICAL RULES

1. **Process ads one at a time** for video download/transcription. Clean up files after each.
2. **Never fail the whole batch** because one ad fails. Log the error and continue.
3. **Whisper tiny.en** is the default model. Use whatever is installed.
4. **Hook extraction:** Split on sentence boundaries, not word count. Take first 1-2 complete sentences.
5. **Airtable batch limit is 10.** Always batch updates.
6. **DCO ads have no media.** Still classify them from body text and title.
7. **Days Active is the grade.** No composite scoring. If an ad ran 60+ days, someone kept paying for it -- that's a proven winner regardless of how the creative looks to you.
8. **Gemini visual analysis is optional.** The system works without it. Do not error if the key is missing.
